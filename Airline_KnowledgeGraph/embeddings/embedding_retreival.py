from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import os

URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")
print("🔥 LOADED NEW embedding_retreival.py")

MODELS = {
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", "journey_minilm_index"),
    "mpnet": ("sentence-transformers/all-mpnet-base-v2", "journey_mpnet_index")
}

    missing = []
    if uri is None:
        missing.append("NEO4J_URI")
    if user is None:
        missing.append("USER_NAME")
    if password is None:
        missing.append("PASSWORD")

    if missing:
        raise ValueError(f"❌ Missing environment variable(s): {', '.join(missing)}")

    return uri, user, password


def get_similar_journeys(query_text, model_key="minilm", top_k=5):
    model_name, index_name = MODELS[model_key]
    model = SentenceTransformer(model_name)

    query_embedding = model.encode(
        query_text,
        normalize_embeddings=True
    ).tolist()

    with driver.session() as session:
        result = session.run("""
        CALL db.index.vector.queryNodes($index, $k, $embedding)
        YIELD node, score
        RETURN
            node.feedback_ID AS journey,
            node.arrival_delay_minutes AS delay,
            node.food_satisfaction_score AS food,
            score
        ORDER BY score DESC
        """, index=index_name, k=top_k, embedding=query_embedding)

        return result.data()
