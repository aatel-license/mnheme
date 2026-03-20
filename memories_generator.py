import argparse
import json
import random
from dataclasses import dataclass, asdict
from typing import List, Optional
from openai import OpenAI
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from mnheme import Feeling

# -------- CLI --------
parser = argparse.ArgumentParser()
parser.add_argument("--n", type=int, default=10)
args = parser.parse_args()


# -------- MODEL --------
@dataclass
class Memory:
    concept: str
    feeling: Feeling
    content: str
    media_type: str = "text"
    note: str = ""
    tags: List[str] = None


# -------- LLM --------
class LLMGenerator:
    VALID_FEELINGS = [f.value for f in Feeling]

    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="",
        )
        self.model = ""
        self.API_URL = "http://localhost:8000/memories"

    def post_memory(self, memory: Memory) -> Optional[str]:
        """Posta il ricordo e restituisce l'id assegnato dal server."""
        payload = asdict(memory)
        payload["feeling"] = memory.feeling.value
        response = requests.post(
            self.API_URL,
            headers={"Content-Type": "application/json", "accept": "application/json"},
            json=payload,
            verify=False,
        )
        response.raise_for_status()
        data = response.json()
        # cerca l'id in campi comuni — adatta se la tua API usa un nome diverso
        return data.get("id") or data.get("_id") or data.get("memory_id")

    def generate_all(self, n: int, already_generated: List[Memory]) -> List[Memory]:
        """Chiede all'LLM di generare n ricordi completamente diversi."""
        existing_concepts = [m.concept for m in already_generated]
        existing_feelings = [m.feeling.value for m in already_generated]

        seed = random.randint(0, 10_000_000)
        prompt = f"""
Sei un generatore di ricordi personali umani e realistici.
SEED: {seed}

COMPITO:
Genera esattamente {n} ricordi personali completamente distinti tra loro.

REQUISITI SUL CONCEPT:
- Il campo "concept" deve essere UNA SOLA PAROLA (sostantivo singolo, es: "mutuo", "licenziamento", "tradimento")
- NON usare frasi, NON usare aggettivi, NON usare articoli
- Concetti già usati da non ripetere: {json.dumps(existing_concepts, ensure_ascii=False)}

REQUISITI SUL FEELING:
- Scegli tra questi valori esatti: {json.dumps(self.VALID_FEELINGS, ensure_ascii=False)}
- Feeling già usati (evita se possibile): {json.dumps(existing_feelings, ensure_ascii=False)}

REQUISITI GENERALI:
- Copri ambiti eterogenei: lavoro, famiglia, amicizia, solitudine, corpo, denaro, tempo, ecc.
- Scrivi il content in prima persona, concreto e specifico (1-2 righe max)
- Evita cliché e situazioni generiche

OUTPUT: solo JSON valido, nessun testo extra — un array di {n} oggetti:
[
  {{
    "concept": "parolasingola",
    "feeling": "...",
    "content": "...",
    "media_type": "text",
    "note": "...",
    "tags": [...]
  }}
]
"""
        res = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=1.2,
            top_p=0.95,
        )
        text = res.output[0].content[0].text

        try:
            raw_list = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON non valido nella risposta:\n{text}") from e

        memories = []
        for item in raw_list:
            # forza concept a parola singola — prende solo il primo token
            item["concept"] = item.get("concept", "").split()[0].lower()

            if item.get("feeling") not in self.VALID_FEELINGS:
                item["feeling"] = random.choice(self.VALID_FEELINGS)
            item["feeling"] = Feeling(item["feeling"])
            memories.append(Memory(**item))

        return memories

    def _generate_and_post(self, batch_n: int) -> List[tuple[Memory, Optional[str]]]:
        """Genera un batch e posta ogni ricordo. Restituisce coppie (memory, id)."""
        batch = self.generate_all(batch_n, already_generated=[])
        results = []
        for memory in batch:
            memory_id = self.post_memory(memory)
            print(f"   ✓ [{memory.feeling.value}] {memory.concept} → id: {memory_id or '?'}")
            results.append((memory, memory_id))
        return results

    def generate(self, n: int) -> List[tuple[Memory, Optional[str]]]:
        BATCH_SIZE = 5
        n_batches = (n + BATCH_SIZE - 1) // BATCH_SIZE
        batch_sizes = [BATCH_SIZE] * n_batches
        batch_sizes[-1] = n - BATCH_SIZE * (n_batches - 1)

        all_results: List[tuple[Memory, Optional[str]]] = []

        with ThreadPoolExecutor(max_workers=n_batches) as executor:
            futures = {
                executor.submit(self._generate_and_post, size): size
                for size in batch_sizes
            }
            for future in as_completed(futures):
                try:
                    batch_result = future.result()
                    all_results.extend(batch_result)
                    print(f"   batch completato: {len(batch_result)} ricordi")
                except Exception as e:
                    print(f"   ✗ batch fallito: {e}")

        return all_results[:n]


# -------- MAIN --------
def main():
    gen = LLMGenerator()
    results = gen.generate(args.n)

    print(f"\n--- {len(results)} RICORDI GENERATI E POSTATI ---\n")
    for i, (m, memory_id) in enumerate(results, 1):
        print(f"{i}. [{m.feeling.value}] {m.concept}  (id: {memory_id or '?'})")
        print(f"   {m.content}")
        if m.note:
            print(f"   nota: {m.note}")
        if m.tags:
            print(f"   tag: {', '.join(m.tags)}")
        print()


if __name__ == "__main__":
    main()