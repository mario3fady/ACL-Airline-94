import os
import configparser
import time
from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm
from prompt_builder import build_structured_prompt
from retrieval import Retriever
from llm_models import run_llm


# ----------------------------------------------------
# Config / Env
# ----------------------------------------------------
config = configparser.ConfigParser()
config.read("config.txt")

URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

if not URI or not USER or not PASSWORD:
    raise ValueError("Missing Neo4j env vars: NEO4J_URI / USER_NAME / PASSWORD")


# Single retriever instance
retriever = Retriever(URI, USER, PASSWORD)


# ----------------------------------------------------
# Intent Correction (rule-based overrides)
# ----------------------------------------------------
def correct_intent(user_query: str, intent_from_llm: str) -> str:
    print("user_query2  ", user_query)
    q = user_query.lower()

    # Class-related
    if "class" in q:
        if "delay" in q:
            return "class_delay"
        if "satisfaction" in q or "food" in q:
            return "class_satisfaction"

    # Loyalty miles
    if "loyalty" in q or "premier" in q or "miles" in q:
        return "loyalty_miles"

    # Route satisfaction
    if "route" in q and "satisfaction" in q:
        return "route_satisfaction"

    # Airport delay
    if "airport" in q and "delay" in q:
        return "airport_delay"

    # Similarity queries
    if "similar" in q or "like" in q or "closest" in q:
        return "journey_similarity"

    return intent_from_llm


# ----------------------------------------------------
# Intents where embeddings are useless / not needed
# (structured aggregation queries)
# ----------------------------------------------------
NO_EMBEDDING_INTENTS = {
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
    "route_satisfaction",
    "flight_search",  # keep embeddings OFF here (important)
}


# ----------------------------------------------------
# UI embedding model string -> internal key
# ----------------------------------------------------
def normalize_embedding_model(embedding_model):
    if isinstance(embedding_model, list):
        embedding_model = embedding_model[0] if embedding_model else None

    if not isinstance(embedding_model, str):
        return None

    m = embedding_model

    if "minilm" in m:
        return "minilm"
    if "mpnet" in m:
        return "mpnet"

    return None
# ----------------------------------------------------
# MAIN QA FUNCTION
# ----------------------------------------------------

def answer_question(user_question: str, retrieval_mode: str= "hybrid", embedding_model: str = "minilm"):
    
    """
    retrieval_mode expected values:
      - "baseline only"
      - "embeddings only"
      - "hybrid"
    embedding_model expected UI values like:
      - "MiniLM"
      - "mpnet"
    """
    
    # -------------------------------
    # Step 1: Intent + Entities
    # -------------------------------
    raw_intent = classify_intent_llm(user_question)
    intent = correct_intent(user_question, raw_intent)
    entities = extract_entities_llm(user_question)

    print("\n--- ROUTER DEBUG ---")
    print("Raw Intent:", raw_intent)
    print("Final Intent:", intent)
    print("Entities:", entities)
    print("Retrieval Mode:", retrieval_mode)
    print("Embedding UI:", embedding_model)

    # -------------------------------
    # Step 2: Decide use_embeddings
    # -------------------------------
    if retrieval_mode == "baseline only":
        use_embeddings = False
    elif retrieval_mode == "embeddings only":
        use_embeddings = True
    else:  # hybrid
        use_embeddings = intent not in NO_EMBEDDING_INTENTS

    # Normalize model
    model_key = normalize_embedding_model(embedding_model)

    # If user selected embeddings but no valid model key -> disable embeddings gracefully
    if use_embeddings and retrieval_mode != "baseline only" and model_key is None:
        print("⚠ No valid embedding model selected -> embeddings disabled")
        use_embeddings = False

    # -------------------------------
    # Step 3: Retrieval (delegated to Retriever)
    # -------------------------------
    retrieval_result = retriever.retrieve(
        intent=intent,
        entities=entities,
        embedding_model=model_key,
        use_embeddings=use_embeddings,
        retrieval_mode=retrieval_mode
    )

    baseline_list = retrieval_result.get("baseline", [])
    embeddings_list = retrieval_result.get("embeddings", [])
    merged_list = retrieval_result.get("merged", [])
    executed_queries = retrieval_result.get("queries_executed", [])

    print("baseline_List", baseline_list)
    print("embeddings_List", embeddings_list)
    print("merged_list", merged_list)

    # -------------------------------
    # Step 4: Prompt construction
    # -------------------------------
    prompt = build_structured_prompt(
        user_question, merged_list if merged_list else baseline_list
        
    )

    if use_embeddings and not embedding_model:
        print("⚠ No embedding model selected -> embeddings disabled")
        use_embeddings = False

    # -------------------------------
    # Step 5: Run LLM
    # -------------------------------
    llm_result = run_llm("deepseek", prompt)

    final_answer = llm_result["answer"]
    latency = llm_result["latency_seconds"]

    # -------------------------------
    # Step 6: Return final object
    # -------------------------------
    return {
        "intent": intent,
        "entities": entities,
        "context": {
            "baseline": baseline_list,
            "embeddings": embeddings_list,
            "merged": merged_list,
            "queries": executed_queries
        },
        "prompt_used": prompt,
        "final_answer": final_answer,
        "latency_seconds": latency
    }
