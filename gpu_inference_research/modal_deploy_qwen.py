"""
Modal Deployment Script — Qwen 3.5-9B / Qwen 2.5-7B Inference with vLLM
=========================================================================
Provider  : Modal (modal.com)
GPU       : L4 (24GB) or A100 (40GB/80GB)
Framework : vLLM (OpenAI-compatible API)
Billing   : Per-second, serverless auto-scaling

Setup:
  pip install modal
  modal setup          # one-time auth
  modal deploy modal_deploy_qwen.py
"""

import modal

# ---------------------------------------------------------------------------
# 1. Container image — pulls model weights at build time (cached across runs)
# ---------------------------------------------------------------------------
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"       # swap for Qwen/Qwen3.5-9B-Instruct
MODEL_REVISION = "main"
GPU_TYPE = "l4"                                # options: "t4", "l4", "a10g", "a100", "h100"
GPU_COUNT = 1

vllm_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "vllm>=0.7.0",
        "huggingface_hub",
        "hf_transfer",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

app = modal.App("tennl-qwen-inference")

# ---------------------------------------------------------------------------
# 2. Persistent volume — cache model weights across cold starts
# ---------------------------------------------------------------------------
model_volume = modal.Volume.from_name("tennl-model-cache", create_if_missing=True)
MODEL_DIR = "/models"

# ---------------------------------------------------------------------------
# 3. Download function — runs once at image build / first deploy
# ---------------------------------------------------------------------------
@app.function(
    image=vllm_image,
    volumes={MODEL_DIR: model_volume},
    timeout=1800,
)
def download_model():
    from huggingface_hub import snapshot_download
    snapshot_download(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_dir=f"{MODEL_DIR}/{MODEL_ID}",
    )
    model_volume.commit()
    print(f"Model {MODEL_ID} downloaded to {MODEL_DIR}/{MODEL_ID}")

# ---------------------------------------------------------------------------
# 4. vLLM inference class — OpenAI-compatible /v1/completions endpoint
# ---------------------------------------------------------------------------
@app.cls(
    image=vllm_image,
    gpu=modal.gpu.Any(count=GPU_COUNT, memory=24000),  # 24GB for L4/A10G
    volumes={MODEL_DIR: model_volume},
    container_idle_timeout=300,        # keep warm 5 min after last request
    allow_concurrent_inputs=64,        # concurrent requests per container
    scaledown_window=120,              # seconds before scale-to-zero
)
class QwenModel:
    @modal.enter()
    def start_engine(self):
        from vllm import LLM, SamplingParams
        self.llm = LLM(
            model=f"{MODEL_DIR}/{MODEL_ID}",
            tensor_parallel_size=GPU_COUNT,
            gpu_memory_utilization=0.90,
            max_model_len=8192,            # max context window
            max_num_batched_tokens=16384,
            max_num_seqs=256,
            dtype="bfloat16",
            enforce_eager=False,
        )
        self.default_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=4096,
            repetition_penalty=1.05,
        )

    @modal.method()
    def generate(self, prompts: list[str], max_tokens: int = 4096) -> list[dict]:
        """Batch generate — accepts list of prompts, returns list of outputs."""
        from vllm import SamplingParams
        params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=max_tokens,
            repetition_penalty=1.05,
        )
        outputs = self.llm.generate(prompts, params)
        results = []
        for output in outputs:
            results.append({
                "prompt": output.prompt,
                "text": output.outputs[0].text,
                "tokens": len(output.outputs[0].token_ids),
                "finish_reason": output.outputs[0].finish_reason,
            })
        return results

    @modal.method()
    def generate_json(self, prompts: list[str], max_tokens: int = 4096) -> list[dict]:
        """Generate structured JSON output using guided decoding."""
        from vllm import SamplingParams
        params = SamplingParams(
            temperature=0.3,           # lower temp for structured output
            top_p=0.95,
            max_tokens=max_tokens,
            repetition_penalty=1.02,
        )
        outputs = self.llm.generate(prompts, params)
        results = []
        for output in outputs:
            results.append({
                "prompt": output.prompt,
                "text": output.outputs[0].text,
                "tokens": len(output.outputs[0].token_ids),
            })
        return results

# ---------------------------------------------------------------------------
# 5. Batch runner — process multiple articles in parallel
# ---------------------------------------------------------------------------
@app.function(image=vllm_image, timeout=3600)
def run_batch(prompt_list: list[str], batch_size: int = 50):
    """
    Run batch inference for content generation.
    Splits prompt_list into chunks and sends to vLLM.
    """
    model = QwenModel()
    all_results = []

    for i in range(0, len(prompt_list), batch_size):
        batch = prompt_list[i : i + batch_size]
        results = model.generate.remote(batch, max_tokens=4096)
        all_results.extend(results)
        print(f"Batch {i // batch_size + 1}: processed {len(batch)} prompts")

    return all_results

# ---------------------------------------------------------------------------
# 6. Local entrypoint — test from CLI
# ---------------------------------------------------------------------------
@app.local_entrypoint()
def main():
    """Run: modal run modal_deploy_qwen.py"""
    # Step 1: ensure model is downloaded
    download_model.remote()

    # Step 2: test single generation
    model = QwenModel()
    test_prompts = [
        "You are a content writer for an Indian lifestyle platform. "
        "Write a 500-word article about morning routines that boost focus. "
        "Output ONLY valid JSON with keys: title, hook, sections (array of {heading, body}), quick_tips (array).",
    ]
    results = model.generate_json.remote(test_prompts, max_tokens=4096)
    for r in results:
        print(f"Tokens: {r['tokens']}")
        print(r["text"][:2000])

    # Step 3: test batch
    batch_prompts = [f"Write a short tip about topic #{i}" for i in range(10)]
    batch_results = run_batch.remote(batch_prompts, batch_size=5)
    print(f"Batch complete: {len(batch_results)} results")
