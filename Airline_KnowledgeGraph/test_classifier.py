from intent_classifier import extract_entities_llm

print(extract_entities_llm("Show me flights from LAX to IAX"))
print(extract_entities_llm("Which flights have the worst delays?"))
print(extract_entities_llm("How many miles did premier silver passengers fly?"))
print(extract_entities_llm("Hello, how are you?"))
print(extract_entities_llm("Recommend me something nice"))
print(extract_entities_llm("How many miles do premier silver members fly?"))
print(extract_entities_llm("Why was flight 42 delayed?"))
print(extract_entities_llm("Hey how are you?"))
print(extract_entities_llm("Show multi-leg journey stats"))

