from neo4j import GraphDatabase
import numpy as np
import os


def load_variables():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("USER_NAME")
    password = os.environ.get("PASSWORD")
    print(uri)
    return uri, user, password


def l2_normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def generate_journey_embeddings():
    """
    For each Journey node, build a numerical feature vector based on journey metrics:
      [food_satisfaction_score, arrival_delay_minutes, actual_flown_miles, number_of_legs]
    Then L2-normalize it and store it in j.embedding (as a list of floats).
    """
    uri, user, password = load_variables()
    driver = GraphDatabase.driver(uri, auth=(user, password))

    query = """
    MATCH (j:Journey)
    RETURN
        j.feedback_ID              AS id,
        coalesce(j.food_satisfaction_score, 0.0) AS food,
        coalesce(j.arrival_delay_minutes,   0.0) AS delay,
        coalesce(j.actual_flown_miles,      0.0) AS miles,
        coalesce(j.number_of_legs,          0.0) AS legs
    """

    update_query = """
    MATCH (j:Journey {feedback_ID: $id})
    SET j.embedding = $embedding
    """

    with driver.session() as session:
        results = session.run(query)

        count = 0
        for record in results:
            food = float(record["food"])
            delay = float(record["delay"])
            miles = float(record["miles"])
            legs = float(record["legs"])

            vec = np.array([food, delay, miles, legs], dtype=float)
            vec = l2_normalize(vec)

            session.run(
                update_query,
                id=record["id"],
                embedding=vec.tolist()
            )
            count += 1

        print(f"✅ Generated embeddings for {count} Journey nodes.")

    driver.close()


if __name__ == "__main__":
    generate_journey_embeddings()
