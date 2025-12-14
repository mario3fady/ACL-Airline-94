from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import os

# ----------------------------------
# CONFIG
# ----------------------------------
URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

MODELS = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "mpnet": "sentence-transformers/all-mpnet-base-v2"
}

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def build_journey_text(record):
    return (
        f"Journey {record['id']} with food satisfaction {record['food']}, "
        f"arrival delay {record['delay']} minutes, "
        f"distance {record['miles']} miles, "
        f"number of legs {record['legs']}, "
        f"class {record['cls']}"
    )


def generate_embeddings():
    query = """
    MATCH (j:Journey)
    RETURN
        j.feedback_ID AS id,
        coalesce(j.food_satisfaction_score, 0) AS food,
        coalesce(j.arrival_delay_minutes, 0) AS delay,
        coalesce(j.actual_flown_miles, 0) AS miles,
        coalesce(j.number_of_legs, 0) AS legs,
        coalesce(j.passenger_class, 'Economy') AS cls
    """

    # Update the embeddings on the Journey node
    update_query = """
    MATCH (j:Journey {{feedback_ID: $id}})
    SET j.embedding_{model} = $embedding
    """

    with driver.session() as session:
        rows = session.run(query).data()

        for model_key, model_name in MODELS.items():
            print(f"🔹 Loading {model_name}")
            model = SentenceTransformer(model_name)

            for r in rows:
                text = build_journey_text(r)
                emb = model.encode(text, normalize_embeddings=True).tolist()

                session.run(
                    update_query.format(model=model_key),
                    id=r["id"],
                    embedding=emb
                )

        print("✅ Embeddings generated for both models")


if __name__ == "__main__":
    generate_embeddings()
