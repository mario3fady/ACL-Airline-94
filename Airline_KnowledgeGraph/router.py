from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm
from retrieval import Retriever
import configparser


# -----------------------------
# Load Neo4j credentials
# -----------------------------
config = configparser.ConfigParser()
config.read("config.txt")

retriever = Retriever(
    config["DEFAULT"]["URI"],
    config["DEFAULT"]["USERNAME"],
    config["DEFAULT"]["PASSWORD"],
)


# -----------------------------
# Main QA Pipeline
# -----------------------------
def answer_question(question):

    # 1. Intent classification
    intent = classify_intent_llm(question)

    # 2. Entity extraction
    entities = extract_entities_llm(question)

    print("Intent:", intent)
    print("Entities:", entities)

    # 3. Routing → Select Cypher Query + Parameters
    query_key, params = retriever.route(intent, entities)

    print("Selected Query:", query_key)
    print("Parameters:", params)

    # --- Handle missing query (e.g., no origin/destination provided) ---
    if query_key is None:
        return {"error": "I could not determine the correct query for your request."}

    # 4. Execute query
    result = retriever.run_query(query_key, params)

    # 5. Return KG result
    return result
