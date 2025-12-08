import os, json, re
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN is not set.")

MODEL_NAME = "google/gemma-2-2b-it"  # <--- FIXED MODEL

client = InferenceClient(api_key=HF_TOKEN)

ENTITY_SYSTEM_PROMPT = """
Extract airline entities and return STRICT valid JSON:

{
  "flights": [...],
  "airports": [...],
  "passengers": [...],
  "journeys": [...],
  "routes": {
      "origin": "",
      "destination": ""
  }
}

Rules:
- Return ONLY JSON. No markdown.
- Missing items must be empty lists or empty strings.
"""

def clean_json(text):
    text = text.strip()
    text = re.sub(r"^```json|```$", "", text).strip()
    return text

def extract_entities_llm(question):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": ENTITY_SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
    )

    raw = response.choices[0].message["content"].strip()
    cleaned = clean_json(raw)

    try:
        return json.loads(cleaned)
    except:
        print("⚠ JSON parse failed. Fallback used.")
        return {
            "flights": [],
            "airports": [],
            "passengers": [],
            "journeys": [],
            "routes": {"origin": "", "destination": ""}
        }
