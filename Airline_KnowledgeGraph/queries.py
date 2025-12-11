QUERIES = {

    # 1. Flight search (origin -> destination)
    "flight_search": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
    MATCH (p:Passenger)-[:TOOK]->(j)
    MATCH (f)-[:DEPARTS_FROM]->(o:Airport)
    MATCH (f)-[:ARRIVES_AT]->(d:Airport)
    WHERE o.station_code = $origin
      AND d.station_code = $destination
    RETURN
        j.feedback_ID AS journey,
        f.flight_number AS flight,
        o.station_code AS origin,
        d.station_code AS destination,
        j.arrival_delay_minutes AS delay,
        j.food_satisfaction_score AS food_score,
        j.passenger_class AS passenger_class,
        j.actual_flown_miles AS miles,
        p.record_locator AS passenger,
        p.generation AS generation,
        p.loyalty_program_level AS loyalty_level,
        f.fleet_type_description AS fleet
    LIMIT 50
    """,

    # 2. Delay info – worst delayed flights
    "delay_info": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        MATCH (p:Passenger)-[:TOOK]->(j)
        RETURN
            j.feedback_ID AS journey,
            f.flight_number AS flight,
            j.arrival_delay_minutes AS delay,
            j.food_satisfaction_score AS food_score,
            j.passenger_class AS passenger_class,
            j.actual_flown_miles AS miles,
            p.record_locator AS passenger,
            p.generation AS generation,
            p.loyalty_program_level AS loyalty_level,
            f.fleet_type_description AS fleet
        ORDER BY delay DESC
        LIMIT 50
    """,

    # 3. Best food satisfaction
    "satisfaction_query": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        MATCH (p:Passenger)-[:TOOK]->(j)
        RETURN
            j.feedback_ID AS journey,
            f.flight_number AS flight,
            j.food_satisfaction_score AS food_score,
            j.arrival_delay_minutes AS delay,
            j.passenger_class AS passenger_class,
            j.actual_flown_miles AS miles,
            p.record_locator AS passenger,
            p.generation AS generation,
            p.loyalty_program_level AS loyalty_level,
            f.fleet_type_description AS fleet
        ORDER BY food_score DESC
        LIMIT 50
    """,

    # 4. Journey stats – aggregate delay & satisfaction per flight
    "journey_stats": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        RETURN
            f.flight_number AS flight,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            AVG(j.food_satisfaction_score) AS avg_food,
            COUNT(j) AS journey_count
        LIMIT 50
    """,

    # 5. Generation analysis
    "generation_analysis": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)
        RETURN
            p.generation AS generation,
            AVG(j.food_satisfaction_score) AS avg_food,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            COUNT(j) AS journey_count
        ORDER BY avg_food DESC
        LIMIT 50
    """,

    # 6. Class search – journeys filtered by class
    "class_search": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)
        MATCH (j)-[:ON]->(f:Flight)
        WHERE j.passenger_class = $class
        RETURN
            j.feedback_ID AS journey,
            j.passenger_class AS passenger_class,
            j.arrival_delay_minutes AS delay,
            j.food_satisfaction_score AS food_score,
            j.actual_flown_miles AS miles,
            p.record_locator AS passenger,
            p.generation AS generation,
            p.loyalty_program_level AS loyalty_level,
            f.flight_number AS flight,
            f.fleet_type_description AS fleet
        LIMIT 50
    """,

    # 7. Loyalty miles
    "loyalty_miles": """
        MATCH (p:Passenger {loyalty_program_level: $level})-[:TOOK]->(j:Journey)
        MATCH (j)-[:ON]->(f:Flight)
        RETURN
            p.loyalty_program_level AS level,
            p.record_locator AS passenger,
            p.generation AS generation,
            SUM(j.actual_flown_miles) AS total_miles,
            COUNT(j) AS journey_count,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            AVG(j.food_satisfaction_score) AS avg_food
        LIMIT 50
    """,

    # 8. Airport delay – worst airports
    "airport_delay": """
        MATCH (j:Journey)-[:ON]->(f:Flight)-[:DEPARTS_FROM]->(a:Airport)
        RETURN
            a.station_code AS airport,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            COUNT(j) AS journey_count
        ORDER BY avg_delay DESC
        LIMIT 50
    """,

    # 9. Route satisfaction – best routes
    "route_satisfaction": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        MATCH (f)-[:DEPARTS_FROM]->(o:Airport)
        MATCH (f)-[:ARRIVES_AT]->(d:Airport)
        RETURN
            o.station_code AS origin,
            d.station_code AS destination,
            AVG(j.food_satisfaction_score) AS avg_food,
            COUNT(j) AS journey_count
        ORDER BY avg_food DESC
        LIMIT 50
    """,

    # 10. Class delay
    "class_delay": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)
        RETURN
            j.passenger_class AS passenger_class,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            COUNT(j) AS journey_count
        ORDER BY avg_delay DESC
        LIMIT 50
    """,

    # 11. Class satisfaction
    "class_satisfaction": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)
        RETURN
            j.passenger_class AS passenger_class,
            AVG(j.food_satisfaction_score) AS avg_food,
            COUNT(j) AS journey_count
        ORDER BY avg_food DESC
        LIMIT 50
    """,

    # 12. Fleet performance
    "fleet_performance": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        RETURN
            f.fleet_type_description AS fleet,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            AVG(j.food_satisfaction_score) AS avg_food,
            COUNT(j) AS journey_count
        ORDER BY avg_delay ASC
        LIMIT 50
    """,

    # 13. High risk passengers
    "high_risk_passengers": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)
        WITH p,
            AVG(j.arrival_delay_minutes) AS avg_delay,
            AVG(j.food_satisfaction_score) AS avg_food,
            COUNT(j) AS journey_count
        WHERE avg_delay > 30 AND avg_food <= 2
        RETURN
            p.record_locator AS passenger,
            avg_delay,
            avg_food,
            journey_count,
            p.generation AS generation,
            p.loyalty_program_level AS loyalty_level
        LIMIT 50
    """,

    # 14. Frequent flyers
    "frequent_flyers": """
        MATCH (p:Passenger)-[:TOOK]->(j:Journey)
        RETURN
            p.record_locator AS passenger,
            p.loyalty_program_level AS loyalty_level,
            p.generation AS generation,
            COUNT(j) AS journey_count,
            SUM(j.actual_flown_miles) AS total_miles
        ORDER BY journey_count DESC
        LIMIT 50
    """,
}
