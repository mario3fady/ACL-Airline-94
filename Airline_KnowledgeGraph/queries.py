# queries.py
# Cypher templates for baseline retrieval

QUERIES = {

    # 1 — Search flights by origin/destination
    "flight_search": """
        MATCH (f:Flight)-[:DEPARTS_FROM]->(a1:Airport {station_code: $origin})
              -[:ARRIVES_AT]->(a2:Airport {station_code: $destination})
        RETURN f.flight_number AS flight, a1.station_code AS origin, a2.station_code AS destination
    """,

    # 2 — Find all flights from an airport
    "flight_from_airport": """
        MATCH (f:Flight)-[:DEPARTS_FROM]->(a:Airport {station_code: $origin})
        RETURN f.flight_number AS flight, a.station_code AS origin
    """,

    # 3 — Flight delay info
    "delay_info": """
        MATCH (j:Journey)-[:ON]->(f:Flight {flight_number: $flight})
        RETURN f.flight_number AS flight,
               AVG(j.arrival_delay_minutes) AS avg_delay,
               MAX(j.arrival_delay_minutes) AS worst_delay
    """,

    # 4 — Worst delay flights
    "worst_delays": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        RETURN f.flight_number AS flight,
               AVG(j.arrival_delay_minutes) AS avg_delay
        ORDER BY avg_delay DESC LIMIT 10
    """,

    # 5 — Loyalty miles query
    "loyalty_miles": """
        MATCH (p:Passenger {loyalty_program_level: $level})-[:TOOK]->(j:Journey)
        RETURN p.loyalty_program_level AS loyalty, SUM(j.actual_flown_miles) AS miles
    """,

    # 6 — Satisfaction score average
    "satisfaction_query": """
        MATCH (j:Journey)
        RETURN AVG(j.food_satisfaction_score) AS avg_food_score
    """,

    # 7 — Multi-leg journey count
    "journey_stats": """
        MATCH (j:Journey)
        WHERE j.number_of_legs > 1
        RETURN COUNT(j) AS multi_leg_count
    """,

    # 8 — Passenger-specific journeys
    "passenger_journeys": """
        MATCH (p:Passenger {record_locator: $record_locator})-[:TOOK]->(j:Journey)
        RETURN p.record_locator AS passenger, COUNT(j) AS journey_count
    """,

    # 9 — Airport traffic (departures)
    "airport_traffic": """
        MATCH (f:Flight)-[:DEPARTS_FROM]->(a:Airport {station_code: $origin})
        RETURN COUNT(f) AS departures
    """,

    # 10 — Flights by fleet type
    "fleet_type_flights": """
        MATCH (f:Flight {fleet_type_description: $fleet})
        RETURN f.flight_number AS flight
    """,

    # 11-Rank flights by food score
    "avg_food_by_flight": """
    MATCH (j:Journey)-[:ON]->(f:Flight)
    RETURN f.flight_number AS flight,
           AVG(j.food_satisfaction_score) AS avg_food_score
    ORDER BY avg_food_score DESC
    """,

    #12-Filter flights by legs count
    "flights_with_many_legs": """
    MATCH (j:Journey)-[:ON]->(f:Flight)
    WHERE j.number_of_legs > $legs
    RETURN f.flight_number AS flight, j.number_of_legs AS legs
    ORDER BY legs DESC
    """,


    #13-Count passengers per flight
    "passenger_count_per_flight": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)-[:ON]->(f:Flight)
        RETURN f.flight_number AS flight,
            COUNT(p) AS passenger_count
        ORDER BY passenger_count DESC
    """,

    
    #14-Direct airport-to-airport routes
    "routes_between_airports": """
    MATCH (f:Flight)-[:DEPARTS_FROM]->(a1:Airport {station_code: $origin}),
          (f)-[:ARRIVES_AT]->(a2:Airport {station_code: $destination})
    RETURN f.flight_number AS flight, a1.station_code AS origin, a2.station_code AS destination
    """,

    #15-Count passengers by generation
    "passenger_by_generation": """
    MATCH (p:Passenger {generation: $generation})
    RETURN p.generation AS generation,
           COUNT(p) AS passenger_count
    """
}
