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

    # 1. Convert KG results to readable text
    context_text = format_context_for_prompt(context)

    # 2. Persona
    persona_text = (
        "You are an Airline Knowledge Graph Assistant. "
        "You specialize in analyzing flight routes, delays, satisfaction scores, "
        "and journey statistics using accurate factual data from the KG."
    )

    # 3. Task instructions
    task_text = (
        "Your job is to answer the user's question using ONLY the facts provided "
        "in the context above. "
        "Do NOT hallucinate or add extra information. "
        "If the context does not contain enough information, say so explicitly."
    )

    # FINAL STRUCTURED PROMPT
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
