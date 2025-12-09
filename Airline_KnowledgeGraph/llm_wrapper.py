from huggingface_hub import InferenceClient
import os

HF_TOKEN = os.environ.get("HF_TOKEN")

client = InferenceClient(api_key=HF_TOKEN)

MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"   # can change later


def run_llm(prompt):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )
    return response.choices[0].message["content"]
