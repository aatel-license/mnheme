from mnheme import MemoryDB
from llm_provider import LLMProvider
from brain import Brain
import sys
db    = MemoryDB(sys.argv[1] or "mente.mnheme")
llm   = LLMProvider.from_env(".env")
brain = Brain(db, llm)

# 1. Costruisce l'identità stabile
p = brain.persona()
print(p.core_traits)      # ["ipersensibile", "testardo", "ironico"]
print(p.worldview)        # "Il mondo delude, ma vale la pena amarlo lo stesso"
print(p.persona_summary)  # → usabile come system prompt aggiuntivo

# 2. Genera un impulso spontaneo (libero arbitrio)
w = brain.will(persona=p)
print(w.impulse)       # "Voglio smettere di giustificarmi con chiunque"
print(w.impulse_type)  # "ribellione"
print(w.action)        # "Scrivere una lettera che non spedirò mai"
print(w.why)           # motivazione viscerale dai ricordi

# 3. Sceglie tra opzioni come una persona con quella storia
c = brain.choose(
    ["restare", "partire", "aspettare"],
    context="abbandonare la propria citta'",
    persona=p,
)
print(f"c.chosen =>{c.chosen}")           # "partire"
print(f"c.emotional_driver => {c.emotional_driver}") # "paura di stagnare"
print(f"c.certainty => {c.certainty}")        # "riluttante"
print(f"c.reasoning => {c.reasoning}")        # ragionamento interno, non neutro
print(f"c.rejected =>{c.rejected}")           # "partire"
print(f"c.memories_invoked => {c.memories_invoked}")        # "riluttante"
print(f"c.provider_used => {c.provider_used}")        # ragionamento interno, non neutro


