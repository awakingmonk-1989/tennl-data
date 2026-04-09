# LiteLLM + Gemini — Technical Spec
## Response Structure, Token Extraction, and Known Issues
### April 8, 2026

---

## 1. Response Object Hierarchy

When using LiteLLM via LlamaIndex (`llama-index-llms-litellm`), the call chain is:

```
LLM.chat(messages)                          → ChatResponse
  └─ LiteLLM wrapper._chat(messages)
       └─ litellm.completion(**kwargs)      → ModelResponse
            └─ Gemini API generateContent   → native Gemini response
```

### LlamaIndex `ChatResponse` (return type of `llm.chat()`)

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `message` | `ChatMessage` | `response["choices"][0]["message"]` | `.content` property returns the LLM text output |
| `raw` | `Optional[Any]` | Full LiteLLM `ModelResponse` object | NOT a dict — it's a Pydantic model with `__getitem__` support |
| `additional_kwargs` | `dict` | `_get_response_token_counts(response)` | **Always `{}` for LiteLLM** — see bug below |
| `delta` | `Optional[str]` | Streaming only | |
| `logprobs` | `Optional[...]` | When provider supplies it | |

Method signatures (all return `ChatResponse`):
- `LLM.chat(messages) -> ChatResponse`
- `LLM.achat(messages) -> ChatResponse`
- `LLM.stream_chat(messages) -> Generator[ChatResponse]`
- `LLM.astream_chat(messages) -> AsyncGenerator[ChatResponse]`

There is no `ChatCompletionResponse` type — it is always `ChatResponse`.

### `ChatMessage.content` property

```python
@property
def content(self) -> str | None:
    content_strs = []
    for block in self.blocks:
        if isinstance(block, TextBlock):
            content_strs.append(block.text)
    ct = "\n".join(content_strs) or None
    return ct
```

For Gemini via LiteLLM, `response.message.content` returns the LLM text output, which is the card JSON typically wrapped in markdown code fences:

```
```json
{ "title": "...", "category": "...", ... }
```​
```

---

## 2. LiteLLM `ModelResponse` (what lives in `ChatResponse.raw`)

The `ModelResponse` is a Pydantic model, NOT a dict subclass:

```python
isinstance(ModelResponse(), dict)  # False
issubclass(ModelResponse, dict)    # False
```

But it supports dict-like access:
```python
response.raw["usage"]      # works via __getitem__
response.raw.get("usage")  # works via .get()
```

### Full structure from a live Gemini call

Reference file: `python/tennl/batch/output/response_raw_dump.json`

```json
{
  "id": "SzjWac-DNcHOg8UP_86zkQY",
  "created": 1775646795,
  "model": "gemini-2.5-flash",
  "object": "chat.completion",
  "system_fingerprint": null,
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "```json\n{...intended card JSON structure...}\n```",
        "role": "assistant",
        "tool_calls": null,
        "function_call": null,
        "images": [],
        "thinking_blocks": []
      }
    }
  ],
  "usage": {
    "completion_tokens": 830,
    "prompt_tokens": 382,
    "total_tokens": 1212,
    "completion_tokens_details": {
      "reasoning_tokens": 591,
      "text_tokens": 239
    },
    "prompt_tokens_details": {
      "audio_tokens": null,
      "cached_tokens": null,
      "text_tokens": 382,
      "image_tokens": null,
      "video_tokens": null
    },
    "cache_read_input_tokens": null
  },
  "vertex_ai_grounding_metadata": [],
  "vertex_ai_url_context_metadata": [],
  "vertex_ai_safety_results": [],
  "vertex_ai_citation_metadata": []
}
```

---

## 3. Token Fields — Complete Breakdown

### `usage` (top-level)

| Field | Example | Meaning |
|-------|---------|---------|
| `prompt_tokens` | 382 | Total input tokens |
| `completion_tokens` | 830 | Total output tokens (thinking + visible text) |
| `total_tokens` | 1212 | `prompt_tokens + completion_tokens` |

### `usage.completion_tokens_details`

| Field | Example | Meaning |
|-------|---------|---------|
| `reasoning_tokens` | 591 | Gemini "thinking" tokens (mapped from `thoughtsTokenCount`) |
| `text_tokens` | 239 | Actual visible output tokens |

Relationship: `completion_tokens` (830) = `reasoning_tokens` (591) + `text_tokens` (239)

### `usage.prompt_tokens_details`

| Field | Example | Meaning |
|-------|---------|---------|
| `text_tokens` | 382 | Text input tokens |
| `audio_tokens` | null | Audio input (not used) |
| `cached_tokens` | null | Prompt caching (not used) |
| `image_tokens` | null | Image input (not used) |
| `video_tokens` | null | Video input (not used) |

### `usage.cache_read_input_tokens`

`null` — no cached input tokens in this response

---

## 4. Gemini Native vs LiteLLM Translated Mapping

| Gemini native (`usageMetadata`) | LiteLLM translated (`usage`) |
|---------------------------------|------------------------------|
| `promptTokenCount` | `prompt_tokens` |
| `candidatesTokenCount` | `text_tokens` (in `completion_tokens_details`) |
| `thoughtsTokenCount` | `reasoning_tokens` (in `completion_tokens_details`) |
| `totalTokenCount` | `total_tokens` |
| `promptTokensDetails[].tokenCount` (TEXT) | `prompt_tokens_details.text_tokens` |

---

## 5. Known Bug: `additional_kwargs` Always Empty for LiteLLM

### Root cause

In `llama_index/llms/litellm/base.py`, the `_chat()` method builds the `ChatResponse`:

```python
return ChatResponse(
    message=message,
    raw=response,
    additional_kwargs=self._get_response_token_counts(response),
)
```

And `_get_response_token_counts`:

```python
def _get_response_token_counts(self, raw_response: Any) -> dict:
    if not isinstance(raw_response, dict):
        return {}                          # <-- ALWAYS hits this for LiteLLM
    usage = raw_response.get("usage", {})
    return {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }
```

`ModelResponse` is a Pydantic model, not a dict. `isinstance(response, dict)` is `False`. So the method returns `{}` every time.

### Impact

- `response.additional_kwargs` is always `{}`
- Token data is only accessible via `response.raw.get("usage")` or `response.raw["usage"]`

### Workaround (IMPLEMENTED)

Read from `response.raw` directly instead of `response.additional_kwargs` when the provider is `litellm`. Implemented in `_extract_litellm_token_metadata()` in the orchestrator.

---

## 6. Known Bug: LiteLLM Gemini Token Count Translation

GitHub issue: [BerriAI/litellm#23731](https://github.com/BerriAI/litellm/issues/23731)

When Gemini uses tool calls / function calling, LiteLLM's `_calculate_usage()` method in `vertex_and_google_ai_studio_gemini.py` incorrectly folds `toolUsePromptTokenCount` into `completion_tokens` and `reasoning_tokens` instead of `prompt_tokens`.

**For our insight card use case** (no tool calls in the direct `llm.chat()` path), this bug does NOT apply. It would only affect calls made through `as_structured_llm()` which uses function calling under the hood.

A fix PR exists: [BerriAI/litellm#24622](https://github.com/BerriAI/litellm/pull/24622)

---

## 7. Why `llm.chat()` Instead of `as_structured_llm()`

| Aspect | `as_structured_llm()` | Direct `llm.chat()` |
|--------|----------------------|---------------------|
| Card parsing | Automatic via function calling | Manual: strip code fences + `model_validate_json()` |
| `response.raw` | Parsed `InsightCard` Pydantic object | Full `ModelResponse` with token data |
| Token usage | **Lost** — raw is overwritten | **Available** at `response.raw["usage"]` |
| Reliability | Higher (function calling schema) | Depends on LLM returning clean JSON |

Decision (IMPLEMENTED): Use `llm.chat()` directly to preserve token data. Parse card JSON manually from `response.message.content` via `_strip_code_fences()` + `InsightCard.model_validate_json()`.

---

## 8. Gemini Code Fence Behavior

Gemini wraps JSON output in markdown code fences even when told to return "valid JSON only":

```
```json
{ "title": "...", ... }
```​
```

The parser must strip these before calling `InsightCard.model_validate_json()`. This is implemented as `_strip_code_fences()` in the orchestrator:

```python
import re

def _strip_code_fences(text: str) -> str:
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()
```

---

## 9. Authentication

LiteLLM reads `GEMINI_API_KEY` from the environment. The orchestrator's `_load_secrets_env()` auto-loads it from `secrets.txt` at the repo root.

```
# secrets.txt
GEMINI_API_KEY=AIzaSy...
```

The model string must include the `gemini/` prefix: `gemini/gemini-2.5-flash` (not just `gemini-2.5-flash`).

---

## 10. Available Gemini Models (April 2026)

| Model | Status | Cost (per 1M tokens) |
|-------|--------|---------------------|
| `gemini/gemini-3-flash` | Stable (GA) | In: $0.50, Out: $1.50 |
| `gemini/gemini-3.1-flash-lite-preview` | Preview | In: $0.25, Out: $1.50 |
| `gemini/gemini-3.1-pro-preview` | Preview | In: $1.25, Out: $5.00 |
| `gemini/gemini-2.5-flash` | Stable | In: $0.075, Out: $0.30 |
| `gemini/gemini-2.5-pro` | Stable | In: $1.25, Out: $5.00 |

Currently configured: `gemini/gemini-2.5-flash` (cheapest stable option).

---

## 11. Implemented Pydantic Models for Token Usage

All models live in `python/tennl/batch/src/tennl/batch/domain/insight_cards.py` and are exported from `domain/__init__.py`.

### `CompletionTokensDetails`

```python
class CompletionTokensDetails(BaseModel):
    model_config = ConfigDict(extra="allow")
    reasoning_tokens: int = 0      # Gemini "thinking" tokens
    text_tokens: int = 0           # Visible output tokens
```

### `PromptTokensDetails`

```python
class PromptTokensDetails(BaseModel):
    model_config = ConfigDict(extra="allow")
    text_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    image_tokens: Optional[int] = None
    video_tokens: Optional[int] = None
```

### `LiteLLMGeminiTokenUsage`

```python
class LiteLLMGeminiTokenUsage(BaseModel):
    model_config = ConfigDict(extra="allow")
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None
    cache_read_input_tokens: Optional[int] = None
```

All models use `extra="allow"` to be forward-compatible if LiteLLM adds new fields.

### Sample `_tokens.json` output (from live Gemini call)

```json
{
  "prompt_tokens": 382,
  "completion_tokens": 673,
  "total_tokens": 1055,
  "completion_tokens_details": {
    "reasoning_tokens": 462,
    "text_tokens": 211,
    "accepted_prediction_tokens": null,
    "audio_tokens": null,
    "rejected_prediction_tokens": null,
    "image_tokens": null,
    "video_tokens": null
  },
  "prompt_tokens_details": {
    "text_tokens": 382,
    "audio_tokens": null,
    "cached_tokens": null,
    "image_tokens": null,
    "video_tokens": null
  },
  "cache_read_input_tokens": null
}
```

---

## 12. Provider-Aware Token Extraction (Implemented)

The orchestrator dispatches token extraction based on the provider name:

```
_extract_token_metadata(response, provider_name)
  ├── provider_name == "litellm"  →  _extract_litellm_token_metadata(response)
  │     reads response.raw["usage"] → LiteLLMGeminiTokenUsage.model_validate() → .model_dump()
  └── else                        →  _extract_default_token_metadata(response)
        reads response.additional_kwargs → {prompt_tokens, completion_tokens, total_tokens}
```

Both extractors return a dict with `prompt_tokens`, `completion_tokens`, `total_tokens` at the top level, making them compatible with `_log_batch_summary()`.

---

## 13. Triple-File Output (Implemented)

Each card produces 3 files with a shared prefix `insight_card_{model}_{epoch_ms}`:

| Suffix | Content | Source |
|--------|---------|--------|
| `.json` | Structured card fields only (title, category, content, tone, etc.) | `InsightCardResult.model_dump()` minus raw/metadata/provider/error |
| `_raw.json` | Full LiteLLM `ModelResponse` | `result.metadata["raw_response"]` (via `_safe_serialize(response.raw)`) |
| `_tokens.json` | Token usage Pydantic model | `result.metadata["token_usage"]` (from `_extract_token_metadata()`) |

Model name in the prefix is sanitized: `gemini/gemini-2.5-flash` becomes `gemini_gemini_2_5_flash`.
