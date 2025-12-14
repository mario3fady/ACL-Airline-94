import os
from neo4j import GraphDatabase


def load_config():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("USER_NAME")
    password = os.environ.get("PASSWORD")

    # Safety checks
    missing = []
    if uri is None: missing.append("NEO4J_URI")
    if user is None: missing.append("USER_NAME")
    if password is None: missing.append("PASSWORD")

    if missing:
        raise ValueError(f"❌ Missing environment variable(s): {', '.join(missing)}")

    return uri, user, password


def create_journey_embedding_index():
    """
    Create a Neo4j vector index on Journey.embedding with dimension 4 and cosine similarity.
    If it already exists, log and do nothing.
    """
    uri, user, password = load_config()
    driver = GraphDatabase.driver(uri, auth=(user, password))

    index_name = "journey_embedding_index"

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
        'embedding',
        4,
        'cosine'
    )
    """

    with driver.session() as session:
        existing = session.run(check_query, name=index_name).single()

        if existing:
            print(f"ℹ️ Vector index '{index_name}' already exists.")
        else:
            session.run(create_query, name=index_name)
            print(f"✅ Created vector index '{index_name}' on Journey.embedding.")

    driver.close()


if __name__ == "__main__":
    create_journey_embedding_index()
