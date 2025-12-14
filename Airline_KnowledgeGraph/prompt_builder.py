import json


def format_context_json(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return "[]"


def build_structured_prompt(user_query, context):
    """
    This function is intentionally defensive because:
    - router may pass (merged_list, user_question)
    - or (user_question, context_dict)
    We normalize inputs safely without changing the API.
    """

    # --------------------------------------------------
    # 0. NORMALIZE INPUTS (CRITICAL FIX)
    # --------------------------------------------------
    # If user_query is NOT a string, swap arguments
    if not isinstance(user_query, str):
        user_query, context = context, user_query

    # Ensure user_query is a string
    user_query = str(user_query)
    q = user_query.lower()

    # If context is a LIST → wrap it
    if isinstance(context, list):
        context = {
            "merged": context,
            "embeddings": context
        }

    # If context is None or invalid
    if not isinstance(context, dict):
        context = {}

    # --------------------------------------------------
    # 1. SIMILARITY QUERY DETECTION
    # --------------------------------------------------
    is_similarity = (
        ("similar" in q or "like" in q or "closest" in q)
        and ("f_" in q or "journey" in q)
    )

    if is_similarity:
        data_rows = context.get("embeddings", [])
    else:
        data_rows = context.get("merged", [])

    context_json = format_context_json(data_rows)

    # --------------------------------------------------
    # 2. PERSONA
    # --------------------------------------------------
    persona_text = (
        "You are an Airline Knowledge Graph Analytics Assistant. "
        "You answer ONLY using the JSON rows provided inside [KG_DATA]. "
        "Never invent data. Never assume missing values."
    )

    # --------------------------------------------------
    # 3. TASK INSTRUCTIONS
    # --------------------------------------------------
    if is_similarity:
        task_text = (
            "The user is asking for JOURNEY SIMILARITY.\n"
            "The rows in [KG_DATA] ARE the similarity results.\n\n"
            "Each row contains:\n"
            "- journey (similar journey ID)\n"
            "- delay\n"
            "- food\n"
            "- score (cosine similarity)\n\n"
            "RULES:\n"
            "1. Journeys are already ranked by similarity score.\n"
            "2. Do NOT verify existence of the original journey.\n"
            "3. If no rows exist, say no similar journeys were found.\n"
        )
    else:
        task_text = (
            "Use ONLY the rows in [KG_DATA] to answer the user's question.\n"
            "Rows may represent:\n"
            "- individual journeys\n"
            "- aggregated metrics\n"
            "- flight-level analytics\n\n"
            "RULES:\n"
            "1. Never fabricate values.\n"
            "2. Perform calculations only using provided rows.\n"
            "3. If data is insufficient, say so clearly.\n"
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
