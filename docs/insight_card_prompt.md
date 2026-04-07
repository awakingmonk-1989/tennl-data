Updated all 4 versions with title + category as part of the single-pass output.

---

## V1 — Prompt Only
*Any model · ~130 tokens · Zero setup · Stateless*

```
Write a short insight card on the topic: {{TOPIC}}.

Category: {{CATEGORY}}
Hook style: {{HOOK_TYPE}}
Emotional register: {{REGISTER}}

Rules:
- Open with a surprising, non-obvious claim or question
- Explain the mechanism in plain language (no jargon)
- Include one concrete example or observation (no citations, no statistics, no data references)
- End with a practical implication or reflection prompt
- Length: 120–180 words
- Tone: conversational, intelligent, never preachy
- Do not reference news, current events, studies, or data sources
- Do not include any unsafe, harmful, hateful, or adult content

Output format (exactly this, no markdown, no extra labels):
TITLE: [a short punchy title, max 8 words]
CATEGORY: [the category]
[card text]
```

**Variables:**
- `{{CATEGORY}}` → Finance · Technology · Science · Life · Psychology · Culture · History · Health
- `{{HOOK_TYPE}}` → contrarian-claim · question-led · named-concept · story-opening · analogy-led
- `{{REGISTER}}` → wonder · urgency · comfort · challenge · nostalgia

**Notes:** Rotate one value from each variable list per run. No session state needed. Safe to run in parallel across any number of workers. Parse output by splitting on the first two newlines after CATEGORY line.

---

## V2 — Spec-Based Prompt
*Large models (Claude, GPT-4-class, Gemini Pro) · ~340 tokens · Parallel-safe · Stateless diversity*

**System prompt:**
```
You are an insight card writer. Insight cards are short, self-contained pieces that deliver one genuinely surprising idea with clarity and warmth.

STRUCTURE (follow in order):
1. TITLE — Max 8 words. Punchy, specific, not generic. Avoid "The power of..." or "Why you should...".
2. CATEGORY — Exactly as provided in the input.
3. HOOK — One sentence. Counterintuitive claim, vivid question, or named concept reveal. Must make the reader pause.
4. MECHANISM — 2–3 sentences. Explain why or how this is true. Plain language only. No jargon.
5. EXAMPLE — 1–2 sentences. A concrete, relatable observation or scenario. No citations. No statistics. No data references.
6. IMPLICATION — 1–2 sentences. What this means for the reader, or a reflection prompt.
7. CLOSE — One memorable sentence. A reframe, lingering thought, or quiet action.

HARD RULES:
- No news, current events, or references to real studies or publications
- No statistics, percentages, or quantified claims requiring a source
- No harmful, hateful, abusive, sexual, or unsafe content of any kind
- No preachy or moralistic tone
- No markdown, headers, or extra labels in output beyond TITLE and CATEGORY

OUTPUT FORMAT (exactly this):
TITLE: [title]
CATEGORY: [category]
[card text as flowing prose]
```

**User prompt:**
```
Write one insight card.

Topic: {{TOPIC}}
Category: {{CATEGORY}}
Hook style: {{HOOK_TYPE}}
Emotional register: {{REGISTER}}
Opening word class: {{OPENING_WORD_CLASS}}
```

**Variables:**
- `{{CATEGORY}}` → Finance · Technology · Science · Life · Psychology · Culture · History · Health
- `{{HOOK_TYPE}}` → contrarian-claim · question-led · named-concept · story-opening · analogy-led
- `{{REGISTER}}` → wonder · urgency · comfort · challenge · nostalgia
- `{{OPENING_WORD_CLASS}}` → article (The / A) · verb (Consider / Imagine / Notice) · proper-noun · question-word (What / Why / When)

**Notes:** `OPENING_WORD_CLASS` is the stateless diversity lever — sample it randomly per run to force structural variation without needing cross-session memory. All four variables are independent; safe to generate in parallel across any number of workers.

---

## V3 — ≤30B Optimised
*Mistral 7B–30B · Qwen · LLaMA 3.1 instruct · Phi-3 medium · ~210 tokens · Single prompt block*

```
[TASK] Write a short insight card. Follow every instruction exactly.

[INPUTS]
Topic: {{TOPIC}}
Category: {{CATEGORY}}
Hook: {{HOOK_TYPE}}
Tone: {{REGISTER}}

[FORMAT] Output exactly this structure, nothing else:
TITLE: [max 8 words, punchy and specific]
CATEGORY: [copy exactly from INPUTS above]
Sentence 1 — A surprising or counterintuitive claim about the topic.
Sentence 2 — Explain why this happens in plain words.
Sentence 3 — Give one everyday example that makes it concrete.
Sentence 4 — Say what this means for a person in ordinary life.
Sentence 5 — End with one short memorable thought or question.

[RULES]
Do not mention news, studies, statistics, or any numbers.
Do not write anything harmful, hateful, sexual, or unsafe.
Do not use bullet points, headers, or markdown.
Do not add any extra labels beyond TITLE and CATEGORY.
Write only what is shown in FORMAT. Nothing before it. Nothing after it.

[BEGIN]
TITLE:
```

**Variables:**
- `{{CATEGORY}}` → Finance · Technology · Science · Life · Psychology · Culture · History · Health
- `{{HOOK_TYPE}}` → contrarian-claim · question-led · named-concept · story-opening · analogy-led
- `{{REGISTER}}` → wonder · urgency · comfort · challenge · nostalgia

**Notes:** The `[BEGIN]` tag followed by `TITLE:` primes the model to output structure immediately, skipping preamble — the most common failure mode in ≤30B instruct models. Numbered sentence slots prevent structural drift. If the model still echoes instructions, add `Sentence 1:` as an additional primer after `TITLE:` and `CATEGORY:` lines.

---

## V4 — MoE / Non-Reasoning
*Mixtral 8x7B · Qwen MoE · DeepSeek MoE · ~170 tokens · No chain-of-thought · Prefix-seeded*

```
Complete this insight card. Write naturally. Do not explain your reasoning. Do not use lists or headers.

Topic: {{TOPIC}}
Category: {{CATEGORY}}
Opening style: {{HOOK_TYPE}}
Feeling: {{REGISTER}}

The card should:
- Open with something unexpected about the topic
- Explain it simply without any numbers or source references
- Include a grounded everyday observation
- Close with a thought the reader will carry with them
- Be between 120 and 160 words

Do not write news, harmful, hateful, sexual, or unsafe content.
Output only the card in this format:

TITLE: [max 8 words, punchy and specific]
CATEGORY: {{CATEGORY}}
{{SEED_PREFIX}}
```

**Variables:**
- `{{CATEGORY}}` → Finance · Technology · Science · Life · Psychology · Culture · History · Health
- `{{HOOK_TYPE}}` → contrarian-claim · question-led · named-concept · story-opening · analogy-led
- `{{REGISTER}}` → wonder · urgency · comfort · challenge · nostalgia
- `{{SEED_PREFIX}}` → your orchestrator injects one of these completed strings per run:
    - `There's something strange about`
    - `Most people assume`
    - `The word nobody uses for`
    - `Before this had a name, people`
    - `It looks like`

**Notes:** `{{SEED_PREFIX}}` is resolved by your orchestrator before the prompt hits the model — the model sees a completed first line, not an instruction. This is the critical distinction from V1–V3. The prefix primes the active expert cluster toward editorial generation immediately and forces opening variation without cross-session state. Rotate `SEED_PREFIX` randomly per run. Do not use chain-of-thought or reasoning scaffold instructions with MoE models — they cause inconsistent expert routing and output drift.