from intent_classifier import classify_intent_llm
from entity_extraction import extract_entities_llm

print("\n--- INTENT TESTS ---")
print(classify_intent_llm("Show me flights from LAX to IAX"))
print(classify_intent_llm("Which flights have the worst delays?"))
print(classify_intent_llm("How many miles did premier silver passengers fly?"))

print("\n--- ENTITY EXTRACTION TESTS ---")
print(extract_entities_llm("Show me flights from LAX to IAX"))
print(extract_entities_llm("Flight 42 from LAX to IAX"))
print(extract_entities_llm("Flights between EWX and LAX"))
print(extract_entities_llm("Why was flight 57 delayed?"))
print(extract_entities_llm("Multi-leg journeys from DEX to IAX"))
