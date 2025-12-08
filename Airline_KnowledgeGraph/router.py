from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm
from retrieval import Retriever
import configparser
from retrieval import format_kg_result
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

def answer_question(user_query: str):
    # 1. Intent classification
    intent = classify_intent_llm(user_query)
    print("\n--- INTENT ---")
    print(intent)

    # 2. Entity extraction
    entities = extract_entities_llm(user_query)
    print("\n--- ENTITIES ---")
    print(entities)

    # 3. Route to correct query + parameters
    query_key, params = retriever.route(intent, entities)

    print("\n--- ROUTER DECISION ---")
    print("Selected Query:", query_key)
    print("Parameters:", params)

    if query_key is None:
        return {
            "intent": intent,
            "entities": entities,
            "error": "I could not determine the correct KG query for your request.",
        }

    # 4. Execute query
    kg_result = retriever.run_query(query_key, params)

    # 5. Return a structured response (you can format this however you like)
    formatted = format_kg_result(intent, kg_result)
    return {
    "intent": intent,
    "entities": entities,
    "query_key": query_key,
    "params": params,
    "kg_result": kg_result,      # still include raw data for debugging
    "answer_text": formatted     # final pretty text
}
