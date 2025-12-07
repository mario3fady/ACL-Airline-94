import os
from huggingface_hub import InferenceClient

# Load API key from environment variable
HF_TOKEN = os.environ.get("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN environment variable is not set. Please run: setx HF_TOKEN \"your_token_here\"")

# Initialize client
client = InferenceClient(api_key=HF_TOKEN)

ENTITY_SYSTEM_PROMPT = """
You are an entity extraction model for an airline knowledge graph.

Your ONLY job is to return a VALID JSON dictionary.
Do NOT output text before or after the JSON.

Extract:

{
  "flights": [...],
  "airports": [...],
  "passengers": [...],
  "journeys": [...],
  "routes": {
       "origin": "...",
       "destination": "..."
  }
}

Rules:
- Return ONLY valid JSON.
- No explanations.
- No comments.
- No markdown formatting.
"""
def extract_entities_llm(text):
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2:novita",
        messages=[
            {"role": "system", "content": ENTITY_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
    )

    raw = completion.choices[0].message["content"].strip()
    print("Raw LLM Output:", raw)

    try:
        return json.loads(raw)
    except:
        print("Failed to parse JSON. Returning fallback schema.")
        return {
            "flights": [],
            "airports": [],
            "passengers": [],
            "journeys": [],
            "routes": {"origin": None, "destination": None}
        }