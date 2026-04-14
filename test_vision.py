#!/usr/bin/env python3
"""
test_vision.py — testa gemma4-vision su LM Studio
Uso: python test_vision.py immagine.jpg
"""
import base64, json, sys
import urllib.request

IMG  = sys.argv[1] if len(sys.argv) > 1 else "mnheme.jpg"
URL  = "http://localhost:1234/v1/chat/completions"
MODEL = ""

with open(IMG, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({
    "model": MODEL,
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Cosa vedi in questa immagine? Rispondi in italiano."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]
    }],
    "max_tokens": 512
}).encode()

print(f"Invio {IMG} a {URL} ...")

req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.loads(r.read())

print(json.dumps(data, indent=2, ensure_ascii=False))