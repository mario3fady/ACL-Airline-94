import os
import re
from huggingface_hub import InferenceClient

# ------------------------------------------------------------------
# Environment & Model Setup
# ------------------------------------------------------------------

HF_TOKEN = os.environ.get("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN not set.")

MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
client = InferenceClient(api_key=HF_TOKEN)

# ------------------------------------------------------------------
# System Prompt for Intent Classification
# ------------------------------------------------------------------

INTENT_SYSTEM_PROMPT = """
You are an Intent Classification Model for an Airline Knowledge Graph System.

Your task is to read the user's natural-language query and classify it into
EXACTLY ONE intent label from the list below.

INTENT LABELS:

- flight_search
  → routes, origins, destinations, specific flights

- delay_info
  → delays, lateness, worst flights, late arrivals

- airport_delay
  → delays by airport or station

- generation_analysis
  → comparisons by passenger generation

- route_satisfaction
  → best or worst routes by satisfaction or experience

- class_delay
  → delays by passenger class

- class_satisfaction
  → satisfaction by passenger class

- fleet_performance
  → aircraft, fleet, or plane type comparisons

- high_risk_passengers
  → unhappy passengers, churn risk, bad experience patterns

- frequent_flyers
  → most frequent travelers or most journeys

- loyalty_miles
  → miles flown, loyalty level analysis

- journey_stats
  → journey counts, number of legs, summaries

- satisfaction_query
  → food or service satisfaction scores

- general_chat
  → greetings or unrelated conversation

NOTE:
- Queries like "show journeys for passenger ABXX7J" are handled by a rule-based
  shortcut as intent = passenger_journey, even though that label is not in this list.

CLASSIFICATION RULES:

1. Output EXACTLY ONE label, no extra text.
2. If the word "delay" appears:
   - Choose the MOST SPECIFIC delay intent available.
3. If the query mentions an airport explicitly with delay:
   - Use airport_delay.
4. If the query mentions passenger class with delay:
   - Use class_delay.
5. If the query is unclear or unrelated:
   - Use general_chat.
6. If multiple intents appear:
   - Choose the PRIMARY one.

EXAMPLES:

USER: "Show me flights from LAX to IAX"
OUTPUT: flight_search

USER: "Which airport has the worst delays?"
OUTPUT: airport_delay

USER: "Which class is delayed the most?"
OUTPUT: class_delay

USER: "Which aircraft performs best?"
OUTPUT: fleet_performance

USER: "Who are the most frequent travelers?"
OUTPUT: frequent_flyers

USER: "How satisfied are economy passengers?"
OUTPUT: class_satisfaction

USER: "Hello"
OUTPUT: general_chat

Return ONLY the intent label. Do NOT explain.
"""

# ------------------------------------------------------------------
# Intent Classification Function
# ------------------------------------------------------------------

def classify_intent_llm(text: str) -> str:
    """
    Classifies user query into exactly one intent label using:
    1. Rule-based shortcuts (for accuracy and control)
    2. LLM classification (fallback for all other cases)
    """
    txt = text.lower()

    # 1) PASSENGER JOURNEY SHORTCUT (record locator + 'passenger')
    record_locator_match = re.search(r"\b[A-Z0-9]{5,8}\b", text)
    if record_locator_match and "passenger" in txt:
        return "passenger_journey"

    # 2) GENERATION ANALYSIS SHORTCUT
    generation_keywords = [
        "generation", "generational", "gen z", "millennial",
        "baby boomer", "older", "younger", "age group",
        "compare generations", "age comparison"
    ]
    if any(word in txt for word in generation_keywords):
        return "generation_analysis"

    # 3) FALLBACK LLM CLASSIFICATION
    response = client.chat_completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    ) if hasattr(client, "chat_completions") else client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message["content"].strip()
