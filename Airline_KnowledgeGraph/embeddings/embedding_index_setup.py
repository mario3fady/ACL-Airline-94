import os
from neo4j import GraphDatabase


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


def create_journey_embedding_indexes():
    """
    Create **two** Neo4j vector indexes on Journey embeddings:

    1) journey_embedding_index_model1
         - property: embedding_model1
         - dimension: 2
         - similarity: cosine
         - Meaning: [delay, miles]  (operational intensity)

    2) journey_embedding_index_model2
         - property: embedding_model2
         - dimension: 2
         - similarity: cosine
         - Meaning: [legs, food]    (complexity & experience)
    """

    uri, user, password = load_config()
    driver = GraphDatabase.driver(uri, auth=(user, password))

    index_configs = [
        ("journey_embedding_index_model1", "embedding_model1", 2),
        ("journey_embedding_index_model2", "embedding_model2", 2),
    ]

    check_query = """
    SHOW INDEXES
    YIELD name, type, entityType, labelsOrTypes, properties
    WHERE name = $name
    RETURN name
    """

    create_query = """
    CALL db.index.vector.createNodeIndex(
        $name,
        'Journey',
        $property,
        $dimension,
        'cosine'
    )
    """

    with driver.session() as session:
        for index_name, prop, dim in index_configs:
            existing = session.run(check_query, name=index_name).single()

            if existing:
                print(f"ℹ️ Vector index '{index_name}' already exists.")
            else:
                session.run(
                    create_query,
                    name=index_name,
                    property=prop,
                    dimension=dim,
                )
                print(
                    f"✅ Created vector index '{index_name}' "
                    f"on Journey.{prop} (dim={dim})."
                )

    driver.close()


if __name__ == "__main__":
    create_journey_embedding_indexes()
