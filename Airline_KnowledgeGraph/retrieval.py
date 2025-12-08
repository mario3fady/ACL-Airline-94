from neo4j import GraphDatabase
from queries import QUERIES


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
        entities format (from entity_extraction.py):

        {
          "flights": [],
          "airports": [],
          "passengers": [],
          "journeys": [],
          "routes": {
              "origin": "",
              "destination": ""
          }
        }
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
            # Prefer structured routes, fall back to airport list
            origin = routes.get("origin") or (airports[0] if len(airports) > 0 else "")
            dest = routes.get("destination") or (airports[1] if len(airports) > 1 else "")

            if not origin or not dest:
                print("⚠ Missing origin/destination for flight_search")
                return None, {}

            return "flight_search", {"origin": origin, "destination": dest}

        # ---------- DELAY INFO ----------
        if intent == "delay_info":
            # "Which flights have the worst delays?"
            return "delay_info", {}

        # ---------- LOYALTY MILES ----------
        if intent == "loyalty_miles":
            # passengers list holds loyalty/program mentions (e.g., ["premier silver"])
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
