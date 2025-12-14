from router import answer_question


print("🛫 Airline KG Assistant — Baseline Mode")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("> ")
    
    if user_input.lower() == "exit":
        break

    try:
        answer = answer_question(
            user_input
        )
        print("Answer:", answer)
    except Exception as e:
        print("Error:", e)
