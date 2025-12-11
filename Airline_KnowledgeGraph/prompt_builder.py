import json

def format_context_for_prompt(context):
    """
    Convert the merged KG results into a readable structured text
    for the LLM to consume.
    """

    merged = context.get("merged", [])

    if not merged:
        return "No relevant KG facts were found."

    lines = ["Here are facts retrieved from the Airline Knowledge Graph:"]

    for r in merged:
        line = []

        # ---------------- FIXED GENERATION HANDLING ----------------
        if "generation" in r:
            line.append(f"Generation: {r.get('generation')}")
            line.append(f"Avg Food Score: {r.get('avg_food')}")
            line.append(f"Avg Delay: {r.get('avg_delay')} minutes")
            line.append(f"Journeys Count: {r.get('journey_count')}")
            lines.append(" - " + " | ".join(line))
            continue
        # ------------------------------------------------------------

        # Normal journey / flight rows
        if "journey" in r and r["journey"] is not None:
            line.append(f"Journey ID: {r['journey']}")

        if "flight" in r:
            line.append(f"Flight Number: {r['flight']}")

        if "origin" in r:
            line.append(f"Origin Airport: {r['origin']}")

        if "destination" in r:
            line.append(f"Destination Airport: {r['destination']}")

        if "delay" in r:
            line.append(f"Arrival Delay: {r['delay']} minutes")

        if "food_score" in r:
            line.append(f"Food Score: {r['food_score']}")

        if "food" in r:
            line.append(f"Food Score: {r['food']}")

        if "score" in r and r["score"] is not None:
            line.append(f"Similarity Score: {r['score']:.4f}")

        lines.append(" - " + " | ".join(line))

    return "\n".join(lines)


def build_structured_prompt(user_query, context):
    """
    Builds the 3-part structured prompt required by Milestone 3.b:
    - CONTEXT
    - PERSONA
    - TASK
    """
    print("totoooo")
    
    context_text = format_context_for_prompt(context)

    persona_text = (
        "You are an Airline Knowledge Graph Assistant. "
        "You specialize in analyzing flight routes, delays, satisfaction scores, "
        "and journey statistics using accurate factual data from the KG."
    )

    task_text = (
        "Your job is to answer the user's question using ONLY the facts provided "
        "in the context above. "
        "Do NOT hallucinate or add extra information. "
        "If the context does not contain enough information, say so explicitly."
        "If the user asks about how many times a passenger has flied you have to manually calculate it using all available flights you have in the data"
        "If the user asks about most/least freequent flyer 'generation' you have to manually calculate by seeing how many unique rows the same 'generation' is in "
        "If the user asks about most/least freequent flyer you have to manually calculate by seeing how many unique 'Took' relationships between each 'Passenger' node and  'Journey'"
           
    )

    prompt = f"""
[CONTEXT]
{context_text}

[PERSONA]
{persona_text}

[TASK]
{task_text}

[USER QUESTION]
{user_query}

[ANSWER]
"""

    return prompt.strip()
