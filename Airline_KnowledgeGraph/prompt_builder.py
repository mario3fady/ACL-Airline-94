import json

def format_context_for_prompt(context):
    """
    Convert the merged KG results into clean JSON for the LLM.
    This ensures the LLM can reliably interpret the data structure.
    """
    merged = context.get("merged", [])

    if not merged:
        return "[]"

    return json.dumps(merged, indent=2, ensure_ascii=False)


def build_structured_prompt(user_query, context):
    """
    Strong, safe, detailed RAG prompt that forces the LLM to:
    - Interpret journey rows correctly
    - Interpret aggregated rows correctly
    - Ignore embedding rows unless relevant
    - NEVER hallucinate missing classes, flights, or data
    - Always compute averages, totals, comparisons manually
    """

    context_text = format_context_for_prompt(context)

    return f"""
You are an Airline Knowledge Graph Analytics Assistant.
You answer using ONLY the JSON data provided below.

==============================
[KG_DATA]
{context_text}
==============================

==============================
DATA DEFINITIONS — READ CAREFULLY:
A Journey row (single passenger on a flight) typically contains:
- journey or feedback_ID → unique journey identifier  
- flight → flight_number  
- origin, destination → airport codes  
- delay or arrival_delay_minutes → minutes delayed (negative = early)  
- food or food_satisfaction_score → 1 to 5  
- passenger_class → Economy, Business, etc.  
- generation → Gen X, Millennial, etc.  
- loyalty_level or loyalty_program_level → bronze/silver/gold/1k levels  
- actual_flown_miles → miles for that journey  
- fleet → aircraft type  

Aggregated rows (from Neo4j queries such as class_delay, journey_stats, fleet_performance) contain:
- avg_delay  
- avg_food  
- journey_count  
- fleet or passenger_class or generation  

Embedding rows (from semantic search) contain ONLY:
- journey, delay, food, score  
If a row has ONLY these 4 fields → it is NOT real KG data and MUST be ignored unless the question explicitly asks for similarity.

==============================
RULES FOR ANSWERING:
1. Use ONLY the JSON rows in [KG_DATA]. Never invent information.
2. If multiple row types exist (journey, aggregated, embedding), choose the one relevant to the question.
3. If the question asks “best”, “worst”, “most”, “least”, you MUST compute rankings manually.
4. If the question asks per class/generation/loyalty/fleet, you MUST aggregate rows manually.
5. If data is missing (e.g., no Business class shown), explicitly say it is not in the dataset.
6. Never confuse:
   - journey rows  
   - flight-level aggregates  
   - class-level aggregates  
   - embedding similarity rows  
7. If a row contains a score but no flight/class data → ignore it for operational analysis.
8. The final answer must be factual, concise, and grounded ONLY in the dataset.

==============================
USER QUESTION:
{user_query}

==============================
YOUR ANSWER (follow the rules above):
"""
