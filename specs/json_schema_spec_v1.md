# Content JSON Schema Spec
## India Discovery Platform — Typed Schema for UI-Ready Content Generation
### Version 1.0 · Works with Content Spec v3.0 + Narration Flow Spec v1.1 · March 2026

---

## ABOUT THIS SPEC

This is the **third and final spec** in the content generation system. It defines the complete typed JSON schema that a content agent must produce. This JSON is the single source of truth for the UI renderer — the UI reads fields, never parses prose.

All three specs must be present for a valid agent run:
- **Content Spec v3.0** — what to write: safety, topics, word counts, source rules, image rules, file outputs
- **Narration Flow Spec v1.1** — how to write it: narrative structure, section options, deep dive variants, tonal arc
- **This spec (JSON Schema v1.0)** — how to structure the output: typed fields, enums, required/optional, nested schemas for every UI element

**Agent rule:** Do not invent fields not in this schema. Do not omit required fields. When a field is optional and not applicable, set it to `null` — do not omit it.

---

## SECTION 0: ROOT SCHEMA ENVELOPE

```json
{
  "$schema": "content-schema-v1.0",
  "article_id": "LIFEHACKS_FOCUS_001",
  "variant": "CURATED_WEB_WITH_IMAGES",
  "content_label": "CURATED CONTENT",
  "topic": "Life Hacks",
  "sub_topic": "Focus & Attention",
  "slug": "lifehacks_focus",
  "category_path": "Lifestyle & Daily Living › Life Hacks › Focus & Attention",
  "target_audience": "India — Urban Adults 18–45",
  "theme": {},
  "theme_override": {},
  "word_count_meta": {},
  "content_safety": {},
  "hero": {},
  "hook": {},
  "sections": [],
  "quick_reference": {},
  "sources": [],
  "content_sources": [],
  "excluded_sources": [],
  "images": [],
  "images_ignored": [],
  "tonal_arc": [],
  "content_option_sequence": [],
  "file_references": {},
  "generation_meta": {}
}
```

---

## SECTION 0A: THEME METADATA (ENHANCEMENT — NON-BREAKING EXTENSION)

Theme metadata is an **additive** root-level layer that records the article’s chosen “angle”. It must not change any existing safety or structure requirements; it only makes theme selection explicit and enforceable.

### 0A.1 Theme object (required)

```json
"theme": {
  "primary": "Best Practices",
  "secondary": "Curiosity-driven framing"
}
```

| Field | Type | Required | Enum Values | Rules |
|---|---|---|---|---|
| primary | enum | YES | "Knowledge Sharing", "Compare & Contrast", "Best Practices", "Safe Tips / Preventive Insights", "Optimal Experiences", "Habit Formation / Behavior Change", "Cultural / India-specific Nuance", "Myth vs Reality", "Quick Wins / Immediate Actions" | Choose exactly 1 primary theme |
| secondary | enum or null | YES | "Storytelling / Narrative hook", "Data-backed credibility", "Emotional relatability", "Curiosity-driven framing", "Experiment / Try-this framing" | Optional; must be null or one value (max 1) |

### 0A.2 Theme override object (required)

```json
"theme_override": {
  "used": false,
  "reason": null
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| used | boolean | YES | true only when the agent deliberately deviates from the most “obvious” theme mapping for the given input |
| reason | string or null | YES | Must be non-null and specific when used=true. Must be null when used=false |

Validation:
- theme.primary missing → REJECT
- theme.secondary present but not in enum → REJECT
- theme_override.used=true and theme_override.reason is null/empty → REJECT
- theme_override.used=false and reason is non-null → REJECT

---

## SECTION 1: WORD COUNT META

```json
"word_count_meta": {
  "word_count": 680,
  "reading_time_minutes": 5,
  "is_short_read": false,
  "is_medium_content": true
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| `word_count` | integer | YES | Actual count of rendered article body. Excludes JSON block |
| `reading_time_minutes` | integer | YES | Derived: word_count / 200, rounded up |
| `is_short_read` | boolean | YES | true if word_count < 500. Mutually exclusive with is_medium_content |
| `is_medium_content` | boolean | YES | true if 500 <= word_count <= 1000. Mutually exclusive with is_short_read |

Validation: word_count > 1200 → REJECT. Both flags true simultaneously → REJECT.

---

## SECTION 2: CONTENT SAFETY

```json
"content_safety": {
  "is_sexually_explicit": false,
  "is_harmful": false,
  "is_abusive": false,
  "is_intimidating": false,
  "is_content_safe": true,
  "has_real_person_references": false,
  "has_sports_references": false,
  "has_movie_references": false,
  "masked_persons": [
    {
      "masked_as": "a Bengaluru-based food blogger",
      "real_name": "REDACTED",
      "context": "Referenced in professional capacity as source of cooking tip"
    }
  ]
}
```

All boolean flags: required, must be false except is_content_safe which must be true.
Any flag set incorrectly → REJECT.
masked_persons: empty array [] when no professionals referenced. Populated only when a public professional is cited in sources but their name is masked in article body text.

---

## SECTION 3: HERO

```json
"hero": {
  "title_line_1": "Reclaim",
  "title_line_2": "Your Focus.",
  "title_display": {
    "line_1_style": "bold_display",
    "line_2_style": "italic_accent"
  },
  "descriptor": "What costs you 4 hours a day without you noticing — and the 3-minute fix.",
  "category_label": "LIFESTYLE · LIFE HACKS",
  "quote_banner": {
    "enabled": false,
    "text": null
  }
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| title_line_1 | string | YES | Strong noun or verb phrase. Displayed bold large serif. |
| title_line_2 | string | YES | Completing thought. Italic, accent colour. Typically shorter than line_1 |
| title_display.line_1_style | enum | YES | Always "bold_display" |
| title_display.line_2_style | enum | YES | Always "italic_accent" |
| descriptor | string | YES | 1 sentence max 15 words. Benefit-focused promise. Not a description of the article |
| category_label | string | YES | ALL CAPS with · separator. Max 4 words. E.g. "LIFESTYLE · LIFE HACKS" |
| quote_banner.enabled | boolean | YES | true only when a single crystallising insight earns it. Default false |
| quote_banner.text | string or null | YES | Italic serif callout text. Not attributed to named person. null when disabled |

Validation: quote_banner.enabled:true and hook.type must both be "quote_banner" or neither — never mismatched.

---

## SECTION 4: HOOK

```json
"hook": {
  "type": "lede",
  "text": "You are not distracted. You are interrupted. There is a difference — and it matters.",
  "display": {
    "style": "bold_lede",
    "border": null
  }
}
```

| Field | Type | Required | Enum Values | Rules |
|---|---|---|---|---|
| type | enum | YES | "quote_banner" or "lede" | quote_banner = italic quote with left border. lede = bold paragraph |
| text | string | YES | | Max 3 sentences. No generic openers |
| display.style | enum | YES | "italic_quote" or "bold_lede" | Maps to type |
| display.border | enum or null | YES | "left_accent" or null | left_accent only for quote_banner type |

---

## SECTION 5: SECTIONS ARRAY

Each section object:

```json
{
  "section_id": "sec_lf_01",
  "title": "The Interruption Tax Nobody is Counting",
  "anchor": "interruption-tax",
  "emoji": "📵",
  "label": "FOCUS",
  "expansion_pattern": "A",
  "content_option": "2",
  "body": {},
  "ambient_card": null,
  "deep_dive_button": null,
  "sub_sections": null
}
```

| Field | Type | Required | Enum Values | Rules |
|---|---|---|---|---|
| section_id | string | YES | | Format: sec_{abbr}_{nn}. Unique within article |
| title | string | YES | | Max 8 words. Specific promise. Works standalone |
| anchor | string | YES | | URL-safe slug |
| emoji | string | YES | | Single emoji, semantic not decorative |
| label | string | YES | | 1–2 words ALL CAPS. Accent colour letter-spaced |
| expansion_pattern | enum | YES | "A" or "B" | A = inline. B = sub-section cards |
| content_option | enum | YES | "1","2","3","4","5","B" | Determines body sub-schema |
| body | object | YES | | Typed per content_option (see 5.1–5.6) |
| ambient_card | object or null | YES | | Populated only for content_option "2" |
| deep_dive_button | object or null | YES | | Populated only when sub_sections present |
| sub_sections | array or null | YES | | null when expansion_pattern "A" |

---

## SECTION 5.1: BODY — OPTION 1 (PURE NARRATIVE)

```json
"body": {
  "option": "1",
  "paragraphs": [
    {
      "text": "Most to-do lists fail because they try to capture and prioritize simultaneously — two completely different cognitive operations forced into one action.",
      "inline_formats": [
        { "phrase": "capture", "style": "italic" },
        { "phrase": "prioritize", "style": "italic" }
      ]
    },
    {
      "text": "Each evening: List 1 — dump everything on your mind without filtering. List 2 — just three tasks for tomorrow. Sleep on List 1. Work from List 2.",
      "inline_formats": [
        { "phrase": "List 1", "style": "bold" },
        { "phrase": "List 2", "style": "bold" }
      ]
    }
  ],
  "closing_line": "When those three tasks are done, the day is a win regardless of everything else."
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| paragraphs | array | YES | 1–2 items max |
| paragraphs[n].text | string | YES | Full paragraph text |
| paragraphs[n].inline_formats | array | YES | Empty [] if no formatting |
| inline_formats[n].phrase | string | YES | Exact phrase as it appears in text |
| inline_formats[n].style | enum | YES | "bold" or "italic" or "bold_italic" |
| closing_line | string or null | YES | 1 short landing sentence. null if paragraph closes cleanly |

---

## SECTION 5.2: BODY — OPTION 2 (NARRATIVE + AMBIENT STAT CARD)

```json
"body": {
  "option": "2",
  "paragraphs": [
    {
      "text": "Every interruption does not just cost 2 seconds. Research on cognitive recovery shows the brain takes 15–23 minutes to return to deep focus after an interruption. Ten interruptions a day means up to four hours of scattered thinking.",
      "inline_formats": [
        { "phrase": "15–23 minutes", "style": "bold" }
      ]
    }
  ],
  "closing_line": "You are not losing the notification moment. You are losing everything that follows."
}
```

ambient_card is a sibling field of body at section level (see Section 5B). Body paragraphs set up why the stat matters. Stat card renders between prose and deep dive button.

Same field rules as Option 1. 1–2 paragraphs.

---

## SECTION 5.3: BODY — OPTION 3 (POINT-WISE FACTS)

```json
"body": {
  "option": "3",
  "intro": "Three techniques that save dishes when something goes wrong:",
  "items": [
    {
      "label": "Over-salted dish",
      "body": "Add chunks of raw potato and simmer 10–15 minutes. The starch absorbs excess salt — chemistry, not folklore.",
      "label_style": "bold"
    },
    {
      "label": "Watery curry",
      "body": "Do not boil down on high heat. Dry-roast poppy seeds, grind fine, stir in. Thickens naturally without altering flavour.",
      "label_style": "bold"
    },
    {
      "label": "Perfect biryani grains",
      "body": "Add a few drops of lemon juice and a drop of oil to cooking water. Breaks down surface starch and keeps every grain distinct.",
      "label_style": "bold"
    }
  ],
  "list_style": "unordered_bullet",
  "closing_line": null
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| intro | string | YES | 1 sentence framing the list |
| items | array | YES | Min 3, max 5 |
| items[n].label | string | YES | 1–4 words. Named concept or technique |
| items[n].body | string | YES | 1–2 sentences explanation |
| items[n].label_style | enum | YES | Always "bold" for Option 3 |
| list_style | enum | YES | "unordered_bullet" or "ordered_number" |
| closing_line | string or null | YES | Optional 1-sentence synthesis |

---

## SECTION 5.4: BODY — OPTION 4 (NARRATIVE + EMBEDDED STEPS)

```json
"body": {
  "option": "4",
  "intro": "The 10-minute evening reset returns your home to neutral before sleep. Not cleaning — resetting. There is a difference.",
  "steps": [
    { "step_number": 1, "step_label": "Kitchen (3 min)", "step_body": "Rinse dishes, wipe counter, put away anything left out." },
    { "step_number": 2, "step_label": "Living space (2 min)", "step_body": "Clothes off the floor, surfaces cleared, cushions straightened." },
    { "step_number": 3, "step_label": "Tomorrow prep (2 min)", "step_body": "Bag packed, charger plugged in, keys on hook." },
    { "step_number": 4, "step_label": "Walk-through (1 min)", "step_body": "One pass through each room — close it down visually." },
    { "step_number": 5, "step_label": "Your signal (2 min)", "step_body": "Whatever marks the day as done for you." }
  ],
  "closing_line": "Ten minutes the night before saves 25 stressed minutes the next morning."
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| intro | string | YES | 2–3 sentences. What the process is and why it works |
| steps | array | YES | 2–6 max. If >6 needed, move to deep dive |
| steps[n].step_number | integer | YES | Sequential from 1 |
| steps[n].step_label | string | YES | Named label — not just a number. E.g. "Kitchen (3 min)" |
| steps[n].step_body | string | YES | 1 sentence. Specific and actionable |
| closing_line | string or null | YES | 1-sentence payoff. Recommended rarely null for Option 4 |

---

## SECTION 5.5: BODY — OPTION 5 (HIGHLIGHT BANNER + POINT-WISE)

```json
"body": {
  "option": "5",
  "highlight_banner": {
    "label": "The commute is curriculum.",
    "label_style": "accent_bold",
    "body": "Bengaluru average commute is 90 minutes a day. Audiobooks, podcasts, language apps — the commute will not get shorter. What you do with it is entirely yours.",
    "display": {
      "style": "ambient_banner",
      "background": "warm_tinted_surface",
      "border": "left_accent",
      "border_width": "3px"
    }
  },
  "items": [
    {
      "label": "Auto-pay everything fixed",
      "body": "Electricity, internet, insurance — set it and forget it. Zero mental overhead. Zero late fees.",
      "label_style": "bold"
    },
    {
      "label": "Sunday meta-work",
      "body": "30 minutes: meal plan, laundry started, devices charged, priorities written. Monday becomes a glide instead of a crash.",
      "label_style": "bold"
    }
  ],
  "list_style": "unordered_bullet",
  "closing_line": null
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| highlight_banner.label | string | YES | 3–7 words. Accent colour bold. The standout catchy phrase |
| highlight_banner.label_style | enum | YES | Always "accent_bold" |
| highlight_banner.body | string | YES | 2–3 sentences. Insight behind the label |
| highlight_banner.display.style | enum | YES | Always "ambient_banner" |
| highlight_banner.display.background | enum | YES | "warm_tinted_surface" |
| highlight_banner.display.border | enum | YES | Always "left_accent" |
| highlight_banner.display.border_width | string | YES | Always "3px" |
| items | array | YES | 2–4 items. Same schema as Option 3 |
| list_style | enum | YES | "unordered_bullet" or "ordered_number" |
| closing_line | string or null | YES | Optional |

---

## SECTION 5.6: BODY — OPTION B (SUB-SECTION CARDS)

Used only when expansion_pattern is "B".

```json
"body": {
  "option": "B",
  "intro": "Indian flavours were made for this. Each card below opens the full step-by-step recipe.",
  "card_grid": {
    "display": "grid",
    "columns": "auto_fill_200px",
    "items": [
      {
        "sub_section_id": "sub_cf_01",
        "card_title": "Dal Miso",
        "card_summary": "Stir 1 tsp white miso into blended masoor off the heat. Sesame oil drizzle. Mind-bending depth in 15 minutes.",
        "card_tag": "Recipe",
        "card_tag_style": "accent_label",
        "cta_label": "Full recipe →"
      },
      {
        "sub_section_id": "sub_cf_02",
        "card_title": "Avocado Paratha",
        "card_summary": "Mashed avocado with chilli, cumin, lime. Aloo paratha technique — creamier, richer, addictive.",
        "card_tag": "Recipe",
        "card_tag_style": "accent_label",
        "cta_label": "Full recipe →"
      }
    ]
  }
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| intro | string | YES | 1–2 sentences framing the cards |
| card_grid.display | enum | YES | Always "grid" |
| card_grid.columns | enum | YES | "auto_fill_200px" or "two_col" or "three_col" |
| card_grid.items | array | YES | Min 2 |
| card.sub_section_id | string | YES | Must match an id in sub_sections array |
| card.card_title | string | YES | Max 6 words |
| card.card_summary | string | YES | 1–2 sentences. Genuinely useful teaser |
| card.card_tag | string | YES | "Recipe" or "Guide" or "Technique" |
| card.card_tag_style | enum | YES | Always "accent_label" |
| card.cta_label | string | YES | "Full recipe →" or "Full guide →" or "Read more →" |

---

## SECTION 5B: AMBIENT CARD SCHEMA

Sibling of body at section level. Populated only when content_option is "2". null for all other options.

```json
"ambient_card": {
  "type": "stat_card",
  "value": "28%",
  "value_style": "large_accent_numeral",
  "explanation": "India wellness market annual growth rate — nearly 4x the global average. Indians are investing in doing life better.",
  "source": "FICCI-EY / Global Wellness Institute, 2025–26",
  "source_style": "muted_parenthetical",
  "display": {
    "style": "ambient_card",
    "background": "warm_tinted_surface",
    "border": "left_accent",
    "border_width": "3px",
    "placement": "after_body_before_deep_dive"
  }
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| type | enum | YES | Always "stat_card" |
| value | string | YES | Large prominent display. E.g. "28%", "15–23 minutes", "72B" |
| value_style | enum | YES | Always "large_accent_numeral" |
| explanation | string | YES | 1–2 sentences. Muted tone |
| source | string | YES | Attribution in parenthetical |
| source_style | enum | YES | Always "muted_parenthetical" |
| display.style | enum | YES | Always "ambient_card" |
| display.background | enum | YES | "warm_tinted_surface" |
| display.border | enum | YES | "left_accent" |
| display.border_width | string | YES | "3px" or "4px" |
| display.placement | enum | YES | Always "after_body_before_deep_dive" |

---

## SECTION 5.7: DEEP DIVE BUTTON

```json
"deep_dive_button": {
  "label": "Deep dive: Renegotiate Your Phone Relationship",
  "sub_section_id": "sub_lf_02",
  "chevron": "›",
  "display": {
    "style": "outlined_pill_button",
    "chevron_animates": true,
    "chevron_animation": "rotate_90_on_open"
  }
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| label | string | YES | Format: "Deep dive: [Specific Topic]". Max 6 words after colon. Never "Read more" |
| sub_section_id | string | YES | Must match a sub_sections[n].id in this section |
| chevron | string | YES | Always "›" |
| display.style | enum | YES | Always "outlined_pill_button" |
| display.chevron_animates | boolean | YES | Always true |
| display.chevron_animation | enum | YES | Always "rotate_90_on_open" |

null when section has no sub_sections.

---

## SECTION 5C: SUB-SECTIONS ARRAY

Sub-section object top level:

```json
{
  "id": "sub_lm_01",
  "title": "The 5-Minute Night Ritual That Fixes Your Mornings",
  "type": "how_to_guide",
  "variant": "A",
  "word_count": 280,
  "summary": "Five minutes before sleep. One task written. Bag packed. One win noted. Wake up with direction instead of fog.",
  "display": {
    "panel_header_style": "dark_bar_with_back_button",
    "panel_body_style": "light_card_on_overlay"
  },
  "content": {},
  "ambient_card": null,
  "time_label": "5 minutes · Difficulty: Very Low",
  "images": []
}
```

| Field | Type | Required | Enum Values | Rules |
|---|---|---|---|---|
| id | string | YES | | Format: sub_{abbr}_{nn}. Unique within article |
| title | string | YES | | The h2 inside the deep dive panel |
| type | enum | YES | "how_to_guide" or "recipe_step_by_step" or "standalone_deepdive" | |
| variant | enum | YES | "A" or "B" or "C" | Determines content sub-schema |
| word_count | integer | YES | | 200–500 hard cap |
| summary | string | YES | | 1–2 sentences for parent card display |
| display.panel_header_style | enum | YES | "dark_bar_with_back_button" | |
| display.panel_body_style | enum | YES | "light_card_on_overlay" | |
| content | object | YES | | Typed per variant |
| ambient_card | object or null | YES | | Same schema as Section 5B. Can appear in deep dive |
| time_label | string or null | YES | | Required for recipe and how_to_guide types |
| images | array | YES | | Same schema as Section 8. Empty [] if none |

---

## SECTION 5C.1: SUB-SECTION CONTENT — VARIANT A (STEPPED PROCESS)

```json
"content": {
  "variant": "A",
  "intro": "Most people try to fix their mornings by waking up earlier. But the real lever is the night before. The brain does not fully switch off during sleep — it processes and consolidates. Give it something useful to work with.",
  "steps": [
    {
      "step_title": "Write Your One Thing",
      "step_heading_format": "step_n_dash_title",
      "step_body": "Not a list. One task. The task that, if accomplished tomorrow, would make the day a win regardless of everything else."
    },
    {
      "step_title": "Set Up the Morning",
      "step_heading_format": "step_n_dash_title",
      "step_body": "Bag packed. Keys on hook. Clothes decided. Alarm set with intention, not panic. Every eliminated decision is one less cognitive drain."
    },
    {
      "step_title": "Note One Win",
      "step_heading_format": "step_n_dash_title",
      "step_body": "One small thing that went well today. Not forced positivity — recalibration. Try it for two weeks."
    }
  ],
  "additional_section": {
    "heading": "The Phone-Free Morning Buffer",
    "body": "Urban Indian millennials who have adopted a 20-minute no-phone morning window consistently report better mood and clearer thinking. Guard that window. Warm water. Breathe. Then check your phone."
  },
  "closing_note": null
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| intro | string | YES | 2–3 sentences. Why before how |
| steps | array | YES | 2–6 items |
| steps[n].step_title | string | YES | Named step title. Not just "Step 1" |
| steps[n].step_heading_format | enum | YES | Always "step_n_dash_title" — renders as "Step N — [Title]" |
| steps[n].step_body | string | YES | 1–4 sentences. Specific and actionable |
| additional_section | object or null | YES | Optional extra concept after steps with its own heading and body |
| closing_note | string or null | YES | 1-sentence payoff |

---

## SECTION 5C.2: SUB-SECTION CONTENT — VARIANT B (INTRO + BOLD LIST)

```json
"content": {
  "variant": "B",
  "intro": "Your phone is an extremely well-engineered machine designed to maximise the time you spend on it. Every infinite scroll, every autoplay exists because your attention is the product being sold. Understanding this is not cynicism — it is useful information.",
  "section_heading": "Four Specific Changes",
  "items": [
    {
      "label": "Turn off all non-essential notifications",
      "body": "Every app that can interrupt you, will. Most should not. Takes 3 minutes. Reclaims hours.",
      "label_style": "bold_sentence"
    },
    {
      "label": "Move social apps off your home screen",
      "body": "Second-screen folder. The tiny friction breaks the automatic open-without-deciding reflex.",
      "label_style": "bold_sentence"
    },
    {
      "label": "Charge your phone outside your bedroom",
      "body": "Buy a cheap alarm clock. Screen time before sleep measurably degrades sleep quality, mood, and next-day focus.",
      "label_style": "bold_sentence"
    },
    {
      "label": "Set a digital evening cutoff",
      "body": "9:30 PM. After that, no work email or messages. Communicate it. Hold it. Your evenings quietly transform.",
      "label_style": "bold_sentence"
    }
  ],
  "list_style": "unordered_bullet",
  "closing_paragraph": "Protecting attention is at least as important as managing time. Four settings changes. That is where the recalculation starts.",
  "closing_paragraph_inline_formats": []
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| intro | string | YES | Max 3–4 lines. The hook and why — not a summary |
| section_heading | string | YES | h3 that groups the items |
| items | array | YES | 3–6 items |
| items[n].label | string | YES | The bold label phrase |
| items[n].body | string | YES | 1–3 sentences |
| items[n].label_style | enum | YES | Always "bold_sentence" — bold label + period + regular body |
| list_style | enum | YES | "unordered_bullet" or "ordered_number" |
| closing_paragraph | string or null | YES | 1–2 sentence synthesis after list |
| closing_paragraph_inline_formats | array | YES | Empty [] if no formatting |

---

## SECTION 5C.3: SUB-SECTION CONTENT — VARIANT C (MULTI-HEADED PROSE)

```json
"content": {
  "variant": "C",
  "intro": "Most to-do apps fail for the same reason: they make capturing tasks and prioritising them the same action. Your brain is trying to offload AND decide simultaneously — exhausting.",
  "sub_sections": [
    {
      "heading": "The Two-List System",
      "body": "List 1 — The Dump: everything on your mind. No filtering. No ordering. Just out. List 2 — The Day: three things only. Sleep on List 1. Work from List 2. List 2 is your contract with tomorrow.",
      "inline_formats": [
        { "phrase": "List 1 — The Dump", "style": "bold" },
        { "phrase": "List 2 — The Day", "style": "bold" }
      ],
      "has_list": true,
      "list": {
        "style": "unordered_bullet",
        "items": [
          { "label": "List 1 — The Dump", "body": "Everything on your mind. No filtering. No ordering. Just out.", "label_style": "bold" },
          { "label": "List 2 — The Day", "body": "Three things only. The three that must happen tomorrow. Everything else waits.", "label_style": "bold" }
        ]
      }
    },
    {
      "heading": "The Two-Minute Rule",
      "body": "For tasks under two minutes — do them now. Do not list them, do not schedule them. These tasks cost more mental energy sitting on a list than they do to simply complete.",
      "inline_formats": [],
      "has_list": false,
      "list": null
    },
    {
      "heading": "Batching for Indian Schedules",
      "body": "Group similar tasks together rather than interleaving them. All messages in two windows. All financial tasks in one weekly 15-minute session. All errands consolidated. Every context switch has a cost. Batching pays it once instead of repeatedly.",
      "inline_formats": [],
      "has_list": false,
      "list": null
    }
  ],
  "closing_line": null
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| intro | string | YES | 2–3 sentences. Context for what follows |
| sub_sections | array | YES | 2–4 items |
| sub_sections[n].heading | string | YES | h3. Named concept specifically |
| sub_sections[n].body | string | YES | 2–4 sentences |
| sub_sections[n].inline_formats | array | YES | Empty [] if no formatting |
| sub_sections[n].has_list | boolean | YES | true if sub-section contains an embedded list |
| sub_sections[n].list | object or null | YES | null when has_list false. Same schema as Option 3 items when true |
| closing_line | string or null | YES | Final 1-sentence payoff for entire deep dive |

---

## SECTION 6: QUICK REFERENCE

### Variant A — Single Column

```json
"quick_reference": {
  "variant": "A",
  "heading": "Quick Reference",
  "single_column": {
    "items": [
      "Revoke all non-essential notification permissions today — 3 minutes, one-time action",
      "Move social apps off your home screen into a second-screen folder",
      "Write tomorrow one most important task before sleeping tonight",
      "Set a digital evening cutoff and communicate it to your team",
      "Build one 15-minute offline window into your workday every day"
    ]
  },
  "two_column": null,
  "display": {
    "style": "dark_card",
    "heading_colour": "gold_accent",
    "item_prefix": "→",
    "item_prefix_colour": "accent"
  }
}
```

### Variant B — Two Column

```json
"quick_reference": {
  "variant": "B",
  "heading": "Your Quick-Start List",
  "single_column": null,
  "two_column": {
    "left_column": {
      "label": "Do Today",
      "items": [
        "Revoke all non-essential notification permissions",
        "Write tomorrow most important task",
        "Note one thing that went well today",
        "Move social apps to a second-screen folder",
        "Assign homes for your 5 most-misplaced items"
      ]
    },
    "right_column": {
      "label": "Do This Week",
      "items": [
        "Try the Two-List method for 5 days straight",
        "Set a digital evening cutoff and hold it",
        "Set up auto-pay for one recurring bill",
        "One commute per day with no audio",
        "10-minute evening reset every night before bed"
      ]
    }
  },
  "display": {
    "style": "dark_card",
    "heading_colour": "gold_accent",
    "column_label_colour": "accent",
    "item_prefix": "→",
    "item_prefix_colour": "accent"
  }
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| variant | enum | YES | "A" or "B" |
| heading | string | YES | "Quick Reference", "Start Here", "Your Action List", "Try These First", "Your Quick-Start List" |
| single_column | object or null | YES | Populated for Variant A. null for Variant B |
| two_column | object or null | YES | Populated for Variant B. null for Variant A |
| single_column.items | array | YES | 4–5 strings. Action verbs. Ordered immediate to commitment |
| two_column.*.label | string | YES | "Do Today" and "Do This Week" standard |
| two_column.*.items | array | YES | 4–5 items per column |
| display.style | enum | YES | Always "dark_card" |

Use Variant B when article content naturally splits into immediate actions vs week-commitment changes.

---

## SECTION 7: SOURCES

```json
"sources": [
  {
    "url": "https://upstox.com/news/upstox-originals/...",
    "type": "Finance Media",
    "is_branded": false,
    "used_in_content": true
  }
],
"content_sources": [
  "https://upstox.com/news/upstox-originals/..."
],
"excluded_sources": ["Reddit", "Quora"]
```

| Field | Type | Required | Rules |
|---|---|---|---|
| sources | array | YES | Every URL visited during research |
| sources[n].type | enum | YES | "Finance Media", "Food Blog", "Branded Blog", "Wellness Brand Blog", "Productivity Blog", "Productivity Media", "Lifestyle Blog", "Lifestyle Media", "Restaurant Blog", "Academic", "Health NGO", "Independent Blog", "Business Media", "Food Media", "Food App Blog" |
| sources[n].is_branded | boolean | YES | true if source is a brand own blog |
| sources[n].used_in_content | boolean | YES | true only if this source contributed to article |
| content_sources | array | YES | URLs of used_in_content:true sources only |
| excluded_sources | array | YES | Always includes "Reddit" and "Quora" |

---

## SECTION 8: IMAGES

```json
"images": [
  {
    "image_id": "img_lf_001",
    "before_lines_text": "The good news: fixing this does not require discipline or willpower.",
    "after_lines_text": "It requires a few deliberate changes, made once.",
    "image_source": "Recommended: royalty-free — Indian professional at desk, phone face-down, focused work",
    "is_external_cited_image_source": false,
    "cited_external_img_source": null,
    "safety_checks": {
      "is_sexually_explicit": false,
      "is_harmful": false,
      "is_abusive": false,
      "is_content_safe": true
    },
    "is_image_rendered": false,
    "image_content_source": "N/A — placeholder",
    "image_uri_source": null
  }
],
"images_ignored": [
  {
    "content_src": "https://source.com/article",
    "image_uri": "Shutterstock wellness image in article",
    "reason": "is_external_cited",
    "is_external_cited_image_source": true,
    "cited_external_img_source": "Shutterstock"
  }
]
```

| Field | Type | Required | Rules |
|---|---|---|---|
| image_id | string | YES | Format: img_{slug}_{sequence} |
| before_lines_text | string | YES | Exact 1–2 article lines immediately before image position |
| after_lines_text | string | YES | Exact 1–2 article lines immediately after image position |
| image_source | string | YES | Recommended search query or source description |
| is_external_cited_image_source | boolean | YES | true if source page credits image to a third party |
| cited_external_img_source | string or null | YES | "Shutterstock", "AFP", "Getty" etc. null if not cited |
| safety_checks.is_content_safe | boolean or "unknown" | YES | "unknown" triggers refinement pass — do not render |
| is_image_rendered | boolean | YES | true only if URI confirmed independently fetchable |
| images_ignored[n].reason | enum | YES | "cannot_fetch", "guard_rail", "is_external_cited", "sports_content", "person_identified", "explicit", "irrelevant", "unknown" |

---

## SECTION 9: NARRATIVE METADATA

```json
"tonal_arc": ["warm", "credibility", "instructional", "india_specific", "reflective"],
"content_option_sequence": ["1", "2", "3", "5", "1"]
```

| Field | Type | Required | Rules |
|---|---|---|---|
| tonal_arc | array | YES | One value per section in reading order. Values: "warm", "credibility", "instructional", "india_specific", "reflective", "actionable" |
| content_option_sequence | array | YES | One value per section. No two consecutive identical values → REJECT if violated |

Validation: tonal_arc.length and content_option_sequence.length must both equal sections.length.

---

## SECTION 10: FILE REFERENCES AND GENERATION META

```json
"file_references": {
  "md": "lifehacks_focus.md",
  "html": "lifehacks_focus.html",
  "json": "lifehacks_focus.json"
},
"generation_meta": {
  "generation_date": "2026-03-31",
  "model": "Claude (Anthropic)",
  "spec_versions": {
    "content_spec": "v3.0",
    "narration_flow_spec": "v1.1",
    "json_schema_spec": "v1.0"
  }
}
```

All three file_references fields required. All three spec_versions fields required.

---

## SECTION 11: DISPLAY TOKEN ENUM REFERENCE

All display-related enum values and their UI rendering intent:

| Token | Renders As |
|---|---|
| "ambient_card" | Warm tinted background, left accent border 3–4px, generous padding. Stat value large+accent. Explanation muted small. |
| "ambient_banner" | Same warm tinted background as ambient_card. Label in accent bold, body regular weight. Full column width. |
| "warm_tinted_surface" | Light themes: soft warm cream (accent at ~6% opacity). Dark themes: warm dark surface slightly lighter than page bg. Never white or stark. |
| "left_accent" | Accent-colour left border, full height of card or banner |
| "dark_card" | Dark background (hero colour), light text, accent-coloured headings and prefix symbols |
| "outlined_pill_button" | Border 1px solid, border-radius 6px, transparent bg. Hover: accent bg + white text |
| "dark_bar_with_back_button" | Dark header bar. Deep dive title left-aligned bold. Back button right-aligned muted. |
| "light_card_on_overlay" | White or light body area below dark header bar |
| "bold_display" | Large serif heavy weight — hero title line 1 |
| "italic_accent" | Italic serif, accent colour — hero title line 2 |
| "accent_label" | Small caps, letter-spaced, accent colour — card tags and section labels |
| "accent_bold" | Bold weight accent colour — Option 5 banner label phrase |
| "large_accent_numeral" | Large display size, bold, accent colour — stat card value |
| "muted_parenthetical" | Small, muted ink, italic — stat card source attribution |
| "bold_sentence" | Bold label + period + regular weight body — Variant B and Option 3 items |
| "step_n_dash_title" | Renders as "Step N — [Title]" at h3 level — Variant A steps |
| "italic_quote" | Italic serif with left accent border — quote banner hook |
| "bold_lede" | Slightly larger body text, elevated weight — lede hook paragraph |
| "grid" | CSS grid auto-fill — recipe and guide card layouts |
| "auto_fill_200px" | grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)) |

---

## SECTION 12: VALIDATION RULES SUMMARY

| Rule | Check | On Fail |
|---|---|---|
| Word cap | word_count <= 1200 | REJECT |
| Sub-section cap | sub_sections[n].word_count <= 500 | REJECT |
| Safety flags | All false except is_content_safe true | REJECT |
| Exclusive word tier | is_short_read and is_medium_content not both true | REJECT |
| Theme present | theme.primary exists and is valid enum | REJECT |
| Theme override reason | theme_override.used=true → reason non-null; used=false → reason null | REJECT |
| No consecutive options | content_option_sequence[n] != sequence[n+1] | REJECT |
| Quote consistency | hero.quote_banner.enabled matches hook.type | REJECT |
| Ambient card null | ambient_card is null when content_option != "2" | REJECT |
| Button null | deep_dive_button is null when sub_sections is null | REJECT |
| Card IDs valid | Every card_grid item sub_section_id matches a sub_sections id | REJECT |
| Array lengths | tonal_arc.length == content_option_sequence.length == sections.length | REJECT |
| File references | All three populated | REJECT |
| Excluded sources | Contains "Reddit" and "Quora" | REJECT |
| Steps max | Option 4 steps <= 6, Variant A steps <= 6 | REJECT |
| Items min/max | Option 3: 3–5, Option 5: 2–4, Variant B: 3–6 | REJECT |
| Sub-sections min | Pattern B requires sub_sections.length >= 2 | REJECT |

---

Schema version: 1.0 · March 2026
Works with: Content Spec v3.0 + Narration Flow Spec v1.1
All three specs must be present for a valid agent run.
