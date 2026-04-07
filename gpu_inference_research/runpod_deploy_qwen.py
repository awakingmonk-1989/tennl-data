"""
RunPod Deployment — Qwen 3.5-9B / Qwen 2.5-7B via vLLM Serverless Worker
===========================================================================
Provider  : RunPod (runpod.io)
GPU       : L40S (48GB) recommended | A100 (80GB) for max throughput
Framework : vLLM (via official RunPod vLLM worker)
Billing   : Per-second (serverless) or per-hour (pods)

Two deployment paths:
  A. Serverless Worker (auto-scaling, pay-per-request)
  B. GPU Pod (dedicated, per-hour billing — cheaper for sustained batch)

Setup:
  pip install runpod requests
  export RUNPOD_API_KEY="your_key_here"
"""

# ===========================================================================
# PATH A: SERVERLESS WORKER — Custom handler for vLLM
# ===========================================================================

# --- handler.py (deployed as serverless worker) ---

import runpod
from vllm import LLM, SamplingParams

# Globals — loaded once on cold start
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"  # or Qwen/Qwen3.5-9B-Instruct
llm = None

def load_model():
    global llm
    if llm is None:
        llm = LLM(
            model=MODEL_ID,
            tensor_parallel_size=1,
            gpu_memory_utilization=0.90,
            max_model_len=8192,
            max_num_batched_tokens=16384,
            max_num_seqs=256,
            dtype="bfloat16",
            trust_remote_code=True,
        )
    return llm

def handler(job):
    """
    RunPod serverless handler.
    Input schema:
    {
      "input": {
        "prompts": ["prompt1", "prompt2", ...],
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 0.9,
        "mode": "json"  // optional — lowers temperature for structured output
      }
    }
    """
    job_input = job["input"]
    prompts = job_input.get("prompts", [])
    max_tokens = job_input.get("max_tokens", 4096)
    temperature = job_input.get("temperature", 0.7)
    top_p = job_input.get("top_p", 0.9)
    mode = job_input.get("mode", "text")

    if mode == "json":
        temperature = 0.3
        top_p = 0.95

    model = load_model()
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


# Start the serverless worker
runpod.serverless.start({"handler": handler})


# ===========================================================================
# PATH B: CLIENT SCRIPT — Call RunPod serverless endpoint or Pod API
# ===========================================================================

"""
client_runpod.py — Call the deployed RunPod endpoint from your batch pipeline.
"""

import os
import time
import requests

RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID")  # from RunPod dashboard

BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"
HEADERS = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json",
}


def submit_batch(prompts: list[str], max_tokens: int = 4096, mode: str = "json"):
    """Submit async job to RunPod serverless endpoint."""
    payload = {
        "input": {
            "prompts": prompts,
            "max_tokens": max_tokens,
            "mode": mode,
        }
    }
    resp = requests.post(f"{BASE_URL}/run", json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]


def poll_result(job_id: str, timeout: int = 600, interval: int = 5):
    """Poll for job completion."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{BASE_URL}/status/{job_id}", headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        if data["status"] == "COMPLETED":
            return data["output"]
        elif data["status"] == "FAILED":
            raise RuntimeError(f"Job failed: {data}")
        time.sleep(interval)
    raise TimeoutError(f"Job {job_id} timed out after {timeout}s")


def run_batch_pipeline(all_prompts: list[str], chunk_size: int = 50):
    """
    Process large batch by chunking prompts and submitting parallel jobs.
    For 3M token workload: ~750 prompts @ 4K tokens each.
    """
    job_ids = []
    for i in range(0, len(all_prompts), chunk_size):
        chunk = all_prompts[i : i + chunk_size]
        job_id = submit_batch(chunk)
        job_ids.append(job_id)
        print(f"Submitted chunk {i // chunk_size + 1}: {len(chunk)} prompts → {job_id}")

    # Collect results
    all_results = []
    for jid in job_ids:
        result = poll_result(jid)
        all_results.extend(result["results"])
        print(f"Job {jid}: {len(result['results'])} results collected")

    return all_results


if __name__ == "__main__":
    # Quick test
    test_prompts = [
        "You are a content writer. Write a 500-word article about focus techniques. "
        "Output valid JSON: {title, hook, sections: [{heading, body}], quick_tips: []}",
    ]
    job_id = submit_batch(test_prompts)
    print(f"Job submitted: {job_id}")
    result = poll_result(job_id)
    print(result)
