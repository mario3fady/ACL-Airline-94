import os
from neo4j import GraphDatabase

# ---------------------------------------------------
#  Helper: load Neo4j credentials
# ---------------------------------------------------
def load_config():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("USER_NAME")
    password = os.environ.get("PASSWORD")

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


# ---------------------------------------------------
#  Journey Similarity using embeddings
# ---------------------------------------------------
def get_similar_journeys(journey_id: str, top_k: int = 5, model: str = "model1"):
    """
    Given a Journey ID (feedback_ID), find the top_k most similar journeys
    using cosine similarity over the selected **2D** embedding model.

    Parameters
    ----------
    journey_id : str
        feedback_ID of the anchor Journey (e.g., "F_16").
    top_k : int
        Number of similar journeys to return.
    model : {"model1", "model2"}
        Which embedding model to use:

          - "model1" → Journey.embedding_model1
                       (2D: [delay, miles] – operational intensity)

          - "model2" → Journey.embedding_model2
                       (2D: [legs, food] – journey complexity & experience)
    """

    if model not in {"model1", "model2"}:
        raise ValueError("model must be 'model1' or 'model2'")

    embedding_prop = "embedding_model1" if model == "model1" else "embedding_model2"

    uri, user, password = load_config()
    driver = GraphDatabase.driver(uri, auth=(user, password))

    # We compute cosine similarity directly in Cypher on the list properties.
    query = f"""
    MATCH (j:Journey {{feedback_ID: $journey_id}})
    WHERE j.{embedding_prop} IS NOT NULL
    WITH j, j.{embedding_prop} AS e1

    MATCH (other:Journey)
    WHERE other.feedback_ID <> j.feedback_ID
      AND other.{embedding_prop} IS NOT NULL
    WITH j, e1, other, other.{embedding_prop} AS e2

    // Compute cosine similarity between e1 and e2
    WITH j, other, e1, e2,
         reduce(dot = 0.0, i IN range(0, size(e1)-1) | dot + e1[i] * e2[i]) AS dot,
         sqrt(reduce(n1 = 0.0, i IN range(0, size(e1)-1) | n1 + e1[i] * e1[i])) AS norm1,
         sqrt(reduce(n2 = 0.0, i IN range(0, size(e2)-1) | n2 + e2[i] * e2[i])) AS norm2
    WITH j, other,
         CASE
             WHEN norm1 = 0 OR norm2 = 0 THEN 0.0
             ELSE dot / (norm1 * norm2)
         END AS cosineSim
    ORDER BY cosineSim DESC
    LIMIT $top_k

    RETURN
        other.feedback_ID             AS journey_id,
        cosineSim                     AS score,
        other.food_satisfaction_score AS food,
        other.arrival_delay_minutes   AS delay,
        other.actual_flown_miles      AS miles,
        other.number_of_legs          AS legs
    """

    rows = []
    try:
        with driver.session() as session:
            result = session.run(query, journey_id=journey_id, top_k=top_k)
            for record in result:
                row = record.data()
                row["embedding_model_used"] = model
                rows.append(row)
    finally:
        driver.close()

    return rows


if __name__ == "__main__":
    # Quick manual test example (use a valid feedback_ID from your KG):
    test_id = "F_1"
    print("Top 5 similar journeys (Model 1 - delay + miles):")
    for r in get_similar_journeys(test_id, top_k=5, model="model1"):
        print(r)

    print("\nTop 5 similar journeys (Model 2 - legs + food):")
    for r in get_similar_journeys(test_id, top_k=5, model="model2"):
        print(r)
