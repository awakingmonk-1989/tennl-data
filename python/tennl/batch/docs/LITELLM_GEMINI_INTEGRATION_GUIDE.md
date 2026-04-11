# LiteLLM + Google Gemini Integration Guide
## For LlamaIndex-based Insight Card Orchestrator

**Version:** 1.0  
**Date:** April 8, 2026  
**Target System:** `python/tennl/batch/src/tennl/batch/generator/insight_cards/insight_card_llamaindex_orchestrator.py`

---

## Table of Contents

1. [Overview](#overview)
2. [LiteLLM Installation](#litellm-installation)
3. [Google Gemini API Setup](#google-gemini-api-setup)
4. [LlamaIndex + LiteLLM Integration](#llamaindex--litellm-integration)
5. [Token Tracking & Logging](#token-tracking--logging)
6. [Implementation Recommendations](#implementation-recommendations)
7. [Code Examples](#code-examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers integrating **LiteLLM** as a provider for the insight card batch job, using **Google Gemini** models via **LlamaIndex**. LiteLLM provides a unified interface to 140+ LLM providers with built-in token tracking, cost calculation, and retry logic.

### Why LiteLLM?

- **Unified API**: Single OpenAI-compatible interface for all providers
- **Built-in Token Tracking**: Automatic token counting and cost calculation
- **Provider Flexibility**: Easy switching between Gemini, OpenAI, Anthropic, etc.
- **Retry Logic**: Automatic retries with exponential backoff
- **Cost Optimization**: Real-time cost tracking per request

---

## LiteLLM Installation

### System Requirements

- Python 3.13 (as per your project requirements)
- `uv` package manager (already in use)

### Installation Steps

```bash
# Navigate to your project directory
cd /Users/devansh/tennl-data/python/tennl/batch

# Install LiteLLM using uv
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv pip install litellm

# Install LlamaIndex LiteLLM integration
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv pip install llama-index-llms-litellm

# Verify installation
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run python -c "import litellm; print(litellm.__version__)"
```

### Dependencies

LiteLLM will automatically install:
- `openai` (for OpenAI-compatible interface)
- `tiktoken` (for token counting)
- `requests` (for HTTP calls)
- `python-dotenv` (for environment variables)

---

## Google Gemini API Setup

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Click **"Get API key"** or **"Create API key"**
4. Choose to create an API key in an existing project or create a new one
5. Click **"Create API key in new project"** (or select existing)
6. Copy the generated API key immediately (it's only shown once)

### Step 2: Enable Required APIs (if needed)

If you encounter permission issues:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services > Library**
4. Search for **"Generative Language API"**
5. Click **Enable**

### Step 3: Set Environment Variable

```bash
# Add to your .env file or export directly
export GEMINI_API_KEY="your-api-key-here"

# Or add to your .env file in python/tennl/batch/
echo "GEMINI_API_KEY=your-api-key-here" >> python/tennl/batch/.env
```

### Available Gemini Models (April 2026)

| Model Name | Status | Best For | Context Window | Cost (per 1M tokens) |
|------------|--------|----------|----------------|----------------------|
| `gemini-3-flash` | **Stable (GA)** | **RECOMMENDED** - Fast, balanced | 1M tokens | Input: $0.50, Output: $1.50 |
| `gemini-3.1-flash-lite-preview` | Preview | Highest throughput, lowest cost | 1M tokens | Input: $0.25, Output: $1.50 |
| `gemini-3.1-pro-preview` | Preview | Most capable reasoning | 2M tokens | Input: $1.25, Output: $5.00 |
| `gemini-2.5-flash` | Stable | Legacy, still supported | 1M tokens | Input: $0.075, Output: $0.30 |
| `gemini-2.5-pro` | Stable | Legacy, complex reasoning | 2M tokens | Input: $1.25, Output: $5.00 |

**Important Notes:**
- **Gemini 3 Flash** is now the default stable model (GA since December 2025)
- **Gemini 3 Pro Preview** was deprecated March 9, 2026 → Use `gemini-3.1-pro-preview` instead
- **Gemini 3.1 Flash-Lite** launched March 3, 2026 - fastest and cheapest option
- Preview models have no shutdown date announced but may have rate limits

**Recommendation for Insight Cards:** Use `gemini/gemini-3-flash` (stable, production-ready) or `gemini/gemini-3.1-flash-lite-preview` (cheapest, fastest).

---

## LlamaIndex + LiteLLM Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  insight_card_llamaindex_orchestrator.py                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LlamaIndex LiteLLM Wrapper                          │   │
│  │  - Handles structured output (InsightCard)           │   │
│  │  - Manages chat messages                             │   │
│  │  - Provides token counting callbacks                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LiteLLM Core                                        │   │
│  │  - Unified API interface                             │   │
│  │  - Token tracking & cost calculation                 │   │
│  │  - Retry logic & error handling                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Google Gemini API                                   │   │
│  │  - Model inference                                   │   │
│  │  - Returns usage metadata                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Basic Integration Pattern

```python
from llama_index.llms.litellm import LiteLLM
from llama_index.core.llms import ChatMessage
import os

# Set API key
os.environ["GEMINI_API_KEY"] = "your-api-key"

# Initialize LiteLLM with Gemini
llm = LiteLLM(
    model="gemini/gemini-3-flash",  # Stable GA model (recommended)
    temperature=0.7,
    max_tokens=1024,
)

# Use with structured output
structured_llm = llm.as_structured_llm(output_cls=InsightCard)

# Make a request
messages = [
    ChatMessage(role="system", content="You are a helpful assistant."),
    ChatMessage(role="user", content="Generate an insight card about productivity.")
]

response = structured_llm.chat(messages)
```

---

## Token Tracking & Logging

### Option 1: LlamaIndex TokenCountingHandler (RECOMMENDED)

**Best for:** Comprehensive tracking across multiple LLM calls, embedding operations, and query engines.

```python
import tiktoken
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core import Settings
from llama_index.llms.litellm import LiteLLM

# Initialize token counter
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode,
    verbose=True,  # Print token usage to console
)

# Set up callback manager
Settings.callback_manager = CallbackManager([token_counter])

# Initialize LLM
llm = LiteLLM(model="gemini/gemini-2.0-flash")

# Make requests...
response = llm.chat(messages)

# Access token counts
print(f"Prompt tokens: {token_counter.prompt_llm_token_count}")
print(f"Completion tokens: {token_counter.completion_llm_token_count}")
print(f"Total tokens: {token_counter.total_llm_token_count}")

# Reset for next batch
token_counter.reset_counts()
```

**Pros:**
- Tracks tokens across entire LlamaIndex pipeline
- Supports embedding token counting
- Persistent across multiple calls
- Can be reset per batch

**Cons:**
- Requires callback setup
- Uses approximate tokenization (tiktoken)

---

### Option 2: LiteLLM Response Metadata (RECOMMENDED FOR YOUR USE CASE)

**Best for:** Per-request token tracking with exact provider-reported counts.

```python
from llama_index.llms.litellm import LiteLLM
from llama_index.core.llms import ChatMessage

llm = LiteLLM(model="gemini/gemini-3-flash")
response = llm.chat(messages)

# Access token counts from response.additional_kwargs
token_usage = response.additional_kwargs
print(f"Prompt tokens: {token_usage.get('prompt_tokens', 0)}")
print(f"Completion tokens: {token_usage.get('completion_tokens', 0)}")
print(f"Total tokens: {token_usage.get('total_tokens', 0)}")

# Access raw response for complete metadata
raw_response = response.raw
print(f"Raw usage: {raw_response.get('usage', {})}")
print(f"Model: {raw_response.get('model', '')}")
print(f"Response ID: {raw_response.get('id', '')}")

# All metadata fields available in response.raw:
# - id: unique response identifier
# - model: model name used
# - created: timestamp
# - usage: {prompt_tokens, completion_tokens, total_tokens}
# - choices: array with message content
# - system_fingerprint: model version fingerprint
```

**Pros:**
- ✅ Exact token counts from provider (not estimated)
- ✅ No additional setup required (no callbacks needed)
- ✅ Available in `response.additional_kwargs` and `response.raw`
- ✅ Includes complete metadata (model, id, timestamps)
- ✅ Works with structured output

**Cons:**
- Per-request only (not cumulative)
- Requires manual aggregation for batch tracking

---

### Option 3: LiteLLM Cost Tracking

**Best for:** Cost monitoring and budget management.

```python
from litellm import completion_cost
from llama_index.llms.litellm import LiteLLM

llm = LiteLLM(model="gemini/gemini-2.0-flash")
response = llm.chat(messages)

# Calculate cost using LiteLLM
cost = completion_cost(completion_response=response.raw)
formatted_cost = f"${float(cost):.10f}"
print(f"Request cost: {formatted_cost}")

# Or access from hidden params (if available)
if hasattr(response, '_hidden_params'):
    cost = response._hidden_params.get("response_cost", 0)
    print(f"Response cost: ${cost:.10f}")
```

---

### Option 4: Hybrid Approach (BEST PRACTICE)

Combine LlamaIndex callbacks for cumulative tracking with per-request metadata for detailed logging.

```python
import tiktoken
import json
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core import Settings
from llama_index.llms.litellm import LiteLLM
from litellm import completion_cost

# Setup token counter for cumulative tracking
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode,
    verbose=False,  # We'll log manually
)
Settings.callback_manager = CallbackManager([token_counter])

# Initialize LLM
llm = LiteLLM(model="gemini/gemini-2.0-flash")

# Track per-request
request_logs = []

def log_request(response, card_index: int):
    """Log detailed token usage for each request"""
    token_usage = response.additional_kwargs
    cost = completion_cost(completion_response=response.raw)
    
    log_entry = {
        "card_index": card_index,
        "model": "gemini-2.0-flash",
        "prompt_tokens": token_usage.get('prompt_tokens', 0),
        "completion_tokens": token_usage.get('completion_tokens', 0),
        "total_tokens": token_usage.get('total_tokens', 0),
        "cost_usd": float(cost),
        "timestamp": datetime.utcnow().isoformat()
    }
    request_logs.append(log_entry)
    return log_entry

# Make requests
for i in range(count):
    response = llm.chat(messages)
    log_entry = log_request(response, i)
    logger.info(f"Card {i}: {log_entry['total_tokens']} tokens, ${log_entry['cost_usd']:.6f}")

# Summary
print(f"\nBatch Summary:")
print(f"Total LLM tokens (cumulative): {token_counter.total_llm_token_count}")
print(f"Total requests: {len(request_logs)}")
print(f"Total cost: ${sum(log['cost_usd'] for log in request_logs):.6f}")

# Save detailed logs
with open("token_usage_log.json", "w") as f:
    json.dump(request_logs, f, indent=2)
```

---

## Implementation Recommendations

### Recommended Approach for Your Orchestrator

Based on your current architecture, here's the recommended implementation:

#### 1. Update `InsightCardResult` Model

First, extend the model to include metadata:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class InsightCardResult(BaseModel):
    title: str
    category: str
    content: str
    tone: str
    emotional_register: str
    title_style: str
    hook_type: str
    opening_word_class: str
    provider: str
    raw: str
    error: Optional[str] = None
    
    # Add metadata field for token tracking
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

#### 2. Update `generate_one_card` Function

```python
import time

def generate_one_card(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    variables: dict,
    provider_name: str,
    dry_run: bool,
) -> InsightCardResult:
    """
    Builds a fresh structured LLM and sends one isolated chat request.
    Captures all metadata including token usage.
    """
    system_prompt = render_prompt(system_prompt_tpl, variables)
    user_prompt = render_prompt(user_prompt_tpl, variables)

    if dry_run:
        preview = f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}"
        return InsightCardResult(
            title="[DRY RUN]",
            category=variables.get("category", ""),
            content="",
            tone=variables.get("tone", ""),
            emotional_register=variables.get("emotional_register", ""),
            title_style=variables.get("title_style", ""),
            hook_type=variables.get("hook_type", ""),
            opening_word_class=variables.get("opening_word_class", ""),
            provider=provider_name,
            raw=preview,
            error=None,
            metadata={}
        )

    response = None
    raw_text = ""
    
    try:
        structured_llm = llm.as_structured_llm(output_cls=InsightCard)
        response = structured_llm.chat(_build_messages(system_prompt, user_prompt))
        raw_text = _extract_raw_text(response)
        card = _coerce_structured_card(getattr(response, "raw", None))
        
        # Extract ALL metadata from response
        metadata = {
            'token_usage': response.additional_kwargs,  # Contains prompt_tokens, completion_tokens, total_tokens
            'raw_response': response.raw,  # Complete raw response from provider
            'timestamp': time.time(),
            'model': response.raw.get('model', provider_name) if hasattr(response, 'raw') else provider_name,
            'response_id': response.raw.get('id', '') if hasattr(response, 'raw') else '',
        }
        
        # Log token usage
        token_usage = response.additional_kwargs
        logger.info(
            f"Token usage - Prompt: {token_usage.get('prompt_tokens', 0)}, "
            f"Completion: {token_usage.get('completion_tokens', 0)}, "
            f"Total: {token_usage.get('total_tokens', 0)}"
        )
        
    except (ValidationError, TypeError, ValueError) as e:
        raw_text = raw_text or _extract_raw_text(response)
        logger.exception(
            "Insight card structured parsing failed (provider=%s)",
            provider_name,
        )
        return _empty_result(provider_name=provider_name, raw=raw_text, error=str(e))
    except Exception as e:
        raw_text = raw_text or _extract_raw_text(response)
        logger.exception(
            "Insight card LLM call failed (provider=%s)",
            provider_name,
        )
        return _empty_result(provider_name=provider_name, raw=raw_text, error=str(e))

    # Build result with metadata
    result = _build_result(card=card, provider_name=provider_name, raw_text=raw_text)
    result.metadata = metadata
    
    return result
```

#### 3. Add File Saving Function

```python
import json
from pathlib import Path
from datetime import datetime

def save_result_to_file(result: InsightCardResult, output_dir: str = "output/insight_cards"):
    """
    Save InsightCardResult to a JSON file with timestamp in filename.
    
    Args:
        result: The InsightCardResult to save
        output_dir: Directory to save files (default: output/insight_cards)
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with epoch timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)
    filename = f"insight_card_result_{timestamp_ms}.json"
    filepath = Path(output_dir) / filename
    
    # Convert result to dict and write formatted JSON
    result_dict = result.model_dump()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved result to: {filepath}")
    return filepath
```

#### 4. Update Batch Runner to Save Files

```python
def run_sequential(
    llm,
    system_prompt_tpl: str,
    user_prompt_tpl: str,
    seed: dict,
    provider_name: str,
    count: int,
    dry_run: bool,
    output_dir: str = "output/insight_cards",
) -> list[InsightCardResult]:
    results = []
    seen = set()
    
    # Initialize batch tracking
    batch_tokens = {
        'total_prompt_tokens': 0,
        'total_completion_tokens': 0,
        'total_tokens': 0,
    }

    sampler = InsightCardVariableSampler(
        seed, worker_id=0, allowed_categories=["Technology"]
    )
    for i in range(count):
        variables = sampler.sample()

        card = generate_one_card(
            llm, system_prompt_tpl, user_prompt_tpl,
            variables, provider_name, dry_run,
        )
        
        # Save each result to individual file
        if not card.error:
            save_result_to_file(card, output_dir)
        
        # Aggregate token usage
        if card.metadata and 'token_usage' in card.metadata:
            usage = card.metadata['token_usage']
            batch_tokens['total_prompt_tokens'] += usage.get('prompt_tokens', 0)
            batch_tokens['total_completion_tokens'] += usage.get('completion_tokens', 0)
            batch_tokens['total_tokens'] += usage.get('total_tokens', 0)
        
        _log_card(card, i, seen, results)
    
    # Log batch summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Batch Summary:")
    logger.info(f"  Total cards generated: {len(results)}")
    logger.info(f"  Total prompt tokens: {batch_tokens['total_prompt_tokens']:,}")
    logger.info(f"  Total completion tokens: {batch_tokens['total_completion_tokens']:,}")
    logger.info(f"  Total tokens: {batch_tokens['total_tokens']:,}")
    logger.info(f"  Output directory: {output_dir}")
    logger.info(f"{'='*60}\n")

    return results
```

---

## Code Examples

### Complete Working Example

```python
"""
Example: Insight Card Generation with LiteLLM + Gemini
"""
import os
import json
from datetime import datetime
from llama_index.llms.litellm import LiteLLM
from llama_index.core.llms import ChatMessage
from pydantic import BaseModel

# Set API key
os.environ["GEMINI_API_KEY"] = "your-api-key-here"

# Define output schema
class InsightCard(BaseModel):
    title: str
    category: str
    content: str
    tone: str

# Initialize LLM
llm = LiteLLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    max_tokens=512,
)

# Create structured LLM
structured_llm = llm.as_structured_llm(output_cls=InsightCard)

# Prepare messages
messages = [
    ChatMessage(
        role="system",
        content="You are an expert at creating insightful, engaging content cards."
    ),
    ChatMessage(
        role="user",
        content="Create an insight card about productivity tips for remote workers."
    )
]

# Make request
response = structured_llm.chat(messages)

# Extract result
card = response.raw
print(f"Title: {card.title}")
print(f"Category: {card.category}")
print(f"Content: {card.content}")

# Extract token usage
token_usage = response.additional_kwargs
print(f"\nToken Usage:")
print(f"  Prompt tokens: {token_usage.get('prompt_tokens', 0)}")
print(f"  Completion tokens: {token_usage.get('completion_tokens', 0)}")
print(f"  Total tokens: {token_usage.get('total_tokens', 0)}")

# Calculate cost (approximate)
prompt_tokens = token_usage.get('prompt_tokens', 0)
completion_tokens = token_usage.get('completion_tokens', 0)
cost = (prompt_tokens * 0.075 / 1_000_000) + (completion_tokens * 0.30 / 1_000_000)
print(f"  Estimated cost: ${cost:.6f}")
```

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error:** `AuthenticationError: GEMINI_API_KEY not found`

**Solution:**
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Set it if missing
export GEMINI_API_KEY="your-api-key"

# Or add to .env file
echo "GEMINI_API_KEY=your-key" >> .env
```

#### 2. Model Not Found

**Error:** `Model gemini-2.0-flash not found`

**Solution:** Always use the `gemini/` prefix:
```python
# ❌ Wrong
llm = LiteLLM(model="gemini-2.0-flash")

# ✅ Correct
llm = LiteLLM(model="gemini/gemini-2.0-flash")
```

#### 3. Token Count Mismatch

**Issue:** LlamaIndex TokenCountingHandler shows different counts than response metadata

**Explanation:** 
- TokenCountingHandler uses tiktoken (OpenAI's tokenizer)
- Gemini uses its own tokenizer
- Counts will differ slightly

**Solution:** Use `response.additional_kwargs` for exact provider counts.

#### 4. Rate Limiting

**Error:** `RateLimitError: Quota exceeded`

**Solution:**
```python
# Add retry logic (built into LiteLLM)
llm = LiteLLM(
    model="gemini/gemini-2.0-flash",
    max_retries=3,  # Retry up to 3 times
)

# Or implement exponential backoff
import time
from litellm.exceptions import RateLimitError

for attempt in range(3):
    try:
        response = llm.chat(messages)
        break
    except RateLimitError:
        wait_time = 2 ** attempt
        logger.warning(f"Rate limited, waiting {wait_time}s...")
        time.sleep(wait_time)
```

#### 5. Structured Output Validation Errors

**Error:** `ValidationError: 1 validation error for InsightCard`

**Solution:**
```python
# Add error handling
try:
    response = structured_llm.chat(messages)
    card = response.raw
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    # Fallback to unstructured response
    response = llm.chat(messages)
    raw_text = response.message.content
    # Parse manually or retry
```

---

## Performance Optimization

### 1. Parallel Processing

```python
import concurrent.futures

def process_card(worker_id: int) -> InsightCardResult:
    # Each worker gets its own LLM instance
    llm = LiteLLM(model="gemini/gemini-2.0-flash")
    # ... generate card ...
    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_card, i) for i in range(count)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]
```

### 2. Caching (for repeated prompts)

```python
# LiteLLM supports caching via additional_kwargs
llm = LiteLLM(
    model="gemini/gemini-2.0-flash",
    additional_kwargs={
        "cache_control": {"type": "ephemeral"}  # Enable caching
    }
)
```

### 3. Batch Size Optimization

- **Small batches (< 10):** Use sequential processing
- **Medium batches (10-100):** Use parallel with 3-5 workers
- **Large batches (> 100):** Use parallel with 10+ workers, implement rate limiting

---

## Cost Estimation

### Gemini 2.0 Flash Pricing

- **Input:** $0.075 per 1M tokens
- **Output:** $0.30 per 1M tokens

### Example Calculation

For 100 insight cards:
- Average prompt: 500 tokens
- Average completion: 200 tokens

```
Input cost:  100 × 500 × $0.075 / 1,000,000 = $0.00375
Output cost: 100 × 200 × $0.30 / 1,000,000  = $0.00600
Total:                                        $0.00975
```

**Cost per card:** ~$0.0001 (very affordable!)

---

## Next Steps

1. **Install LiteLLM** using the commands in the installation section
2. **Get your Gemini API key** from Google AI Studio
3. **Update your orchestrator** with the recommended implementation
4. **Test with a small batch** (e.g., `--count 5`)
5. **Monitor token usage** and adjust as needed
6. **Scale up** to production batch sizes

---

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Token Usage Guide](https://docs.litellm.ai/docs/completion/token_usage)
- [LiteLLM Gemini Provider](https://docs.litellm.ai/docs/providers/gemini)
- [LlamaIndex LiteLLM Integration](https://docs.llamaindex.ai/en/stable/api_reference/llms/litellm/)
- [LlamaIndex Token Counting](https://docs.llamaindex.ai/en/stable/module_guides/observability/callbacks/token_counting_migration/)
- [Google AI Studio](https://ai.google.dev/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)

---

**Document Version:** 1.0  
**Last Updated:** April 8, 2026  
**Maintained By:** Tennl Batch Team
