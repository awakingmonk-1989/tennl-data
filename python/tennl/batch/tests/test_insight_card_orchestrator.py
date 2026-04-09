from __future__ import annotations

import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from tennl.batch.domain import InsightCard, InsightCardResult
from tennl.batch.generator.insight_cards.insight_card_llamaindex_orchestrator import (
    InsightCardVariableSampler,
    _build_messages,
    _log_card,
    generate_one_card,
)


@dataclass
class FakeResponse:
    raw: object
    text: str = ""


class FakeStructuredLLM:
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None):
        self._response = response
        self._error = error
        self.messages = None

    def chat(self, messages):
        self.messages = messages
        if self._error is not None:
            raise self._error
        text = self._response.text if self._response else ""
        return SimpleNamespace(
            message=SimpleNamespace(content=text),
            raw=self._response.raw if self._response else None,
        )


class FakeLLM:
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None):
        self._structured = FakeStructuredLLM(response=response, error=error)
        self.output_cls = None

    def chat(self, messages):
        return self._structured.chat(messages)

    def as_structured_llm(self, output_cls):
        self.output_cls = output_cls
        return self._structured


def _seed() -> dict:
    return {
        "hook_types": ["question-led"],
        "registers": ["wonder"],
        "opening_word_classes": ["question-word"],
        "title_style_hints": {"styles": ["intriguing question"], "avoid": ["Old Title"]},
        "categories": {
            "Technology": {
                "themes": ["counterintuitive mechanism", "hidden cost"],
                "human_contexts": ["time and attention", "work and focus"],
            }
        },
    }


def _tech_sampler(worker_id: int = 0) -> InsightCardVariableSampler:
    return InsightCardVariableSampler(
        _seed(), worker_id=worker_id, allowed_categories=["Technology"]
    )


class InsightCardOrchestratorTests(unittest.TestCase):
    def test_sampler_maps_tone_and_emotional_register_from_register(self) -> None:
        variables = _tech_sampler(0).sample()

        self.assertEqual(variables["register"], "wonder")
        self.assertEqual(variables["tone"], "wonder")
        self.assertEqual(variables["emotional_register"], "wonder")

    def test_generate_one_card_returns_structured_result(self) -> None:
        card = InsightCard(
            title="Quiet Loops",
            category="Technology",
            content="A short insight card body.",
            layout="hook_body_close",
            content_blocks={"hook": "h", "body": "b", "close": "c"},
            tone="wonder",
            emotional_register="wonder",
            title_style="intriguing question",
            hook_type="question-led",
            opening_word_class="question-word",
        )
        response = FakeResponse(raw=card, text=card.model_dump_json())
        llm = FakeLLM(response=response)

        result = generate_one_card(
            llm=llm,
            system_prompt_tpl="System {category}",
            user_prompt_tpl="User {topic}",
            variables=_tech_sampler(0).sample(),
            provider_name="openai",
            dry_run=False,
        )

        self.assertIsNone(llm.output_cls)
        self.assertIsInstance(result, InsightCardResult)
        self.assertEqual(result.title, "Quiet Loops")
        self.assertEqual(result.content, "A short insight card body.")
        self.assertEqual(result.provider, "openai")
        self.assertIn('"title":"QuietLoops"', result.raw.replace(" ", ""))

    def test_generate_one_card_captures_runtime_error(self) -> None:
        llm = FakeLLM(error=RuntimeError("provider exploded"))

        result = generate_one_card(
            llm=llm,
            system_prompt_tpl="",
            user_prompt_tpl="User {topic}",
            variables=_tech_sampler(0).sample(),
            provider_name="azure-openai",
            dry_run=False,
        )

        self.assertEqual(result.error, "provider exploded")
        self.assertEqual(result.provider, "azure-openai")
        self.assertEqual(result.content, "")

    def test_generate_one_card_captures_invalid_structured_output(self) -> None:
        response = FakeResponse(raw={"title": "Missing required fields"}, text='{"title":"Missing required fields"}')
        llm = FakeLLM(response=response)

        result = generate_one_card(
            llm=llm,
            system_prompt_tpl="",
            user_prompt_tpl="User {topic}",
            variables=_tech_sampler(0).sample(),
            provider_name="openai",
            dry_run=False,
        )

        self.assertIsNotNone(result.error)
        self.assertIn("content", (result.error or "").lower())
        self.assertIn("Missing required fields", result.raw)

    def test_log_card_dedupes_on_title_and_content(self) -> None:
        seen: set[str] = set()
        results: list[InsightCardResult] = []
        first = InsightCardResult(
            title="Same Title",
            category="Technology",
            content="Same content",
            tone="wonder",
            emotional_register="wonder",
            title_style="intriguing question",
            hook_type="question-led",
            opening_word_class="question-word",
            provider="openai",
            raw="{}",
        )
        second = first.model_copy(update={"provider": "azure-openai"})

        _log_card(first, idx=0, seen=seen, results=results)
        _log_card(second, idx=1, seen=seen, results=results)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider, "openai")

    def test_dry_run_returns_prompt_preview_in_raw(self) -> None:
        result = generate_one_card(
            llm=FakeLLM(),
            system_prompt_tpl="System {category}",
            user_prompt_tpl="User {topic}",
            variables=_tech_sampler(0).sample(),
            provider_name="openai",
            dry_run=True,
        )

        self.assertEqual(result.title, "[DRY RUN]")
        self.assertIn("[SYSTEM]", result.raw)
        self.assertIn("[USER]", result.raw)

    def test_build_messages_omits_empty_system_prompt(self) -> None:
        messages = _build_messages("", "hello")

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role.value, "user")
        self.assertEqual(messages[0].content, "hello")
