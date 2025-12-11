from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm

print("\n--- INTENT TESTS ---")
# print(classify_intent_llm("Show me flights from LAX to IAX"))
# print(classify_intent_llm("Which flights have the worst delays?"))
# print(classify_intent_llm("How many miles did premier silver passengers fly?"))
# # 5. passenger_satisfaction
# print(classify_intent_llm("What is the average satisfaction score for passengers on flight 203?"))

# # 6. airport_delays
# print(classify_intent_llm("Which airports had the longest delays last month?"))

# # 7. airline_performance
# print(classify_intent_llm("Compare the performance of United Airlines and Delta Airlines."))

# # 8. aircraft_utilization
# print(classify_intent_llm("How many hours was aircraft A320-900 utilized this week?"))

# # 9. route_popularity
# print(classify_intent_llm("What are the most popular routes between California and Texas?"))

# # 10. flight_cancellations
# print(classify_intent_llm("How many flights were canceled yesterday?"))

# # 11. airline_market_share
# print(classify_intent_llm("What is the market share of American Airlines?"))

# # 12. weather_delay_correlation
# print(classify_intent_llm("How much do weather conditions affect flight delays?"))

# # 13. passenger_food_feedback
# print(classify_intent_llm("What did passengers think about the food on Emirates flights?"))

# # 14. frequent_flyers
# print(classify_intent_llm("Who are the top 5 frequent flyers this year?"))


# print("\n--- ADDITIONAL ENTITY EXTRACTION TESTS ---")

# # passenger_satisfaction
# print(extract_entities_llm("Show passenger satisfaction for Flight 203"))

# # airport_delays
# print(extract_entities_llm("Delays at JFK airport last month"))

# # airline_performance
# print(extract_entities_llm("United Airlines performance metrics"))

# # aircraft_utilization
# print(extract_entities_llm("Utilization for aircraft tail number N492UA"))

# # route_popularity
# print(extract_entities_llm("Most popular routes from LAX to Texas"))

# # flight_cancellations
# print(extract_entities_llm("Cancelled flights from LAX yesterday"))

# # airline_market_share
# print(extract_entities_llm("Market share of Delta Airlines this year"))

# # weather_delay_correlation
# print(extract_entities_llm("How does weather affect delays between ORD and DEN?"))

# # passenger_food_feedback
# print(extract_entities_llm("Passenger food feedback on Qatar Airways flights"))

# # frequent_flyers
# print(extract_entities_llm("Top frequent flyers by miles flown"))

print("\n--- ENTITY EXTRACTION TESTS ---")
# print(extract_entities_llm("Show me flights from LAX to IAX"))
# print(extract_entities_llm("Flight 42 from LAX to IAX"))
# print(extract_entities_llm("Flights between EWX and LAX"))
print(extract_entities_llm("Why was flight 57 delayed?"))
print(extract_entities_llm("Multi-leg journeys from DEX to IAX"))
