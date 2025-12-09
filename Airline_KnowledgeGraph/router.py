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

    # 3. Hybrid KG Retrieval (baseline + embeddings)
    context = retriever.retrieve(intent, entities, use_embeddings=True)

    print("\n--- HYBRID CONTEXT ---")
    print(context)

    return context