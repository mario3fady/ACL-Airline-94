import os, json, re
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN is not set.")

MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"  # <--- FIXED MODEL

client = InferenceClient(api_key=HF_TOKEN)

ENTITY_SYSTEM_PROMPT = """
You are an Airline Entity Extraction Model for a Knowledge Graph System.

Your task is to extract ALL relevant airline-related entities from the user's query and return them in STRICT VALID JSON ONLY.

JSON FORMAT TO RETURN (NO OTHER TEXT):

{
  "flights": [],       // flight numbers only, e.g., ["42", "966"]
  "airports": [],      // list of any airport codes mentioned, e.g., ["LAX", "IAX"]
  "passengers": [],    // loyalty levels, passenger groups, or record locators (e.g., ["Premier Silver", "BNXX5R"])
  "journeys": [],      // journey identifiers or leg counts if mentioned
  "routes": {
      "origin": "",     // single airport code or empty string
      "destination": "" // single airport code or empty string
  }
}

RULES:
- Return ONLY valid JSON. NO markdown, NO backticks, NO explanation.
- Airport codes are ALWAYS 3–letter uppercase codes (e.g., "LAX").
- Extract flight numbers even if written as "flight 42".
- Record locators are 5–8 uppercase alphanumeric tokens (e.g., "BNXX5R").
- If multiple routes appear, choose the PRIMARY one.
- If no entity is found, return empty lists or empty strings.
- Preserve order of mentions where possible.
- Never invent entities that are not stated.

EXAMPLES:

USER: "Show me flights from LAX to IAX"
RETURN:
{
  "flights": [],
  "airports": ["LAX", "IAX"],
  "passengers": [],
  "journeys": [],
  "routes": {"origin": "LAX", "destination": "IAX"}
}

USER: "Why was flight 57 delayed?"
RETURN:
{
  "flights": ["57"],
  "airports": [],
  "passengers": [],
  "journeys": [],
  "routes": {"origin": "", "destination": ""}
}

USER: "Show multi-leg journeys from DEX to IAX"
RETURN:
{
  "flights": [],
  "airports": ["DEX", "IAX"],
  "passengers": [],
  "journeys": ["multi-leg"],
  "routes": {"origin": "DEX", "destination": "IAX"}
}

USER: "Show me journeys for passenger BNXX5R"
RETURN:
{
  "flights": [],
  "airports": [],
  "passengers": ["BNXX5R"],
  "journeys": [],
  "routes": {"origin": "", "destination": ""}
}

RETURN ONLY JSON. No prose.
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
        parsed = json.loads(cleaned)
    except:
        print("⚠ JSON parse failed. Fallback used.")
        parsed = {
            "flights": [],
            "airports": [],
            "passengers": [],
            "journeys": [],
            "routes": {"origin": "", "destination": ""}
        }

    # --------- EXTRA HARDENING: inject record locators into `passengers` ---------
    # Record locators: 5–8 uppercase alphanumeric tokens (e.g. "BNXX5R")
    record_locator_pattern = r"\b[A-Z0-9]{5,8}\b"
    locs = re.findall(record_locator_pattern, question)

    # Remove airport-like 3-letter codes and very short tokens
    locs = [l for l in locs if len(l) >= 5]

    # Make sure the key exists and is a list
    if "passengers" not in parsed or not isinstance(parsed["passengers"], list):
        parsed["passengers"] = []

    # Add record locators without duplicating existing passenger tokens
    for loc in locs:
        if loc not in parsed["passengers"]:
            parsed["passengers"].append(loc)

    return parsed
