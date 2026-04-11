from __future__ import annotations

# ─────────────────────────────────────────────────────────────
# Chat engine factory — fresh instance per card generation
# ─────────────────────────────────────────────────────────────

def build_chat_engine(llm, system_prompt: str):
    """
    Creates a fresh SimpleChatEngine with no prior chat history.
    Each call is a new isolated session — no state leaks between cards.
    """
    from llama_index.core.chat_engine import SimpleChatEngine

    return SimpleChatEngine.from_defaults(
        llm=llm,
        system_prompt=system_prompt if system_prompt.strip() else None,
    )
