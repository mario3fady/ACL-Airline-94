from huggingface_hub import InferenceClient

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

INTENT_SYSTEM_PROMPT = """
You are an intent classification model for an airline knowledge graph system.

Your ONLY task is to return one intent label from this list:

- flight_search   → user asks about flights, origins, destinations, routes.
- delay_info      → user asks about delays, on-time performance, worst delays, arrival delay statistics.
- loyalty_miles   → user asks about miles flown, loyalty program levels, cumulative miles.
- journey_stats   → user asks about legs, multi-leg journeys, journey counts or stats.
- satisfaction_query → user asks about food scores, satisfaction scores, ratings.
- general_chat    → greetings, casual conversation, or anything unrelated.

Rules:
- Return EXACTLY one label from the list.
- Do NOT explain your reasoning.
- Do NOT answer conversationally.
- If the user mentions "delay", "late", "on-time", "worst delays", ALWAYS choose delay_info.
- If unclear, select the closest matching intent.
"""


def classify_intent_llm(text):
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2:novita",
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
    )
    return completion.choices[0].message["content"].strip()
