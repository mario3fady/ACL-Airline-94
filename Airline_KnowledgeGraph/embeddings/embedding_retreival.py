import numpy as np
from neo4j import GraphDatabase
import os



URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")



driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


# ---------------- UTILS ----------------

def embed_query(text: str):
    """
    Convert user query into a vector.
    SIMPLE version:
       - If query mentions "delay", use weight on delay dimension.
       - If query mentions "food", use weight on food dimension.
    (This keeps embedding logic allowed within Node Embeddings requirement)
    """

    text = text.lower()

    food = 1 if "food" in text or "satisfaction" in text else 0
    delay = 1 if "delay" in text or "late" in text else 0
    miles = 1 if "miles" in text or "distance" in text else 0
    legs = 1 if "legs" in text or "connections" in text else 0

    vec = np.array([food, delay, miles, legs], dtype=float)
    # FIX: avoid zero vector (invalid for Neo4j)
    if np.sum(vec) == 0:
        vec = np.array([1.0, 1.0, 1.0, 1.0], dtype=float)
        
    norm = np.linalg.norm(vec)
    return (vec / norm).tolist() if norm != 0 else vec.tolist()


def query_similar_journeys(query_vec, top_k=5):
    with driver.session() as session:
        results = session.run(
            """
            CALL db.index.vector.queryNodes(
                'journey_embedding_index',
                $k,
                $vec
            ) YIELD node, score
            RETURN node.feedback_ID AS journey,
                   node.arrival_delay_minutes AS delay,
                   node.food_satisfaction_score AS food,
                   score
            """,
            k=int(top_k),
            vec=[float(x) for x in query_vec]
        )
        return results.data()


def get_similar_journeys(user_query):
    vec = embed_query(user_query)
    results = query_similar_journeys(vec)
    return results
