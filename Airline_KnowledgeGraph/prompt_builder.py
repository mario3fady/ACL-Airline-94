import json

def format_context_json(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except:
        return "[]"


def build_structured_prompt(user_query: str, context: dict):

    q = user_query.lower()

    # --------------------------------------------------
    # 1. SIMILARITY QUERIES → USE EMBEDDING RESULTS ONLY
    # --------------------------------------------------
    is_similarity = ("similar" in q or "like" in q) and ("f_" in q or "journey" in q)

    if is_similarity:
        data_rows = context.get("embeddings", [])
    else:
        data_rows = context.get("merged", [])

    context_json = format_context_json(data_rows)

    # --------------------------------------------------
    # 2. Persona
    # --------------------------------------------------
    persona_text = (
        "You are an Airline Knowledge Graph Analytics Assistant. "
        "You answer ONLY using the JSON rows provided inside [KG_DATA]. "
        "Never invent data. Never assume missing values."
    )

    # --------------------------------------------------
    # 3. Task Instructions
    # --------------------------------------------------
    if is_similarity:
        task_text = (
            "The user is asking for JOURNEY SIMILARITY.\n"
            "The rows in [KG_DATA] ARE the similarity results. Each row has:\n"
            "- journey (a journey ID similar to the one asked about)\n"
            "- delay\n"
            "- food\n"
            "- score (cosine similarity)\n\n"
            "IMPORTANT RULES:\n"
            "1. The original journey (e.g., F_1) **WILL NOT** appear in the list.\n"
            "2. Do NOT check whether F_1 exists in the dataset — similarity does not require that.\n"
            "3. Simply return the journeys ranked by score.\n"
            "4. If the list is empty, say no similarity results exist.\n"
        )
    else:
        task_text = (
            "Use ONLY the rows in [KG_DATA] to answer the user's question.\n"
            "Rows may represent:\n"
            "- individual journeys\n"
            "- aggregated metrics (avg_delay, avg_food, journey_count)\n"
            "- flight-level analytics\n\n"
            "RULES:\n"
            "1. Never create data not shown in [KG_DATA].\n"
            "2. Compute averages, best/worst, and counts manually if needed.\n"
            "3. If information is missing, say so.\n"
        )

    # --------------------------------------------------
    # 4. FINAL PROMPT
    # --------------------------------------------------
    prompt = f"""
==============================
[KG_DATA]
{context_json}
==============================

[PERSONA]
{persona_text}

[TASK]
{task_text}

[USER QUESTION]
{user_query}

[ANSWER]
"""
    return prompt.strip()
