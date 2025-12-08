from neo4j import GraphDatabase
import pandas as pd
import os


URI = os.environ.get("NEO4J_URI")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["USER_NAME"], os.environ["PASSWORD"])
)


df = pd.read_csv("Airline_surveys_sample.csv")
print("Loaded dataset:", df.shape)
print(df.head())



def create_graph(tx, row):
    # -------------------Passenger Node-------------------------
    tx.run("""
        MERGE (p:Passenger {record_locator: $record_locator})
        SET p.loyalty_program_level = $loyalty_program_level,
            p.generation = $generation
    """,
    record_locator=row["record_locator"],
    loyalty_program_level=row["loyalty_program_level"],
    generation=row["generation"]
    )

    # -------------------Journey Node-------------------------

    tx.run("""
        MERGE (j:Journey {feedback_ID: $feedback_ID})
        SET j.food_satisfaction_score = $food_satisfaction_score,
            j.arrival_delay_minutes = $arrival_delay_minutes,
            j.actual_flown_miles = $actual_flown_miles,
            j.number_of_legs = $number_of_legs,
            j.passenger_class = $passenger_class
    """,
    feedback_ID=row["feedback_ID"],
    food_satisfaction_score=row["food_satisfaction_score"],
    arrival_delay_minutes=row["arrival_delay_minutes"],
    actual_flown_miles=row["actual_flown_miles"],
    number_of_legs=row["number_of_legs"],
    passenger_class=row["passenger_class"]
    )

    # -------------------Flight Node-------------------------
    tx.run("""
        MERGE (f:Flight {
            flight_number: $flight_number,
            fleet_type_description: $fleet_type_description
        })
    """,
    flight_number=row["flight_number"],
    fleet_type_description=row["fleet_type_description"]
    )

    # -------------------Airport Nodes-------------------------
    tx.run("""
        MERGE (a1:Airport {station_code: $origin})
        MERGE (a2:Airport {station_code: $destination})
    """,
    origin=row["origin_station_code"],
    destination=row["destination_station_code"]
    )

    # -------------------Relationships-------------------------
    tx.run("""
        MATCH (p:Passenger {record_locator: $record_locator}),
              (j:Journey {feedback_ID: $feedback_ID}),
              (f:Flight {flight_number: $flight_number, fleet_type_description: $fleet_type_description}),
              (a1:Airport {station_code: $origin}),
              (a2:Airport {station_code: $destination})

        MERGE (p)-[:TOOK]->(j)
        MERGE (j)-[:ON]->(f)
        MERGE (f)-[:DEPARTS_FROM]->(a1)
        MERGE (f)-[:ARRIVES_AT]->(a2)
    """,
    record_locator=row["record_locator"],
    feedback_ID=row["feedback_ID"],
    flight_number=row["flight_number"],
    fleet_type_description=row["fleet_type_description"],
    origin=row["origin_station_code"],
    destination=row["destination_station_code"]
    )
    
with driver.session() as session:
    for i, row in df.iterrows():
        session.execute_write(create_graph, row)
        if i % 200 == 0:
            print(f"Inserted {i} rows...")

print("NEW RAW KG CREATED ")
driver.close()
