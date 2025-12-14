from neo4j import GraphDatabase
import os

URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

INDEXES = {
    "journey_minilm_index": "embedding_minilm",
    "journey_mpnet_index": "embedding_mpnet"
}

DIMENSIONS = {
    "embedding_minilm": 384,
    "embedding_mpnet": 768
}

def create_indexes():
    with driver.session() as session:
        for index_name, prop in INDEXES.items():
            session.run(f"""
            CALL db.index.vector.createNodeIndex(
                '{index_name}',
                'Journey',
                '{prop}',
                {DIMENSIONS[prop]},
                'cosine'
            )
            """)

            print(f"✅ Created index {index_name}")

if __name__ == "__main__":
    create_indexes()
