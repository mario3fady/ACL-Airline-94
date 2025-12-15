import re

FACT_KEYWORDS = {
    "economy", "business", "first",
    "delay", "delays", "minutes",
    "food", "satisfaction",
    "airport", "route", "journey", "flight"
}

def compute_kg_faithfulness_accuracy(answer: str, kg_rows: list) -> float:
    """
    Computes KG-faithfulness accuracy using ONLY factual claims:
    - numbers
    - journey / flight IDs
    - passenger classes
    """

    if not answer or not kg_rows:
        return 0.0

    # -------------------------------
    # 1. Extract KG facts
    # -------------------------------
    kg_numbers = set()
    kg_strings = set()

    for row in kg_rows:
        for v in row.values():
            if isinstance(v, (int, float)):
                kg_numbers.add(str(int(v)))
            elif isinstance(v, str):
                kg_strings.add(v.lower())

    # -------------------------------
    # 2. Extract factual claims from answer
    # -------------------------------
    claimed_numbers = set(re.findall(r"\b\d+\b", answer))

    claimed_classes = {
        w.lower()
        for w in re.findall(r"\b[A-Za-z]+\b", answer)
        if w.lower() in {"economy", "business", "first"}
    }

    claimed_ids = set(re.findall(r"\bF_\d+\b|\b\d{2,4}\b", answer))

    claimed_facts = claimed_numbers | claimed_classes | claimed_ids

    if not claimed_facts:
        return 1.0  # no factual claims → no hallucination

    # -------------------------------
    # 3. Verify claims
    # -------------------------------
    verified = 0

    for fact in claimed_facts:
        if fact in kg_numbers or fact.lower() in kg_strings:
            verified += 1

    return round(verified / len(claimed_facts), 3)
