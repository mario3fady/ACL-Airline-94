from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm
from retrieval import Retriever, format_kg_result
import configparser

config = configparser.ConfigParser()
config.read("config.txt")

retriever = Retriever(
    config["DEFAULT"]["URI"],
    config["DEFAULT"]["USERNAME"],
    config["DEFAULT"]["PASSWORD"],
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

    # 4. Execute Neo4j query → raw records (list of dict)
    kg_records = retriever.run_query(query_key, params)

    # 5. Build human-readable answer text
    answer_text = format_kg_result(intent, kg_records)

    return {
        "intent": intent,
        "entities": entities,
        "query_key": query_key,
        "params": params,
        "kg_result": kg_records,   # raw data
        "answer_text": answer_text # pretty text
    }
