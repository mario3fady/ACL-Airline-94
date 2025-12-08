from neo4j import GraphDatabase
from queries import QUERIES

class Retriever:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query_key, params):
        query = QUERIES.get(query_key)

        if query is None:
            return {"error": f"Unknown query: {query_key}"}

        # ---------------- DEBUG LOGGING ----------------
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

    # -------- Intent routing logic --------
    def route(self, intent, entities):
        flights = entities.get("flights", [])
        airports = entities.get("airports", [])
        routes = entities.get("routes", {})
        passengers = entities.get("passengers", [])

        # ---------------- ROUTING DEBUG ----------------
        print("\n--- ROUTER DEBUG ---")
        print("Intent:", intent)
        print("Entities:", entities)

        # ---------- FLIGHT SEARCH ----------
        if intent == "flight_search":
            origin = routes.get("origin", "")
            dest = routes.get("destination", "")

            # If entity extraction failed, try airports[] list
            if (not origin or not dest) and len(airports) >= 2:
                origin, dest = airports[:2]

            # If still empty → stop early
            if not origin or not dest:
                print("⚠ Missing origin/destination → cannot run flight_search")
                return None, {}

            return "flight_search", {
                "origin": origin,
                "destination": dest
            }

        # ---------- DELAY INFO ----------
        if intent == "delay_info":
            return "worst_delays", {}

        # ---------- LOYALTY MILES ----------
        if intent == "loyalty_miles":
            level = passengers[0] if passengers else ""
            if not level:
                print("⚠ Loyalty level missing")
            return "loyalty_miles", {"level": level}

        # ---------- JOURNEY STATS ----------
        if intent == "journey_stats":
            return "journey_stats", {}

        # ---------- SATISFACTION ----------
        if intent == "satisfaction_query":
            return "satisfaction_query", {}

        return None, {}
