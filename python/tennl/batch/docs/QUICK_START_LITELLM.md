# Quick Start: LiteLLM + Gemini Integration

## TL;DR - Get Started in 5 Minutes

### 1. Install LiteLLM

```bash
cd /Users/devansh/tennl-data/python/tennl/batch
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv pip install litellm llama-index-llms-litellm
```

### 2. Get Gemini API Key

1. Visit: https://ai.google.dev/
2. Click "Get API key"
3. Copy your key

### 3. Set Environment Variable

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Update Your Code

```python
from llama_index.llms.litellm import LiteLLM
import os

# Initialize
llm = LiteLLM(
    model="gemini/gemini-2.0-flash",  # Note: "gemini/" prefix is required
    temperature=0.7,
    max_tokens=1024,
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Use with structured output
structured_llm = llm.as_structured_llm(output_cls=InsightCard)
response = structured_llm.chat(messages)

# Get token usage
token_usage = response.additional_kwargs
print(f"Tokens used: {token_usage.get('total_tokens', 0)}")
```

### 5. Run Your Batch Job

```bash
UV_PROJECT_ENVIRONMENT="python/tennl/batch/.venv" uv run python -m tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator --count 5
```

---

## Token Tracking - Best Option for Your Use Case

### Recommended: Use `response.additional_kwargs`

This gives you exact token counts from Gemini without any additional setup:

```python
response = llm.chat(messages)

# Extract token usage
token_usage = response.additional_kwargs
prompt_tokens = token_usage.get('prompt_tokens', 0)
completion_tokens = token_usage.get('completion_tokens', 0)
total_tokens = token_usage.get('total_tokens', 0)

# Log it
logger.info(f"Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total")

# Calculate cost (Gemini 2.0 Flash pricing)
cost = (prompt_tokens * 0.075 / 1_000_000) + (completion_tokens * 0.30 / 1_000_000)
logger.info(f"Cost: ${cost:.6f}")
```

### Why This Approach?

✅ **Exact counts** from Gemini (not estimated)  
✅ **No additional setup** required  
✅ **Available immediately** in every response  
✅ **Works with structured output**  
✅ **Includes all metadata** from the provider  

---

## Logging Best Practices

### Per-Request Logging

```python
def log_request(response, card_index: int):
    """Log token usage for each card generation"""
    token_usage = response.additional_kwargs
    
    logger.info(
        f"Card {card_index}: "
        f"{token_usage.get('total_tokens', 0)} tokens "
        f"(prompt: {token_usage.get('prompt_tokens', 0)}, "
        f"completion: {token_usage.get('completion_tokens', 0)})"
    )
    
    return token_usage
```

### Batch-Level Aggregation

```python
# Track across all requests
batch_stats = {
    'total_prompt_tokens': 0,
    'total_completion_tokens': 0,
    'total_tokens': 0,
    'request_count': 0
}

for i in range(count):
    response = llm.chat(messages)
    usage = response.additional_kwargs
    
    batch_stats['total_prompt_tokens'] += usage.get('prompt_tokens', 0)
    batch_stats['total_completion_tokens'] += usage.get('completion_tokens', 0)
    batch_stats['total_tokens'] += usage.get('total_tokens', 0)
    batch_stats['request_count'] += 1

# Log summary
logger.info(f"\nBatch Summary:")
logger.info(f"  Requests: {batch_stats['request_count']}")
logger.info(f"  Total tokens: {batch_stats['total_tokens']:,}")
logger.info(f"  Avg tokens/request: {batch_stats['total_tokens'] / batch_stats['request_count']:.0f}")
```

### Save to File (Optional)

```python
import json
from datetime import datetime

# Collect detailed logs
request_logs = []

for i in range(count):
    response = llm.chat(messages)
    usage = response.additional_kwargs
    
    request_logs.append({
        'timestamp': datetime.utcnow().isoformat(),
        'card_index': i,
        'model': 'gemini-2.0-flash',
        'prompt_tokens': usage.get('prompt_tokens', 0),
        'completion_tokens': usage.get('completion_tokens', 0),
        'total_tokens': usage.get('total_tokens', 0),
    })

# Save to file
with open('token_usage_log.json', 'w') as f:
    json.dump(request_logs, f, indent=2)
```

---

## Available Models

| Model | Speed | Quality | Cost (per 1M tokens) | Best For |
|-------|-------|---------|----------------------|----------|
| `gemini/gemini-2.0-flash` | ⚡⚡⚡ | ⭐⭐⭐ | $0.075 / $0.30 | **Recommended** - Fast, cheap |
| `gemini/gemini-2.5-flash` | ⚡⚡⚡ | ⭐⭐⭐⭐ | $0.075 / $0.30 | Balanced |
| `gemini/gemini-2.5-pro` | ⚡⚡ | ⭐⭐⭐⭐⭐ | $1.25 / $5.00 | Complex reasoning |
| `gemini/gemini-3-flash-preview` | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | $0.075 / $0.30 | Latest, fastest |

**Start with `gemini-2.0-flash`** - it's fast, cheap, and perfect for insight cards.

---

## Common Issues & Solutions

### Issue: "GEMINI_API_KEY not found"

```bash
# Check if set
echo $GEMINI_API_KEY

# Set it
export GEMINI_API_KEY="your-key-here"

# Or add to .env file
echo "GEMINI_API_KEY=your-key" >> python/tennl/batch/.env
```

### Issue: "Model not found"

Always use the `gemini/` prefix:

```python
# ❌ Wrong
llm = LiteLLM(model="gemini-2.0-flash")

# ✅ Correct
llm = LiteLLM(model="gemini/gemini-2.0-flash")
```

### Issue: Rate limiting

```python
# LiteLLM has built-in retries
llm = LiteLLM(
    model="gemini/gemini-2.0-flash",
    max_retries=3,  # Automatically retry on rate limits
)
```

---

## Cost Estimation

### Example: 100 Insight Cards

Assuming:
- 500 tokens per prompt
- 200 tokens per completion

```
Input:  100 × 500 × $0.075 / 1,000,000 = $0.00375
Output: 100 × 200 × $0.30 / 1,000,000  = $0.00600
Total:                                   $0.00975
```

**Cost per card: ~$0.0001** (less than a penny for 100 cards!)

---

## Next Steps

1. ✅ Install LiteLLM (see step 1 above)
2. ✅ Get API key (see step 2 above)
3. ✅ Update your orchestrator code
4. ✅ Test with small batch: `--count 5`
5. ✅ Monitor token usage in logs
6. ✅ Scale up to production

---

## Full Documentation

For detailed implementation guide, see:
- **[LITELLM_GEMINI_INTEGRATION_GUIDE.md](./LITELLM_GEMINI_INTEGRATION_GUIDE.md)** - Complete guide with examples

## External Resources

- [LiteLLM Docs](https://docs.litellm.ai/)
- [Gemini API](https://ai.google.dev/)
- [LlamaIndex LiteLLM](https://docs.llamaindex.ai/en/stable/api_reference/llms/litellm/)

---

**Questions?** Check the full guide or the troubleshooting section.
