from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm
from retrieval import Retriever
import configparser
from prompt_builder import build_structured_prompt
from llm_models import run_llm
import os


# -----------------------------
# Load Neo4j credentials
# -----------------------------
config = configparser.ConfigParser()
config.read("config.txt")

URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

retriever = Retriever(
    URI,
    USER,
    PASSWORD,
)


# ================================================================
# Helper: override bad LLM intent decisions (high-accuracy rules)
# ================================================================
def correct_intent(user_query, intent_from_llm):

    q = user_query.lower()

    if "class" in q:
        if "delay" in q:
            return "class_delay"
        elif "satisfaction" in q or "food" in q:
            return "class_satisfaction"


    # ----- LOYALTY MILES -----
    if "loyalty" in q or "premier" in q or "miles" in q:
        return "loyalty_miles"

    # ----- ROUTE SATISFACTION -----
    if "route" in q and "satisfaction" in q:
        return "route_satisfaction"

    # ----- AIRPORT DELAY -----
    if "airport" in q and "delay" in q:
        return "airport_delay"
    
    if "similar" in q or "like" in q or "closest" in q:
        return "journey_similarity"
    

    # otherwise keep LLM intent
    return intent_from_llm


# ================================================================
# Helper: disable embeddings for structured logic-only queries
# ================================================================
NO_EMBEDDING_INTENTS = {
    "flight_search",
    "delay_info",
    "satisfaction_query",
    "journey_stats",
    "generation_analysis",
    "class_search",
    "class_delay",
    "class_satisfaction",
    "loyalty_miles",
    "airport_delay",
    "fleet_performance",
    "high_risk_passengers",
    "frequent_flyers",
    "route_satisfaction"
}


# ================================================================
# MAIN QA FUNCTION
# ================================================================
def answer_question(user_query: str, retrieval_mode: str = "hybrid"):
    # 1. Intent classification
    intent_raw = classify_intent_llm(user_query)
    intent = correct_intent(user_query, intent_raw)

    # 2. Entity extraction
    entities = extract_entities_llm(user_query)

    # -----------------------------
    # 3. Retrieval mode handling
    # -----------------------------
    # Determine whether to enable embeddings
    if retrieval_mode == "baseline only":
        use_embeddings = False
    elif retrieval_mode == "embeddings only":
        use_embeddings = True
    else:  # hybrid
        use_embeddings = intent not in NO_EMBEDDING_INTENTS

    # Run the retriever
    context = retriever.retrieve(
        intent=intent,
        entities=entities,
        use_embeddings=use_embeddings,
        retrieval_mode=retrieval_mode  # ← pass to Retriever if you want
    )

    # -----------------------------
    # 4. Build prompt
    # -----------------------------
    prompt = build_structured_prompt(user_query, context)

    # -----------------------------
    # 5. Run LLMs
    # -----------------------------
    model_results = {
        "deepseek": run_llm("deepseek", prompt),
        "gemma": run_llm("gemma", prompt),
        "llama": run_llm("llama", prompt),
    }

    return {
        "intent": intent,
        "entities": entities,
        "context": {
            "baseline": context.get("baseline", []),
            "embeddings": context.get("embeddings", []),
            "merged": context.get("merged", []),
            "queries": context.get("queries_executed", [])
        },
        "prompt_used": prompt,
        "model_comparison": model_results
    }
