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

    # ---------------------------
    # Sort by embedding score
    # ---------------------------
    merged_list.sort(
        key=lambda x: (x["score"] is None, x["score"] if x["score"] is not None else float("inf"))
    )

    return merged_list


# ---------------------------------------------------
# FORMATTER: Convert KG raw data → human readable text
# ---------------------------------------------------
# def format_kg_result(intent, records):
#     """
#     Convert raw Neo4j result list into clean human-readable text.
#     Safely handles missing keys and invalid record types.
#     """

#     # --- Embedding-only similarity mode ---
#     if intent == "embedding_similarity":
#         lines = ["Here are journeys most similar to your request:\n"]
#         for r in records:
#             lines.append(
#                 f"- Journey {r.get('journey')} | Delay: {r.get('delay')} | "
#                 f"Food Score: {r.get('food')} | Similarity Score: {r.get('score'):.4f}"
#             )
#         return "\n".join(lines)
    
#     # Empty or invalid
#     if not records or isinstance(records, dict):
#         return "No matching results found in the knowledge graph."

#     # Keep only dict rows
#     safe_records = [r for r in records if isinstance(r, dict)]
#     if not safe_records:
#         return "No structured data returned from the knowledge graph."

#     # ---------------- FLIGHT SEARCH ----------------
#     if intent == "flight_search":
#         lines = ["Here are the flights found:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Flight {r.get('flight')} from {r.get('origin')} to {r.get('destination')} "
#                 f"had a delay of {r.get('delay')} minutes and a food score of {r.get('food_score')}."
#             )
#         return "\n".join(lines)

#     # ---------------- DELAY INFO ----------------
#     if intent == "delay_info":
#         lines = ["Worst delayed flights:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Flight {r.get('flight')} had a delay of {r.get('delay')} minutes."
#             )
#         return "\n".join(lines)

#     # ---------------- SATISFACTION QUERY ----------------
#     if intent == "satisfaction_query":
#         lines = ["Flights with top food satisfaction scores:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Flight {r.get('flight')} has a food satisfaction score of {r.get('food_score')}."
#             )
#         return "\n".join(lines)

#     # ---------------- JOURNEY STATS ----------------
#     if intent == "journey_stats":
#         lines = ["Journey statistics per flight:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Flight {r.get('flight')}: "
#                 f"Avg Delay = {r.get('avg_delay')} min | "
#                 f"Avg Food Score = {r.get('avg_food')} | "
#                 f"Journeys Count = {r.get('journey_count')}."
#             )
#         return "\n".join(lines)

#     # ---------------- GENERATION ANALYSIS ----------------
#     if intent == "generation_analysis":
#         lines = ["Generation analysis (satisfaction & delays):\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Generation {r.get('generation')}: "
#                 f"Avg Food Score = {r.get('avg_food'):.1f}, "
#                 f"Avg Delay = {r.get('avg_delay'):.1f} min, "
#                 f"Journeys = {r.get('journey_count')}."
#             )
#         return "\n".join(lines)

#     # ---------------- PASSENGER JOURNEY (SINGULAR) ----------------
#     if intent == "passenger_journey":
#         lines = ["Passenger journey history:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Journey {r.get('journey')} | Flight {r.get('flight')} | "
#                 f"Delay = {r.get('delay')} minutes | Food Score = {r.get('food_score')}."
#             )
#         return "\n".join(lines)

#     # ---------------- LEGACY PASSENGER_JOURNEYS (keep for safety) ----------------
#     if intent == "passenger_journeys":
#         lines = ["Passenger journey history:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Journey {r.get('journey')}: delay = {r.get('delay')} minutes, "
#                 f"food score = {r.get('food_score')}."
#             )
#         return "\n".join(lines)

#     # ---------------- CLASS SEARCH ----------------
#     if intent == "class_search":
#         lines = ["Journeys for passengers in this class:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Journey {r.get('journey')} (Class: {r.get('class')}), "
#                 f"Delay = {r.get('delay')} minutes."
#             )
#         return "\n".join(lines)

#     # ---------------- LOYALTY MILES ----------------
#     if intent == "loyalty_miles":
#         lines = ["Loyalty miles summary:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Loyalty Level: {r.get('level')}\n"
#                 f"  Total Miles: {r.get('total_miles')}\n"
#                 f"  Journeys Taken: {r.get('journey_count')}"
#             )
#         return "\n".join(lines)

#     # ---------------------- AIRPORT DELAY ----------------------
#     if intent == "airport_delay":
#         lines = ["Worst airports by delay:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Airport {r.get('airport')}: avg delay {r.get('avg_delay'):.1f} min "
#                 f"across {r.get('journey_count')} journeys."
#             )
#         return "\n".join(lines)

#     # ---------------------- ROUTE SATISFACTION ----------------------
#     if intent == "route_satisfaction":
#         lines = ["Best routes for food satisfaction:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- {r.get('origin')} → {r.get('destination')}: avg food {r.get('avg_food'):.1f}, "
#                 f"{r.get('journey_count')} journeys."
#             )
#         return "\n".join(lines)

#     # ---------------------- CLASS DELAY ----------------------
#     if intent == "class_delay":
#         lines = ["Delays by passenger class:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Class {r.get('class')}: avg delay {r.get('avg_delay'):.1f} min "
#                 f"({r.get('journey_count')} journeys)."
#             )
#         return "\n".join(lines)

#     # ---------------------- CLASS SATISFACTION ----------------------
#     if intent == "class_satisfaction":
#         lines = ["Food satisfaction by passenger class:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Class {r.get('class')}: avg food score {r.get('avg_food'):.1f} "
#                 f"({r.get('journey_count')} journeys)."
#             )
#         return "\n".join(lines)

#     # ---------------------- FLEET PERFORMANCE ----------------------
#     if intent == "fleet_performance":
#         lines = ["Fleet performance summary:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Fleet {r.get('fleet')}: avg delay {r.get('avg_delay'):.1f} min, "
#                 f"avg food {r.get('avg_food'):.1f}, {r.get('journey_count')} journeys."
#             )
#         return "\n".join(lines)

#     # ---------------------- HIGH RISK PASSENGERS ----------------------
#     if intent == "high_risk_passengers":
#         lines = ["Passengers with consistently bad experiences:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Passenger {r.get('passenger')}: avg delay {r.get('avg_delay'):.1f}, "
#                 f"avg food {r.get('avg_food'):.1f}, {r.get('journey_count')} journeys."
#             )
#         return "\n".join(lines)

#     # ---------------------- FREQUENT FLYERS ----------------------
#     if intent == "frequent_flyers":
#         lines = ["Top frequent flyers:\n"]
#         for r in safe_records:
#             lines.append(
#                 f"- Passenger {r.get('passenger')}: {r.get('journey_count')} journeys, "
#                 f"{r.get('total_miles')} miles."
#             )
#         return "\n".join(lines)

#     # Fallback
#     return str(records)


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
    def retrieve(self, intent, entities, use_embeddings=True):
        # 1. Baseline routing
        query_key, params = self.route(intent, entities)

        if query_key is None:
            return {"error": "Unable to determine query from intent/entities."}

        print("bedooo", query_key)
        # 2. Run baseline Cypher
        baseline_result = self.run_query(query_key, params)

        # 3. Run embedding retrieval (optional)
        embedding_result = []
        if use_embeddings:
            embedding_result = get_similar_journeys(
                intent + " " + " ".join(entities.get("airports", []))
            )
        # 4. Merge results
        merged = merge_results(baseline_result, embedding_result)

        # 5. Build unified context for LLM
        context = {
            "intent": intent,
            "entities": entities,
            "query_key": query_key,
            "params": params,
            "baseline": baseline_result,
            "embeddings": embedding_result,
            "merged": merged,
            "metadata": {
                "baseline_count": len(baseline_result) if isinstance(baseline_result, list) else 0,
                "embedding_count": len(embedding_result)
            }
        }
        

        return context
