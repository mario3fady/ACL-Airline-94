import numpy as np
from neo4j import GraphDatabase
import os


# ---------------------------------------
# Neo4j Driver Setup
# ---------------------------------------
URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


# ---------------------------------------
# Build a SIMPLE embedding vector from text
# ---------------------------------------
def embed_query(text: str):
    text = text.lower()

    food = 1 if "food" in text or "satisfaction" in text else 0
    delay = 1 if "delay" in text or "late" in text else 0
    miles = 1 if "miles" in text or "distance" in text else 0
    legs = 1 if "legs" in text or "connections" in text else 0

    vec = np.array([food, delay, miles, legs], dtype=float)

    if np.sum(vec) == 0:
        vec = np.array([1.0, 1.0, 1.0, 1.0])

    norm = np.linalg.norm(vec)
    return (vec / norm).tolist()


# ---------------------------------------
# Get similar journeys using Neo4j vector index
# GENERAL – not hardcoded to F_16
# ---------------------------------------
def get_similar_journeys(journey_id: str, top_k: int = 5):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (j:Journey {feedback_ID: $journey_id})
            WHERE j.embedding IS NOT NULL
            WITH j, j.embedding AS e1

            MATCH (other:Journey)
            WHERE other.feedback_ID <> j.feedback_ID
              AND other.embedding IS NOT NULL
            WITH j, e1, other, other.embedding AS e2

            WITH other,
                 reduce(dot = 0.0, i IN range(0, size(e1)-1) |
                    dot + (e1[i] * e2[i])
                 ) AS dot,
                 sqrt(reduce(s = 0.0, x IN e1 | s + x*x)) AS mag1,
                 sqrt(reduce(s = 0.0, x IN e2 | s + x*x)) AS mag2

            WITH other, dot / (mag1 * mag2) AS score
            RETURN 
                other.feedback_ID AS journey,
                other.arrival_delay_minutes AS delay,
                other.food_satisfaction_score AS food,
                score
            ORDER BY score DESC
            LIMIT $top_k
            """,
            journey_id=journey_id,
            top_k=top_k
        )

        return result.data()
