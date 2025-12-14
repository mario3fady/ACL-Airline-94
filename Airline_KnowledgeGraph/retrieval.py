from neo4j import GraphDatabase
from queries import QUERIES

from embeddings.embedding_retreival import get_similar_journeys


def merge_results(baseline_list, embedding_list, key_candidates=None):
    """
    Merges baseline Cypher rows with embedding-based rows.
    Automatically detects the correct unique key from a list of candidates.
    """

    if baseline_list is None:
        baseline_list = []
    if embedding_list is None:
        embedding_list = []

    if key_candidates is None:
        key_candidates = ["journey", "flight", "journey_id", "generation"]

    def detect_key(row):
        for k in key_candidates:
            if k in row and row[k] is not None:
                return k, row[k]
        return None, None

    merged = {}

    # ---------------------------
    # Add baseline first
    # ---------------------------
    for row in baseline_list:
        row = dict(row)
        key_name, key_value = detect_key(row)

        if key_value is None:
            # create artificial unique ID to avoid collisions
            key_value = id(row)

        row["score"] = None  # baseline has no embedding score
        merged[key_value] = row

    # ---------------------------
    # Add embedding results
    # ---------------------------
    for row in embedding_list:
        row = dict(row)
        key_name, key_value = detect_key(row)

        if key_value is None:
            key_value = id(row)

        if key_value not in merged:
            merged[key_value] = row
        else:
            # merge scores instead of discarding embeddings
            if merged[key_value].get("score") is None and row.get("score") is not None:
                merged[key_value]["score"] = row["score"]

            # merge any missing fields
            for k, v in row.items():
                if k not in merged[key_value] or merged[key_value][k] is None:
                    merged[key_value][k] = v

    merged_list = list(merged.values())
    # print("baseline_list", baseline_list)
    # print("embeddings_list", embedding_list)
    print("merged_list",merged_list)
    print("baseline_List",baseline_list)
    print("embeddings_List", embedding_list)

    # ---------------------------
    # Sort by embedding score
    # ---------------------------
    merged_list.sort(
        key=lambda x: (x["score"] is None, x["score"] if x["score"] is not None else float("inf"))
    )

    return merged_list




# ---------------------------------------------------
#                RETRIEVER CLASS
# ---------------------------------------------------
class Retriever:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ---------------- CYPHER EXECUTION ----------------
    def run_query(self, query_key, params=None):
        query = QUERIES.get(query_key)
        if query is None:
            return {"error": f"Unknown query: {query_key}"}

        if params is None:
            params = {}

        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return [r.data() for r in result]
        except Exception as e:
            return {"error": str(e)}

    # ---------------------------------------------------
    #   NEW: BASELINE QUERY WRAPPER (needed for UI mode)
    # ---------------------------------------------------
    def run_baseline_query(self, intent, entities):
        query_key, params = self.route(intent, entities)

        if query_key is None:
            return []

        return self.run_query(query_key, params)

    # ---------------------------------------------------
    #   NEW: EMBEDDING QUERY WRAPPER
    # ---------------------------------------------------
    def run_embedding_query(self, intent, params, embedding_model=None):
        """
        Runs the embedding-based retrieval for supported intents.
        Right now, only 'journey_similarity' uses embeddings.

        embedding_model:
            - None     → default to "model1"
            - "model1" → Journey.embedding_model1 ([delay, miles])
            - "model2" → Journey.embedding_model2 ([legs, food])
        """
        if intent != "journey_similarity":
            return []

        journey_id = params.get("journey_id")
        if not journey_id:
            # If you want, you can also handle params["flight_number"] later
            print("⚠ journey_similarity called without journey_id")
            return []

        # Decide which model to use (fallback to model1)
        model_to_use = embedding_model 

        try:
            return get_similar_journeys(
                journey_id=journey_id,
                top_k=10,
                model=model_to_use,
            )
        except Exception as e:
            print("Embedding retrieval error:", e)
            return []


    # ---------------- INTENT → QUERY ROUTING ----------------
    def route(self, intent, entities):
        """
        Convert (intent + extracted entities) → (query_key, params)
        """

        airports = entities.get("airports", [])
        routes = entities.get("routes", {}) or {}
        passengers = entities.get("passengers", [])

        print("\n--- ROUTER DEBUG ---")
        print("Intent:", intent)
        print("Entities:", entities)

        # ---------- FLIGHT SEARCH ----------
        if intent == "flight_search":
            origin = routes.get("origin") or (airports[0] if len(airports) > 0 else "")
            dest = routes.get("destination") or (airports[1] if len(airports) > 1 else "")

            if not origin or not dest:
                print("⚠ Missing origin/destination → flight_search aborted")
                return None, {}

            return "flight_search", {"origin": origin, "destination": dest}

        # ---------- DELAY INFO ----------
        if intent == "delay_info":
            return "delay_info", {}

        # ---------- LOYALTY MILES ----------
        if intent == "loyalty_miles":
            level = passengers[0] if passengers else ""
            if not level:
                print("⚠ Missing loyalty level")
                return None, {}
            return "loyalty_miles", {"level": level}

        # ---------- JOURNEY STATS ----------
        if intent == "journey_stats":
            return "journey_stats", {}

        # ---------- SATISFACTION ----------
        if intent == "satisfaction_query":
            return "satisfaction_query", {}

        # ---------- GENERATION ANALYSIS ----------
        if intent == "generation_analysis":
            # No parameters needed
            return "generation_analysis", {}

        # ---------- CLASS SEARCH ----------
        if intent == "class_search":
            # Assume first passenger-like token is the class name (e.g., "Economy")
            cls = passengers[0] if passengers else ""
            if not cls:
                print("⚠ Missing passenger class for class_search")
                return None, {}
            return "class_search", {"class": cls}

        # ---------- AIRPORT DELAY ----------
        if intent == "airport_delay":
            # Aggregate per airport, no params
            return "airport_delay", {}

        # ---------- ROUTE SATISFACTION ----------
        if intent == "route_satisfaction":
            # Aggregate per origin-destination route
            return "route_satisfaction", {}

        # ---------- CLASS DELAY ----------
        if intent == "class_delay":
            return "class_delay", {}

        # ---------- CLASS SATISFACTION ----------
        if intent == "class_satisfaction":
            return "class_satisfaction", {}

        # ---------- FLEET PERFORMANCE ----------
        if intent == "fleet_performance":
            return "fleet_performance", {}

        # ---------- HIGH RISK PASSENGERS ----------
        if intent == "high_risk_passengers":
            return "high_risk_passengers", {}

        # ---------- FREQUENT FLYERS ----------
        if intent == "frequent_flyers":
            return "frequent_flyers", {}
        
        if intent == "journey_similarity":
            # Try to get a journey ID first
            journeys = entities.get("journeys", [])
            flights = entities.get("flights", [])

            if journeys:
                # e.g. "F_16"
                return "journey_similarity", {"journey_id": journeys[0]}

        # ---------- PASSENGER JOURNEY ----------
        if intent == "passenger_journey":
            if not passengers:
                print("⚠ No passenger ID detected for passenger_journey")
                return None, {}
            record_locator = passengers[0]
            return "passenger_journey", {"record_locator": record_locator}

        # Unknown intent
        return None, {}

    # ---------------- MAIN RETRIEVAL METHOD ----------------
        # ---------------- MAIN RETRIEVAL METHOD ----------------
    def retrieve(self, intent, entities, use_embeddings=True, retrieval_mode="hybrid", embedding_model=None):
        """
        Unified retrieval controller.
        Supports:
        - baseline only
        - embeddings only
        - hybrid (baseline + embeddings + merge)
        """

        # 0) Route intent + entities → (query_key, params)
        query_key, params = self.route(intent, entities)

        queries_run = []
        baseline_rows = []
        embedding_rows = []

        # ----------------------------
        # 1. Baseline Retrieval
        # ----------------------------
        if retrieval_mode != "embeddings only" and query_key is not None and query_key in QUERIES:
            baseline_rows = self.run_query(query_key, params)
            queries_run.append(QUERIES[query_key])

               # ----------------------------
        # 2. Embedding retrieval (optional)
        # ----------------------------
        if use_embeddings and retrieval_mode != "baseline only":
            embedding_rows = self.run_embedding_query(intent, params, embedding_model=embedding_model)

        # ----------------------------
        # 3. Retrieval Mode Logic
        # ----------------------------
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
                "queries_executed": queries_run
            }

        # ----------------------------
        # 4. Hybrid (Default)
        # ----------------------------
        merged = merge_results(baseline_rows, embedding_rows)

        return {
            "baseline": baseline_rows,
            "embeddings": embedding_rows,
            "merged": merged,
            "queries_executed": queries_run
        }


