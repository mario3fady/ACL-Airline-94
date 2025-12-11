QUERIES = {

    # 1. Flight search (origin -> destination)
    "flight_search": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        MATCH (f)-[:DEPARTS_FROM]->(o:Airport)
        MATCH (f)-[:ARRIVES_AT]->(d:Airport)
        WHERE o.station_code = $origin
          AND d.station_code = $destination
        RETURN f.flight_number AS flight,
               o.station_code AS origin,
               d.station_code AS destination,
               j.arrival_delay_minutes AS delay,
               j.food_satisfaction_score AS food_score
        LIMIT 5
    """,

    # 2. Delay info – "Which flights have the worst delays?"
    "delay_info": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        RETURN f.flight_number AS flight,
               j.arrival_delay_minutes AS delay
        ORDER BY delay DESC
        LIMIT 5
    """,

    # 3. Satisfaction query – best food satisfaction
    "satisfaction_query": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        RETURN f.flight_number AS flight,
               j.food_satisfaction_score AS food_score
        ORDER BY food_score DESC
        LIMIT 5
    """,

    # 4. Journey stats – aggregate delay & satisfaction per flight
    "journey_stats": """
        MATCH (j:Journey)-[:ON]->(f:Flight)
        RETURN f.flight_number AS flight,
               AVG(j.arrival_delay_minutes) AS avg_delay,
               AVG(j.food_satisfaction_score) AS avg_food,
               COUNT(j) AS journey_count
        LIMIT 5
    """,

    # 5. Passenger journeys by record locator (NOT WORKING)
    "passenger_journeys": """
        MATCH (p:Passenger {record_locator: $record_locator})-[:TOOK]->(j:Journey)
        RETURN j.feedback_ID AS journey,
               j.arrival_delay_minutes AS delay,
               j.food_satisfaction_score AS food_score
        LIMIT 5
    """,

    # 6. Class search – journeys filtered by passenger class
    "class_search": """
        MATCH (j:Journey)
        WHERE j.passenger_class = $class
        RETURN j.feedback_ID AS journey,
               j.passenger_class AS class,
               j.arrival_delay_minutes AS delay
        LIMIT 5
    """,

    # 7. Loyalty miles – total miles flown by passengers at a loyalty level
    "loyalty_miles": """
        MATCH (p:Passenger {loyalty_program_level: $level})-[:TOOK]->(j:Journey)
        RETURN p.loyalty_program_level AS level,
               SUM(j.actual_flown_miles) AS total_miles,
               COUNT(j) AS journey_count
        LIMIT 5
    """,
    # 8. Airport delay – worst origin airports by average delay
"airport_delay": """
    MATCH (j:Journey)-[:ON]->(f:Flight)-[:DEPARTS_FROM]->(a:Airport)
    RETURN a.station_code AS airport,
           AVG(j.arrival_delay_minutes) AS avg_delay,
           COUNT(j) AS journey_count
    ORDER BY avg_delay DESC
    LIMIT 5
""",

# 9. Route satisfaction – best routes by food satisfaction
"route_satisfaction": """
    MATCH (j:Journey)-[:ON]->(f:Flight)
    MATCH (f)-[:DEPARTS_FROM]->(o:Airport)
    MATCH (f)-[:ARRIVES_AT]->(d:Airport)
    RETURN o.station_code AS origin,
           d.station_code AS destination,
           AVG(j.food_satisfaction_score) AS avg_food,
           COUNT(j) AS journey_count
    ORDER BY avg_food DESC
    LIMIT 5
""",

# 10. Class delay – average delay by passenger class
"class_delay": """
    MATCH (j:Journey)
    RETURN j.passenger_class AS class,
           AVG(j.arrival_delay_minutes) AS avg_delay,
           COUNT(j) AS journey_count
    ORDER BY avg_delay DESC
    LIMIT 3
""",

# 11. Class satisfaction – average food satisfaction by class
"class_satisfaction": """
    MATCH (j:Journey)
    RETURN j.passenger_class AS class,
           AVG(j.food_satisfaction_score) AS avg_food,
           COUNT(j) AS journey_count
    ORDER BY avg_food DESC
""",

# 12. Fleet performance – aircraft type comparison
"fleet_performance": """
    MATCH (j:Journey)-[:ON]->(f:Flight)
    RETURN f.fleet_type_description AS fleet,
           AVG(j.arrival_delay_minutes) AS avg_delay,
           AVG(j.food_satisfaction_score) AS avg_food,
           COUNT(j) AS journey_count
    ORDER BY avg_delay ASC
    LIMIT 5
""",

# 13. High risk passengers – consistently bad experience
"high_risk_passengers": """
    MATCH (p:Passenger)-[:TOOK]->(j:Journey)
    WITH p,
         AVG(j.arrival_delay_minutes) AS avg_delay,
         AVG(j.food_satisfaction_score) AS avg_food,
         COUNT(j) AS journey_count
    WHERE avg_delay > 30 AND avg_food <= 2
    RETURN p.record_locator AS passenger,
           avg_delay,
           avg_food,
           journey_count
    LIMIT 5
""",

# 14. Frequent flyers – most journeys and miles
"frequent_flyers": """
    MATCH (p:Passenger)-[:TOOK]->(j:Journey)
    RETURN p.record_locator AS passenger,
           COUNT(j) AS journey_count,
           SUM(j.actual_flown_miles) AS total_miles
    ORDER BY journey_count DESC
    LIMIT 5
""",

# 15. Generation analysis – satisfaction and delay by generation
"generation_analysis": """
    MATCH (p:Passenger)-[:TOOK]->(j:Journey)
    RETURN p.generation AS generation,
           AVG(j.food_satisfaction_score) AS avg_food,
           AVG(j.arrival_delay_minutes) AS avg_delay,
           COUNT(j) AS journey_count
    ORDER BY avg_food DESC
"""

    
}
