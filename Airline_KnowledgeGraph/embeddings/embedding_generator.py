from neo4j import GraphDatabase
import numpy as np
import os


def load_variables():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("USER_NAME")
    password = os.environ.get("PASSWORD")
    return uri, user, password


def l2_normalize(vec: np.ndarray) -> np.ndarray:
    """L2-normalize a 1D numpy vector. If norm=0, return as-is."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def generate_journey_embeddings():
    """
    For each Journey node, build **two** separate numerical feature embeddings
    (we intentionally remove the original 4D combined embedding).

    Embedding Model 1 (2D) – Operational Intensity:
        embedding_model1 = [arrival_delay_minutes, actual_flown_miles]

    Embedding Model 2 (2D) – Journey Complexity & Experience:
        embedding_model2 = [number_of_legs, food_satisfaction_score]

    All vectors are L2-normalized before being stored on the Journey node.
    """

    uri, user, password = load_variables()
    if not uri or not user or not password:
        raise ValueError(
            "Missing one or more Neo4j environment variables: "
            "NEO4J_URI, USER_NAME, PASSWORD"
        )

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Fetch the raw numeric features from each Journey node
    query = """
    MATCH (j:Journey)
    RETURN
        j.feedback_ID              AS id,
        coalesce(j.arrival_delay_minutes,   0.0) AS delay,
        coalesce(j.actual_flown_miles,      0.0) AS miles,
        coalesce(j.number_of_legs,          0.0) AS legs,
        coalesce(j.food_satisfaction_score, 0.0) AS food
    """

    # Update the embeddings on the Journey node
    update_query = """
    MATCH (j:Journey {feedback_ID: $id})
    SET
        j.embedding_model1 = $embedding_model1,
        j.embedding_model2 = $embedding_model2
    """

    with driver.session() as session:
        results = session.run(query)

        count = 0
        for record in results:
            delay = float(record["delay"])
            miles = float(record["miles"])
            legs  = float(record["legs"])
            food  = float(record["food"])

            # 2D Model 1: [delay, miles]
            vec_model1 = np.array([delay, miles], dtype=float)
            vec_model1 = l2_normalize(vec_model1)

            # 2D Model 2: [legs, food]
            vec_model2 = np.array([legs, food], dtype=float)
            vec_model2 = l2_normalize(vec_model2)

            session.run(
                update_query,
                id=record["id"],
                embedding_model1=vec_model1.tolist(),
                embedding_model2=vec_model2.tolist(),
            )
            count += 1

        print(f"✅ Generated 2D embeddings (model1 & model2) for {count} Journey nodes.")

    driver.close()


if __name__ == "__main__":
    generate_journey_embeddings()
