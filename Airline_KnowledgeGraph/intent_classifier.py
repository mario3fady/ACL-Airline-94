import json
import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN not set.")

MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"  # <--- FIXED MODEL

client = InferenceClient(api_key=HF_TOKEN)

INTENT_SYSTEM_PROMPT = """
You are an Intent Classification Model for an Airline Knowledge Graph System.

Your task is to read the user's natural-language query and classify it into EXACTLY ONE intent label from the list below:

INTENT LABELS:
- flight_search        → questions about routes, flights, origins, destinations.
- delay_info           → questions about delays, lateness, cancellations, on-time performance.
- loyalty_miles        → questions about miles flown, loyalty levels, total distance, passenger mileage.
- journey_stats        → questions about number of legs, multi-leg trips, journey summaries.
- satisfaction_query   → questions about food scores, satisfaction ratings, overall scores.
- general_chat         → greetings, chit-chat, unrelated conversation.

REQUIREMENTS:
- Output ONLY the label text (e.g., "flight_search").
- Do NOT explain.
- Do NOT output extra words.
- If multiple intents appear, choose the PRIMARY one.
- If the query includes the word "delay", ALWAYS classify as delay_info.
- If the query is unclear, choose general_chat.

EXAMPLES:
USER: "Show me flights from LAX to IAX"  
OUTPUT: flight_search

USER: "Which flights arrive late most often?"  
OUTPUT: delay_info

USER: "How many miles did premier silver members earn?"  
OUTPUT: loyalty_miles

USER: "How many legs did my journey have?"  
OUTPUT: journey_stats

USER: "What is my satisfaction score?"  
OUTPUT: satisfaction_query

USER: "Hi, how are you?"  
OUTPUT: general_chat

Return ONLY the label, nothing else.

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
