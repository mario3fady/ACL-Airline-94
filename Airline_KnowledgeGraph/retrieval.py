from neo4j import GraphDatabase
from queries import QUERIES

from embeddings.embedding_retreival import get_similar_journeys


def merge_results(baseline_list, embedding_list, key="journey"):
    """
    Merge baseline Cypher results and embedding-based results:
    - Convert everything to consistent dictionaries
    - Remove duplicates by `key` (default: journey/feedback_ID)
    - Return merged sorted by embedding score (if available)
    """

    if baseline_list is None:
        baseline_list = []

    if embedding_list is None:
        embedding_list = []

    # Standardize baseline: ensure all records have a "journey" or "flight" key
    cleaned_baseline = []
    for r in baseline_list:
        r_fixed = dict(r)

        # Make sure every record has a unique ID field
        if "journey" not in r_fixed:
            # Some queries return flight_number; embed-based returns journey ID
            r_fixed["journey"] = r_fixed.get("journey") or r_fixed.get("flight") or None

        # No embedding score here
        r_fixed["score"] = None
        cleaned_baseline.append(r_fixed)

    # Clean embedding results (they already contain journey + score)
    cleaned_embedding = []
    for r in embedding_list:
        cleaned_embedding.append({
            "journey": r.get("journey"),
            "delay": r.get("delay"),
            "food": r.get("food"),
            "score": r.get("score")
        })

    # Deduplicate using a dictionary keyed by journey ID
    merged = {}
    for r in cleaned_baseline:
        jid = r.get("journey")
        if jid not in merged:
            merged[jid] = r

    for r in cleaned_embedding:
        jid = r.get("journey")
        if jid not in merged:
            merged[jid] = r
        else:
            # If exists, update with embedding score
            merged[jid]["score"] = r.get("score")

    # Convert back to list
    merged_list = list(merged.values())

    # Sort by embedding similarity when available
    merged_list.sort(key=lambda x: (x["score"] is None, x["score"]), reverse=False)

    return merged_list

# ---------------------------------------------------
# FORMATTER: Convert KG raw data → human readable text
# ---------------------------------------------------
def format_kg_result(intent, records):
    """
    Convert raw Neo4j result list into clean human-readable text.
    Safely handles missing keys and invalid record types.
    """

    if intent == "embedding_similarity":
        lines = ["Here are journeys most similar to your request:\n"]
        for r in records:
            lines.append(
                f"- Journey {r.get('journey')} | Delay: {r.get('delay')} | "
                f"Food Score: {r.get('food')} | Similarity Score: {r.get('score'):.4f}"
            )
        return "\n".join(lines)
    
    # Empty or invalid
    if not records or isinstance(records, dict):
        return "No matching results found in the knowledge graph."

    # Keep only dict rows
    safe_records = [r for r in records if isinstance(r, dict)]
    if not safe_records:
        return "No structured data returned from the knowledge graph."

    # ---------------- FLIGHT SEARCH ----------------
    if intent == "flight_search":
        lines = ["Here are the flights found:\n"]
        for r in safe_records:
            lines.append(
                f"- Flight {r.get('flight')} from {r.get('origin')} to {r.get('destination')} "
                f"had a delay of {r.get('delay')} minutes and a food score of {r.get('food_score')}."
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

    # DEFAULT
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

        # Unknown intent
        return None, {}

    # ---------------- MAIN RETRIEVAL METHOD ----------------
    def retrieve(self, intent, entities, use_embeddings=True):
        # 1. Baseline routing
        query_key, params = self.route(intent, entities)

        if query_key is None:
            return {"error": "Unable to determine query from intent/entities."}

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
