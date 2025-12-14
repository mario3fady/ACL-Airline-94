from neo4j import GraphDatabase
from queries import QUERIES
from embeddings.embedding_retreival import get_similar_journeys


# ====================================================
#                RESULT MERGING
# ====================================================
def merge_results(baseline_list, embedding_list, key_candidates=None):
    """
    Merge baseline KG rows with embedding similarity rows.
    Embedding score is preserved and used for ranking.
    """

    baseline_list = baseline_list or []
    embedding_list = embedding_list or []

    if key_candidates is None:
        key_candidates = ["journey", "journey_id", "flight"]

    def get_key(row):
        for k in key_candidates:
            if k in row and row[k] is not None:
                return row[k]
        return id(row)

    merged = {}

    # Add baseline rows first
    for row in baseline_list:
        row = dict(row)
        key = get_key(row)
        row["score"] = None
        merged[key] = row

    # Merge embedding rows
    for row in embedding_list:
        row = dict(row)
        key = get_key(row)

        if key not in merged:
            merged[key] = row
        else:
            # Preserve embedding score
            if row.get("score") is not None:
                merged[key]["score"] = row["score"]

            # Fill missing fields
            for k, v in row.items():
                if merged[key].get(k) is None:
                    merged[key][k] = v

    merged_list = list(merged.values())

    # Sort: embedding hits first
    merged_list.sort(
        key=lambda x: (x["score"] is None, x["score"] if x["score"] is not None else float("inf"))
    )

    return merged_list


# ====================================================
#                RETRIEVER CLASS
# ====================================================
class Retriever:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ------------------------------------------------
    #               CYPHER EXECUTION
    # ------------------------------------------------
    def run_query(self, query_key, params=None):
        query = QUERIES.get(query_key)
        if not query:
            return []

        params = params or {}

        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return [r.data() for r in result]
        except Exception as e:
            print("Cypher error:", e)
            return []

    # ------------------------------------------------
    #           EMBEDDING RETRIEVAL
    # ------------------------------------------------
    def run_embedding_query(self, intent, params, embedding_model):
        """
        Embedding retrieval is ONLY used for journey similarity.
        """

        if intent != "journey_similarity":
            return []

        journey_id = params.get("journey_id")
        if not journey_id:
            print("⚠ journey_similarity without journey_id")
            return []

        if embedding_model not in {"minilm", "mpnet"}:
            print("⚠ Invalid embedding model:", embedding_model)
            return []

        query_text = f"Journey similar to {journey_id}"

        try:
            return get_similar_journeys(
                query_text=query_text,
                model_key=embedding_model,
                top_k=15
            )
        except Exception as e:
            print("Embedding retrieval error:", e)
            return []

    # ------------------------------------------------
    #           INTENT → QUERY ROUTER
    # ------------------------------------------------
    def route(self, intent, entities):
        airports = entities.get("airports", [])
        routes = entities.get("routes", {}) or {}
        passengers = entities.get("passengers", [])
        journeys = entities.get("journeys", [])

        # ---------- FLIGHT SEARCH ----------
        if intent == "flight_search":
            origin = routes.get("origin") or (airports[0] if len(airports) > 0 else None)
            dest = routes.get("destination") or (airports[1] if len(airports) > 1 else None)

            if not origin or not dest:
                return None, {}
            return "flight_search", {"origin": origin, "destination": dest}

        # ---------- SIMPLE AGGREGATES ----------
        if intent in {
            "delay_info",
            "journey_stats",
            "satisfaction_query",
            "generation_analysis",
            "airport_delay",
            "route_satisfaction",
            "class_delay",
            "class_satisfaction",
            "fleet_performance",
            "high_risk_passengers",
            "frequent_flyers"
        }:
            return intent, {}

        # ---------- LOYALTY ----------
        if intent == "loyalty_miles":
            if not passengers:
                return None, {}
            return "loyalty_miles", {"level": passengers[0]}

        # ---------- CLASS SEARCH ----------
        if intent == "class_search":
            if not passengers:
                return None, {}
            return "class_search", {"class": passengers[0]}

        # ---------- JOURNEY SIMILARITY ----------
        if intent == "journey_similarity":
            if not journeys:
                return None, {}
            return "journey_similarity", {"journey_id": journeys[0]}

        return None, {}

    # ------------------------------------------------
    #            MAIN RETRIEVAL PIPELINE
    # ------------------------------------------------
    def retrieve(
        self,
        intent,
        entities,
        embedding_model,
        use_embeddings=True,
        retrieval_mode="hybrid"
    ):
        """
        Supports:
        - baseline only
        - embeddings only
        - hybrid
        """

        query_key, params = self.route(intent, entities)

        baseline_rows = []
        embedding_rows = []
        queries_run = []

        # ---------- BASELINE ----------
        if retrieval_mode != "embeddings only" and query_key in QUERIES:
            baseline_rows = self.run_query(query_key, params)
            queries_run.append(QUERIES[query_key])

        # ---------- EMBEDDINGS ----------
        if use_embeddings and retrieval_mode != "baseline only":
            embedding_rows = self.run_embedding_query(
                intent,
                params,
                embedding_model
            )

        # ---------- MODE LOGIC ----------
        if retrieval_mode == "baseline only":
            return {
                "baseline": baseline_rows,
                "embeddings": [],
                "merged": baseline_rows,
                "queries_executed": queries_run
            }

        if retrieval_mode == "embeddings only":
            return {
                "baseline": [],
                "embeddings": embedding_rows,
                "merged": embedding_rows,
                "queries_executed": []
            }

        merged = merge_results(baseline_rows, embedding_rows)

        return {
            "baseline": baseline_rows,
            "embeddings": embedding_rows,
            "merged": merged,
            "queries_executed": queries_run
        }
