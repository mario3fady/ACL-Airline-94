import time
from huggingface_hub import InferenceClient
import os

HF_TOKEN = os.environ.get("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("❌ HF_TOKEN is not set as environment variable.")

# -----------------------------------------------
# AVAILABLE MODELS (free + fast + works with HF API)
# -----------------------------------------------
AVAILABLE_MODELS = {
    "deepseek": "deepseek-ai/DeepSeek-V3.2",
    "gemma":    "google/gemma-2-2b-it",
    "llama":    "meta-llama/Llama-3.1-8B-Instruct"
}


# -----------------------------------------------
# UNIFIED LLM CALL FUNCTION
# -----------------------------------------------
def run_all_llm(model_name, prompt, max_tokens=300):
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    model_id = AVAILABLE_MODELS[model_name]
    client = InferenceClient(api_key=HF_TOKEN)

    start = time.time()

    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.2
    )

    end = time.time()

    answer = response.choices[0].message["content"]

    return {
        "model": model_name,
        "model_id": model_id,
        "latency_seconds": round(end - start, 3),
        "answer_length": len(answer),
        "answer": answer
    }
