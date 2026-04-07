"""
Cerebrium Deployment — Qwen 3.5-9B / Qwen 2.5-7B Inference
=============================================================
Provider  : Cerebrium (cerebrium.ai)
GPU       : A10 (24GB) or L40S (48GB)
Framework : vLLM
Billing   : Per-second, auto-scaling, fast cold starts (2-4s)

Setup:
  pip install cerebrium
  cerebrium login
  cerebrium init tennl-qwen-inference
  cd tennl-qwen-inference
  # Copy this file as main.py
  cerebrium deploy
"""

# ---------------------------------------------------------------------------
# cerebrium.toml — Project configuration (place in project root)
# ---------------------------------------------------------------------------
CEREBRIUM_TOML = """
[cerebrium.deployment]
name = "tennl-qwen-inference"
python_version = "3.11"
include = "[./*, main.py]"
docker_base_image_url = "nvidia/cuda:12.4.1-devel-ubuntu22.04"

[cerebrium.hardware]
gpu = "AMPERE_A10"          # options: AMPERE_A10, L40S, A100_40GB, A100_80GB, H100
gpu_count = 1
cpu = 4
memory = 16.0               # GB RAM

[cerebrium.scaling]
min_replicas = 0             # scale to zero when idle
max_replicas = 5             # max concurrent instances
cooldown = 300               # seconds before scale-down

[cerebrium.dependencies.pip]
vllm = ">=0.7.0"
huggingface_hub = "latest"
hf_transfer = "latest"
"""

# ---------------------------------------------------------------------------
# main.py — Cerebrium serverless function
# ---------------------------------------------------------------------------

from typing import Optional
from vllm import LLM, SamplingParams

# Model config
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"  # or Qwen/Qwen3.5-9B-Instruct

# Global model instance — loaded once per container
_llm: Optional[LLM] = None


def get_model() -> LLM:
    global _llm
    if _llm is None:
        _llm = LLM(
            model=MODEL_ID,
            tensor_parallel_size=1,
            gpu_memory_utilization=0.90,
            max_model_len=8192,
            max_num_batched_tokens=16384,
            max_num_seqs=256,
            dtype="bfloat16",
            trust_remote_code=True,
        )
    return _llm


def generate(
    prompts: list[str],
    max_tokens: int = 4096,
    temperature: float = 0.7,
    top_p: float = 0.9,
    mode: str = "text",
) -> dict:
    """
    Main inference endpoint.

    Args:
        prompts: List of prompt strings
        max_tokens: Max output tokens per prompt (default 4096)
        temperature: Sampling temperature (default 0.7; 0.3 for JSON mode)
        top_p: Nucleus sampling (default 0.9)
        mode: "text" or "json" (json lowers temperature automatically)

    Returns:
        dict with "results" list
    """
    if mode == "json":
        temperature = 0.3
        top_p = 0.95

    model = get_model()
    params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        repetition_penalty=1.05,
    )

    outputs = model.generate(prompts, params)
    results = []
    for output in outputs:
        results.append({
            "text": output.outputs[0].text,
            "tokens": len(output.outputs[0].token_ids),
            "finish_reason": output.outputs[0].finish_reason,
        })

    return {"results": results}


def generate_json(prompts: list[str], max_tokens: int = 4096) -> dict:
    """Convenience wrapper for structured JSON output."""
    return generate(prompts, max_tokens=max_tokens, mode="json")


# ---------------------------------------------------------------------------
# Client script — call Cerebrium endpoint from batch pipeline
# ---------------------------------------------------------------------------
"""
client_cerebrium.py

import requests

CEREBRIUM_API_KEY = "your_api_key"
ENDPOINT_URL = "https://api.cerebrium.ai/v4/p-xxxx/tennl-qwen-inference/generate"

headers = {
    "Authorization": f"Bearer {CEREBRIUM_API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "prompts": [
        "Write a 500-word article about morning routines. "
        "Output JSON: {title, hook, sections: [{heading, body}], tips: []}"
    ],
    "max_tokens": 4096,
    "mode": "json",
}

resp = requests.post(ENDPOINT_URL, json=payload, headers=headers)
print(resp.json())
"""
