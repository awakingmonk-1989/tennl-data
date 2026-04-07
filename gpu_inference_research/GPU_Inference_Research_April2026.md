# GPU Inference Research — On-Demand Cloud Providers for Content Generation
### Tennl Platform | April 2026 | Batch Workload: ~3M Output Tokens

---

## 1. Executive Summary

- **Workload**: ~3M output tokens, 2K–4K tokens per request, structured JSON output
- **Best Model**: **Qwen 2.5-7B-Instruct** (proven) or **Qwen 3.5-9B-Instruct** (latest, March 2026)
- **Best Cost Setup**: RunPod L40S Pod → **$0.21 total** for 3M tokens (~16 min)
- **Best Speed Setup**: H100 (Hyperbolic/RunPod) → **$0.10 total** (~4 min)
- **Best No-Ops**: Together AI API → **$0.54 total** (~5 min, zero infra)

---

## 2. Model Selection

### 2.1 Hard Requirements Checklist

| Requirement | Qwen 3.5-9B | Qwen 2.5-7B | Mistral NeMo 12B | Gemma 2-9B | Phi-4-mini 3.8B |
|---|---|---|---|---|---|
| Commercial license (Apache 2.0 / MIT) | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 | MIT |
| Structured JSON output | Excellent | Excellent | Good | Good | Good |
| Multilingual (Indian langs) | Hindi, Tamil, Telugu + 20 | 29+ langs incl Hindi, Tamil, Telugu | 100+ langs incl Hindi | English-focused | 20+ langs |
| Content safety / guardrails | Strong | Strong | Strong | Very strong | Good |
| 2K–4K token output | Yes (128K ctx) | Yes (128K ctx) | Yes (128K ctx) | Yes (128K ctx) | Yes (64K ctx) |
| Complex instruction following | Excellent | Excellent | Excellent | Excellent | Exceptional |
| No thinking overhead | Yes | Yes | Yes | Yes | Yes |
| ≤ 9B parameters | 9B | 7B | 12B (slightly over) | 9B | 3.8B |
| vLLM compatible | Yes | Yes | Yes | Yes | Yes |

### 2.2 Top 3 Recommended Models (Ranked)

**1. Qwen 2.5-7B-Instruct** — `Qwen/Qwen2.5-7B-Instruct`
- Battle-tested, production-ready, best-in-class JSON generation
- 7B fits comfortably on any 24GB+ GPU even at FP16
- 29+ languages including Hindi, Tamil, Telugu
- Apache 2.0 — zero commercial restrictions

**2. Qwen 3.5-9B-Instruct** — `Qwen/Qwen3.5-9B-Instruct`
- Latest release (March 2, 2026), improved instruction following
- 128K context, improved structured output capabilities
- Apache 2.0, strong multilingual including Indian languages
- Slightly higher VRAM requirement than 2.5-7B

**3. Mistral NeMo 12B** — `mistralai/Mistral-Nemo-Instruct-2407`
- 100+ language training (best multilingual coverage)
- Apache 2.0, function calling support
- 12B → needs 4-bit quantization for 24GB GPUs
- Excellent for content needing diverse language support

### 2.3 Models NOT Recommended

| Model | Reason |
|---|---|
| Llama 3.2 (1B/3B) | Custom license — not Apache 2.0, commercial terms need legal review |
| DeepSeek-V3 | License ambiguity for commercial use |
| GLM-5 | License unverified for commercial use |
| Gemma 3-27B | Exceeds 9B parameter budget (27B) |
| Phi-4 (14B) | Exceeds 9B parameter budget |

### 2.4 Quantization Options (VRAM vs Quality)

| Format | VRAM (7B) | VRAM (9B) | Quality Loss | Recommended For |
|---|---|---|---|---|
| FP16 / BF16 | ~16 GB | ~20 GB | None | A100 80GB, H100 |
| INT8 (GPTQ) | ~8 GB | ~10 GB | Minimal | L40S, A100 40GB |
| INT4 (AWQ) | ~5 GB | ~6 GB | Small | L4 (24GB), A10G |
| GGUF Q4_K_M | ~5 GB | ~6.5 GB | Small | L4, T4 (limited) |

---

## 3. Cloud Provider Comparison

### 3.1 Provider Overview

| Feature | Modal | Cerebrium | RunPod | Together AI | Hyperbolic |
|---|---|---|---|---|---|
| **Billing model** | Per-second | Per-second | Per-second (serverless) / Per-hour (pod) | Per-token (API) / Per-hour (dedicated) | Per-hour |
| **Cold start** | ~10s (with snapshots) | 2–4s (fastest) | 5–15s (serverless) | N/A (API) | N/A |
| **Scale to zero** | Yes | Yes | Yes (serverless) | N/A | No |
| **Auto-scaling** | Plan-based | Automatic | Serverless only | Built-in | No |
| **Docker support** | Custom images | Custom images | Docker + templates | N/A | No |
| **vLLM support** | Yes | Yes | Yes (official templates) | Managed | No |
| **Egress fees** | Yes | Yes | Zero | Zero | N/A |
| **Free credits** | $30 starter | Limited | $25 starter | Free tier | No |
| **Best for** | Dev experience, prototyping | Fast cold starts, production | Batch workloads (pods) | Zero-ops API | Cheapest GPU/hr |

### 3.2 GPU Pricing by Provider (Per Hour)

| GPU | VRAM | Modal | Cerebrium | RunPod (Pod) | RunPod (Serverless) | Together AI | Hyperbolic |
|---|---|---|---|---|---|---|---|
| T4 | 16 GB | $0.59 | $0.59 | $0.40 | — | — | — |
| L4 | 24 GB | $0.73 | — | $0.44 | — | — | — |
| A10G | 24 GB | $1.10 | $0.70 | $0.50 | — | — | — |
| L40S | 48 GB | $1.65 | $1.25 | $0.79 | $4.79 (active) | — | — |
| A100 40GB | 40 GB | $2.78 | $2.10 | $1.64 | — | — | — |
| A100 80GB | 80 GB | $3.73 | $3.15 | $2.49 | — | $3.49 | — |
| H100 | 80 GB | $4.89 | $4.25 | $3.99 | — | $3.49 | $1.49 |

### 3.3 API Provider Pricing (Per 1M Output Tokens)

| Provider | Model | Price / 1M Output Tokens | Notes |
|---|---|---|---|
| Together AI | Qwen 2.5-7B Turbo | $0.18–0.30 | Cheapest managed API |
| Fireworks AI | Qwen 2.5-7B | $0.20–0.50 | Fast inference |
| DeepSeek API | DeepSeek V3 | $0.14–0.28 | Cheapest overall but license concerns |

---

## 4. GPU Configuration for 7B–9B Models

### 4.1 Recommended GPU per Quantization

| Model Size | Quantization | Min GPU | Recommended GPU | Throughput (tok/s) |
|---|---|---|---|---|
| 7B | BF16 | A100 40GB | L40S / A100 80GB | 2,500–3,500 |
| 7B | INT4 (AWQ) | L4 / A10G (24GB) | L40S | 2,000–3,100 |
| 9B | BF16 | A100 40GB | L40S / A100 80GB | 2,000–3,000 |
| 9B | INT4 (AWQ) | L4 / A10G (24GB) | L40S | 1,800–2,800 |

### 4.2 vLLM Optimal Configuration

```bash
# Single L40S — Qwen 2.5-7B (BF16)
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --max-num-batched-tokens 16384 \
  --max-num-seqs 256 \
  --dtype bfloat16 \
  --enable-chunked-prefill \
  --port 8000

# Single L4/A10G — Qwen 2.5-7B (AWQ 4-bit)
vllm serve Qwen/Qwen2.5-7B-Instruct-AWQ \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 128 \
  --quantization awq \
  --dtype float16 \
  --enable-chunked-prefill \
  --port 8000
```

### 4.3 Key vLLM Parameters

| Parameter | Value | Effect |
|---|---|---|
| `gpu_memory_utilization` | 0.85–0.95 | Higher = more KV cache = more concurrent requests |
| `max_num_batched_tokens` | 8192–16384 | Total tokens per batch iteration |
| `max_num_seqs` | 128–512 | Max concurrent sequences |
| `enable_chunked_prefill` | true | Batch prefill with decode for better throughput |
| `max_model_len` | 8192 | Keep low if outputs are 2K–4K (saves VRAM) |
| `dtype` | bfloat16 | Best for Ampere/Hopper GPUs |

---

## 5. Cost Analysis — 3M Token Workload

### 5.1 Self-Hosted GPU (Pod / Dedicated)

| Setup | GPU Cost/hr | Throughput | Time for 3M | Total Cost | Cost/1M Tokens |
|---|---|---|---|---|---|
| RunPod L40S Pod | $0.79 | ~3,100 tok/s | ~16 min | **$0.21** | $0.07 |
| RunPod A100 80GB Pod | $2.49 | ~3,500 tok/s | ~14 min | **$0.58** | $0.19 |
| Hyperbolic H100 | $1.49 | ~10,000 tok/s | ~5 min | **$0.12** | $0.04 |
| Modal L40S | $1.65 | ~3,100 tok/s | ~16 min | **$0.44** | $0.15 |
| Cerebrium L40S | $1.25 | ~3,100 tok/s | ~16 min | **$0.33** | $0.11 |
| Lambda H100 (reserved) | $1.89 | ~10,000 tok/s | ~5 min | **$0.16** | $0.05 |

### 5.2 Serverless (Pay-Per-Use)

| Setup | Active Rate | Time for 3M | Total Cost | Cost/1M Tokens |
|---|---|---|---|---|
| RunPod L40S Serverless | $4.79/hr | ~16 min | **$1.28** | $0.43 |
| Modal L40S (auto-scale) | $1.65/hr + overhead | ~18 min | **$0.55** | $0.18 |
| Cerebrium A10 | $0.70/hr + overhead | ~25 min | **$0.35** | $0.12 |

### 5.3 Managed API (Zero Infrastructure)

| Provider | Rate | Total Cost (3M) | Time |
|---|---|---|---|
| Together AI (Qwen 2.5-7B) | $0.18–0.30/1M | **$0.54–$0.90** | <5 min |
| Fireworks AI | $0.20–0.50/1M | **$0.60–$1.50** | <5 min |

### 5.4 Winner Summary

| Priority | Best Option | Cost for 3M | Time |
|---|---|---|---|
| **Cheapest** | Hyperbolic H100 | $0.12 | 5 min |
| **Best value** | RunPod L40S Pod | $0.21 | 16 min |
| **Fastest** | H100 (Hyperbolic/Lambda) | $0.12–0.16 | 4–5 min |
| **Zero ops** | Together AI API | $0.54 | <5 min |
| **Best DX** | Modal L40S | $0.44 | 16 min |
| **Best cold start** | Cerebrium | $0.33 | 16 min |

---

## 6. Deployment Strategy Recommendations

### 6.1 For Tennl Batch Workloads (Recommended Path)

**Option A: RunPod Pod + vLLM (Best Cost)**
- Provision L40S pod on-demand ($0.79/hr)
- Deploy vLLM via Docker (see `docker-compose-vllm.yml`)
- Run batch, terminate pod
- Cost: ~$0.21 per 3M tokens
- Files: `runpod_deploy_qwen.py`, `runpod_Dockerfile`

**Option B: Modal Serverless (Best DX)**
- Deploy via `modal deploy modal_deploy_qwen.py`
- Auto-scales, auto-shuts-down, per-second billing
- No Docker management needed
- Cost: ~$0.44 per 3M tokens
- File: `modal_deploy_qwen.py`

**Option C: Together AI API (Fastest to Start)**
- Zero deployment, just API calls
- `curl https://api.together.xyz/v1/chat/completions ...`
- Cost: ~$0.54 per 3M tokens
- Best for: testing, low-volume, prototyping

### 6.2 Batch Processing Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Batch Queue │ ──▶ │  vLLM Server │ ──▶ │ JSON Output │
│  (prompts)   │     │  (L40S GPU)  │     │  (articles) │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │
       │  chunk_size=50     │  max_tokens=4096
       │  concurrent=4      │  temperature=0.3 (JSON)
       └────────────────────┘
```

- Chunk prompts into batches of 50
- vLLM handles internal batching (max_num_seqs=256)
- 4 concurrent API callers for pipeline saturation
- Estimated throughput: 750 articles @ 4K tokens each = 3M tokens

---

## 7. Delivered Files

| File | Purpose |
|---|---|
| `modal_deploy_qwen.py` | Complete Modal deployment — download, serve, batch runner, test entrypoint |
| `runpod_deploy_qwen.py` | RunPod serverless handler + client script for batch pipeline |
| `runpod_Dockerfile` | Docker image for RunPod serverless worker with vLLM |
| `cerebrium_deploy_qwen.py` | Cerebrium deployment config + inference function + client example |
| `docker-compose-vllm.yml` | Self-hosted vLLM on any GPU pod (RunPod/Lambda/bare metal) |

---

## 8. Quick Start Decision Tree

```
Need 3M tokens processed?
│
├─ Budget < $0.25 → RunPod L40S Pod ($0.21, 16 min)
├─ Budget < $0.15 → Hyperbolic H100 ($0.12, 5 min)
├─ Want zero infra → Together AI API ($0.54, 5 min)
├─ Want best DX   → Modal ($0.44, 16 min)
├─ Need fast cold starts → Cerebrium ($0.33, 16 min)
└─ Running daily batches → RunPod L40S Pod (cheapest at scale)
```

---

## 9. Model Licensing — Commercial Use Verification

| Model | License | Commercial Use | Restrictions | Source |
|---|---|---|---|---|
| Qwen 2.5-7B-Instruct | Apache 2.0 | 100% free | None | huggingface.co/Qwen/Qwen2.5-7B-Instruct |
| Qwen 3.5-9B-Instruct | Apache 2.0 | 100% free | None | huggingface.co/Qwen/Qwen3.5-9B-Instruct |
| Mistral NeMo 12B | Apache 2.0 | 100% free | None | mistral.ai |
| Gemma 2-9B-IT | Apache 2.0 | 100% free | None | huggingface.co/google/gemma-2-9b-it |
| Phi-4-mini | MIT | 100% free | None | huggingface.co/microsoft/phi-4-mini |

All recommended models are **Apache 2.0 or MIT licensed** — fully cleared for commercial use with zero restrictions on output, redistribution, or modification.

---

## 10. Sources

- Modal Pricing: modal.com/pricing
- Cerebrium Pricing: cerebrium.ai/pricing
- RunPod Pricing: runpod.io/pricing
- Together AI Pricing: together.ai/pricing
- Hyperbolic: hyperbolic.xyz
- Lambda Labs: lambda.ai/pricing
- Qwen 3.5 Announcement: venturebeat.com — Alibaba Qwen 3.5 (March 2026)
- vLLM Docs: docs.vllm.ai/en/stable/configuration/optimization/
- HuggingFace Model Cards: huggingface.co/Qwen, huggingface.co/google, huggingface.co/mistralai
- GPU Benchmarks: koyeb.com/docs/hardware/gpu-benchmarks
- LLM Stats: llm-stats.com/benchmarks
