from router import answer_question
from retrieval import Retriever   



retriever = Retriever(
    uri="bolt://localhost:7687",     
    user="neo4j",                   
    password="airline1234"           
)

questions = [
    "Show me flights from LAX to IAX",
    "Which flights have the worst delays?",
    "How many miles did premier silver passengers fly?",
    "Show multi-leg journey stats",
    "What is the average food rating for each flight?",
    "Flights with more than 2 legs",
    "Which flights carry the most passengers?",
    "Routes between LAX and EWX",
    "How many Gen Z passengers exist?",
    "Flights arriving to IAX",
    "Flights departing from EWX"
]

print("\n=== BASELINE PIPELINE TEST ===\n")

for q in questions:
    print(f"\n--- QUESTION ---\n{q}")
    try:
        answer = answer_question(q)
        print("\n--- ANSWER ---")
        print(answer)
    except Exception as e:
        print("ERROR:", e)
