import os
from huggingface_hub import InferenceClient

# Load API key from environment variable
HF_TOKEN = os.environ.get("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN environment variable is not set. Please run: setx HF_TOKEN \"your_token_here\"")

# Initialize client
client = InferenceClient(api_key=HF_TOKEN)

INTENT_SYSTEM_PROMPT = """
You are an intent classification model for an airline knowledge graph system.

Your ONLY task is to return one intent label from this list:

- flight_search
- delay_info
- loyalty_miles
- journey_stats
- satisfaction_query
- general_chat

Rules:
- Return EXACTLY one label from the list.
- Do NOT explain your reasoning.
- Do NOT answer conversationally.
- If user mentions 'delay', always choose delay_info.
"""

def classify_intent_llm(text: str) -> str:
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2:novita",
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        max_tokens=5
    )

    return completion.choices[0].message['content'].strip()
