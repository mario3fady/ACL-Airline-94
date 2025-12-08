from neo4j import GraphDatabase
from queries import QUERIES


# ---------------------------------------------------
# FORMATTER: Convert KG raw data → human readable text
# ---------------------------------------------------
def format_kg_result(intent, records):
    """
    Convert raw Neo4j result list into clean human-readable text.
    Safely handles missing keys and invalid record types.
    """

    # If empty or invalid
    if not records or isinstance(records, dict):
        return "No matching results found in the knowledge graph."

    # Keep only dict-like rows
    safe_records = [r for r in records if isinstance(r, dict)]
    if not safe_records:
        return "No structured data returned from the knowledge graph."

    # ---------------- FLIGHT SEARCH ----------------
    if intent == "flight_search":
        lines = ["Here are the flights found:\n"]
        for r in safe_records:
            lines.append(
                f"- Flight {r.get('flight')} from {r.get('origin')} to {r.get('destination')} "
                f"has a delay of {r.get('delay')} minutes and a food score of {r.get('food_score')}."
            )
        return "\n".join(lines)

    # ---------------- DELAY INFO ----------------
    if intent == "delay_info":
        lines = ["Worst delayed flights:\n"]
        for r in safe_records:
            lines.append(
                f"- Flight {r.get('flight')} had a delay of {r.get('delay')} minutes."
            )
        return "\n".join(lines)

    # ---------------- SATISFACTION QUERY ----------------
    if intent == "satisfaction_query":
        lines = ["Flights with top food satisfaction scores:\n"]
        for r in safe_records:
            lines.append(
                f"- Flight {r.get('flight')} has a food satisfaction score of {r.get('food_score')}."
            )
        return "\n".join(lines)

    # ---------------- JOURNEY STATS ----------------
    if intent == "journey_stats":
        lines = ["Journey statistics per flight:\n"]
        for r in safe_records:
            lines.append(
                f"- Flight {r.get('flight')}: "
                f"Avg Delay = {r.get('avg_delay')} min | "
                f"Avg Food Score = {r.get('avg_food')} | "
                f"Journeys Count = {r.get('journey_count')}."
            )
        return "\n".join(lines)

    # ---------------- PASSENGER JOURNEYS ----------------
    if intent == "passenger_journeys":
        lines = ["Passenger journey history:\n"]
        for r in safe_records:
            lines.append(
                f"- Journey {r.get('journey')}: delay = {r.get('delay')} minutes, "
                f"food score = {r.get('food_score')}."
            )
        return "\n".join(lines)

    # ---------------- CLASS SEARCH ----------------
    if intent == "class_search":
        lines = ["Journeys for passengers in this class:\n"]
        for r in safe_records:
            lines.append(
                f"- Journey {r.get('journey')} (Class: {r.get('class')}), "
                f"Delay = {r.get('delay')} minutes."
            )
        return "\n".join(lines)

    # ---------------- LOYALTY MILES ----------------
    if intent == "loyalty_miles":
        lines = ["Loyalty miles summary:\n"]
        for r in safe_records:
            lines.append(
                f"- Loyalty Level: {r.get('level')}\n"
                f"  Total Miles: {r.get('total_miles')}\n"
                f"  Journeys Taken: {r.get('journey_count')}"
            )
        return "\n".join(lines)

    # DEFAULT FALLBACK
    return str(records)


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
        """
        Execute a Cypher query identified by query_key with parameter dict `params`.
        Returns a list of dicts (records).
        """
        query = QUERIES.get(query_key)

        if query is None:
            return {"error": f"Unknown query: {query_key}"}

        if params is None:
            params = {}

        # Debug logging
        print("\n--- EXECUTING CYPHER QUERY ---")
        print("Query Key:", query_key)
        print("Cypher:", query)
        print("Parameters:", params)

        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                data = [r.data() for r in result]

            print("Query Output:", data)
            return data

        except Exception as e:
            print("❌ CYPHER ERROR:", e)
            return {"error": str(e)}

    # ---------------- INTENT → QUERY ROUTING ----------------
    def route(self, intent, entities):
        """
        Map (intent + extracted entities) -> (query_key, params)
        """

        flights = entities.get("flights", [])
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
                print("⚠ Missing origin/destination for flight_search")
                return None, {}

            return "flight_search", {"origin": origin, "destination": dest}

        # ---------- DELAY INFO ----------
        if intent == "delay_info":
            return "delay_info", {}

        # ---------- LOYALTY MILES ----------
        if intent == "loyalty_miles":
            level = passengers[0] if passengers else ""
            if not level:
                print("⚠ Loyalty level missing for loyalty_miles")
                return None, {}
            return "loyalty_miles", {"level": level}

        # ---------- JOURNEY STATS ----------
        if intent == "journey_stats":
            return "journey_stats", {}

        # ---------- SATISFACTION ----------
        if intent == "satisfaction_query":
            return "satisfaction_query", {}

        # ---------- GENERAL CHAT OR UNKNOWN ----------
        return None, {}
