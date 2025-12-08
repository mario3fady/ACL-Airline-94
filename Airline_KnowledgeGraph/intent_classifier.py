import json
import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN not set.")

MODEL_NAME = "google/gemma-2-2b-it"  # <--- FIXED MODEL

client = InferenceClient(api_key=HF_TOKEN)

INTENT_SYSTEM_PROMPT = """
You are an intent classifier for an airline knowledge graph.
Return EXACTLY ONE label:

- flight_search
- delay_info
- loyalty_miles
- journey_stats
- satisfaction_query
- general_chat
"""

def classify_intent_llm(text):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message["content"].strip()
