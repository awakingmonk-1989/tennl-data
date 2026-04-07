Given  constraint that **JSON schema integrity is non-negotiable**, best  setup for **generation only** is:

* **1 compact generation prompt**
* **1 compact-but-complete JSON schema spec placeholder**
* **no other spec/skill attachments in generation runtime**

That keeps strict renderer compliance while cutting the biggest prompt bloat from the current YAML.

---

## 1) Final compact generation YAML

````yaml
content_gen_novelty_v2:
  name: content_gen_novelty_v2
  version: 2

  system_prompt: |
    You are a high-quality content creator for an India-focused discovery platform.

    Goal:
    Generate one short-read article that is warm, specific, refreshing, safe, and worth reading or sharing.

    You must produce:
    1. A complete article in markdown
    2. One final JSON object in a fenced ```json block

    Runtime authority:
    - The runtime creative controls are authoritative for this run.
    - content_mode is article-level and must shape the overall article.
    - angle is the main framing lens.
    - tone is the emotional/style voice.
    - hook_style controls the opening hook.
    - Do not replace or override these unless blocked by safety.

    Hard safety rules:
    - Safe for broad audiences.
    - No sexual/adult content, hate, abuse, intimidation, harmful or illegal guidance, politics, war, sports, movies/TV, direct real private persons, or sensitive advice content.
    - No Reddit or Quora.
    - Synthesize; do not copy source text.
    - If a public professional is referenced, mask them in body text and keep identifying detail only in JSON metadata.

    Writing quality:
    - Write in a warm, sharp, grounded, non-generic voice.
    - Avoid template openings, clickbait, generic motivation, repetitive listicle style, filler transitions, and preachy tone.
    - Each section must feel independently useful.
    - Each section should follow: setup -> insight -> payoff.
    - Final section should feel reflective, not repetitive.
    - Quick Reference must be distilled from the article.

    Title and hook:
    - Use a strong 2-line title.
    - Add a short descriptor with a clear reader benefit.
    - Hook must be specific and engaging, not generic.
    - Avoid openings like “In today’s fast-paced world”, “We all know”, “It is important to note”.

    UI alignment:
    - You will receive allowed UI skeleton options for this run.
    - Choose the single best UI skeleton based on the content you generate.
    - Let article structure and section rhythm align naturally with that choice.
    - Do not describe HTML, CSS, JS, rendering logic, or frontend implementation.

    Structure rules:
    - One PAGE per run.
    - 3 to 5 POSTS/sections in reading order.
    - Use the provided content_option_sequence in order.
    - Do not repeat adjacent content options.
    - Each section must clearly fit its assigned content option.

    Deep dives:
    - Optional, not mandatory.
    - Use only when justified: 2+ parallel items/concepts, summary-only treatment would be weak, and full inline treatment would exceed the word budget.
    - If used, attach deep-dive content only to its parent section in JSON.

    Output integrity:
    - The JSON schema is mandatory and authoritative.
    - Do not invent fields.
    - Do not omit required fields.
    - When a field is optional and not applicable, set it to null.
    - Keep PAGE vs POST vs DEEP DIVE hierarchy exact.
    - Keep markdown and JSON aligned to the same article.
    - Keep images empty for this batch.

  runtime_input_block: |
    topic: {topic}
    sub_topic: {sub_topic}
    sub_topic_description: {sub_topic_description}
    content_variant: {content_variant}

    ranked_input:
      rank: {rank}
      topic_cluster: {ranked_topic}
      why_it_makes_the_cut_now: {why_it_makes_the_cut_now}
      best_fit_formats: {best_fit_formats}

    creative_pools:
      intent_profile: {intent_profile}
      content_mode_pool: {content_mode_pool}
      angle_pool: {angle_pool}
      tone_pool: {tone_pool}
      hook_style_pool: {hook_style_pool}
      quality_constraints.must_include: {must_include}
      quality_constraints.avoid: {avoid}

    runtime_creative_controls:
      content_mode: {content_mode}
      angle: {angle}
      tone: {tone}
      hook_style: {hook_style}

    structure_controls:
      content_option_sequence: {content_option_sequence}
      quick_reference_variant: {quick_reference_variant}
      allowed_ui_skeletons: {allowed_ui_skeletons}

    batch_controls:
      target_word_range: {target_word_range}
      hard_word_limit: {hard_word_limit}
      images_enabled: false
      excluded_sources: ["Reddit", "Quora"]

  output_block: |
    Produce in this exact order:
    1. Markdown article
    2. One fenced ```json block with the final JSON object

    Markdown order:
    ---
    # [Title Line 1]
    ## *[Title Line 2]*

    > Content Label: [label]
    > Safety: ✅ Safe

    **Category:** [category_path]
    **Audience:** [target_audience]

    ---

    [Hook]

    ---

    ## [emoji] [LABEL]
    ### [Section Title]

    [Section body]

    ---

    [Repeat for remaining sections]

    ---

    **Quick Reference**
    [Distilled action list]

    ---

    **Sources**
    - [Sources if applicable]

    ---

    Critical requirements:
    - Respect runtime creative controls throughout.
    - Choose exactly one UI skeleton from allowed_ui_skeletons and reflect it in JSON.
    - Every section must be fully written.
    - Deep dives are optional and only when justified.
    - Keep images arrays empty.
    - Do not exceed the hard word limit.

  attachments_block: |
    [JSON_SCHEMA_SPEC_COMPACT]
    {json_schema_spec_compact}
````

---

## 2) Compact-but-complete JSON schema spec

This is the version to pass as `{json_schema_spec_compact}`.
It keeps **all sections / fields / validation intent**, but removes most long prose. It is derived from your full schema, not a weakened version.

````markdown
# Content JSON Schema Spec — Compact Runtime Version
Version: 1.0
Purpose: Mandatory output contract for generation. UI reads fields, never prose.
Rule: Do not invent fields. Do not omit required fields. Use null for optional non-applicable fields.

## 0. ROOT ENVELOPE
Required root object:
```json
{
  "$schema": "content-schema-v1.0",
  "article_id": "",
  "variant": "",
  "content_label": "",
  "topic": "",
  "sub_topic": "",
  "slug": "",
  "category_path": "",
  "target_audience": "",
  "generation_controls": {},
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
````

## 0A. GENERATION CONTROLS (required)

```json
"generation_controls": {
  "intent_profile": [],
  "available_pools": {
    "content_mode_pool": [],
    "angle_pool": [],
    "tone_pool": [],
    "hook_style_pool": []
  },
  "selected_runtime_values": {
    "content_mode": "",
    "angle": "",
    "tone": "",
    "hook_style": ""
  },
  "runtime_override": {
    "used": false,
    "reason": null
  }
}
```

Validation:

* selected_runtime_values must belong to their pools
* runtime_override.used=true => reason required
* runtime_override.used=false => reason=null

## 0B. THEME (required)

```json
"theme": {
  "primary": "",
  "secondary": null
},
"theme_override": {
  "used": false,
  "reason": null
}
```

theme.primary enum:

* Knowledge Sharing
* Compare & Contrast
* Best Practices
* Safe Tips / Preventive Insights
* Optimal Experiences
* Habit Formation / Behavior Change
* Cultural / India-specific Nuance
* Myth vs Reality
* Quick Wins / Immediate Actions

theme.secondary enum or null:

* Storytelling / Narrative hook
* Data-backed credibility
* Emotional relatability
* Curiosity-driven framing
* Experiment / Try-this framing

## 1. WORD COUNT META

```json
"word_count_meta": {
  "word_count": 0,
  "reading_time_minutes": 0,
  "is_short_read": false,
  "is_medium_content": true
}
```

Validation:

* word_count <= 1200
* is_short_read and is_medium_content cannot both be true

## 2. CONTENT SAFETY

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
  "has_sensitive_advice_content": false,
  "masked_persons": []
}
```

masked_persons item:

```json
{
  "masked_as": "",
  "real_name": "",
  "context": ""
}
```

## 3. HERO

```json
"hero": {
  "title_line_1": "",
  "title_line_2": "",
  "title_display": {
    "line_1_style": "bold_display",
    "line_2_style": "italic_accent"
  },
  "descriptor": "",
  "category_label": "",
  "quote_banner": {
    "enabled": false,
    "text": null
  }
}
```

## 4. HOOK

```json
"hook": {
  "type": "lede",
  "text": "",
  "display": {
    "style": "bold_lede",
    "border": null
  }
}
```

Validation:

* hook.type enum: quote_banner | lede
* display.style enum: italic_quote | bold_lede
* display.border enum/null: left_accent | null
* hero.quote_banner.enabled must match hook.type

## 5. SECTIONS ARRAY

Each section:

```json
{
  "section_id": "",
  "title": "",
  "anchor": "",
  "emoji": "",
  "label": "",
  "expansion_pattern": "A",
  "content_option": "1",
  "body": {},
  "ambient_card": null,
  "deep_dive_button": null,
  "sub_sections": null
}
```

Validation:

* expansion_pattern enum: A | B
* content_option enum: 1 | 2 | 3 | 4 | 5 | B

### 5.1 BODY OPTION 1

```json
"body": {
  "option": "1",
  "paragraphs": [
    { "text": "", "inline_formats": [] }
  ],
  "closing_line": null
}
```

### 5.2 BODY OPTION 2

```json
"body": {
  "option": "2",
  "paragraphs": [
    { "text": "", "inline_formats": [] }
  ],
  "closing_line": null
}
```

### 5.3 BODY OPTION 3

```json
"body": {
  "option": "3",
  "intro": "",
  "items": [
    { "label": "", "body": "", "label_style": "bold" }
  ],
  "list_style": "unordered_bullet",
  "closing_line": null
}
```

Validation: items 3–5

### 5.4 BODY OPTION 4

```json
"body": {
  "option": "4",
  "intro": "",
  "steps": [
    { "step_number": 1, "step_label": "", "step_body": "" }
  ],
  "closing_line": null
}
```

Validation: steps 2–6

### 5.5 BODY OPTION 5

```json
"body": {
  "option": "5",
  "highlight_banner": {
    "label": "",
    "label_style": "accent_bold",
    "body": "",
    "display": {
      "style": "ambient_banner",
      "background": "warm_tinted_surface",
      "border": "left_accent",
      "border_width": "3px"
    }
  },
  "items": [
    { "label": "", "body": "", "label_style": "bold" }
  ],
  "list_style": "unordered_bullet",
  "closing_line": null
}
```

Validation: items 2–4

### 5.6 BODY OPTION B

```json
"body": {
  "option": "B",
  "intro": "",
  "card_grid": {
    "display": "grid",
    "columns": "auto_fill_200px",
    "items": [
      {
        "sub_section_id": "",
        "card_title": "",
        "card_summary": "",
        "card_tag": "",
        "card_tag_style": "accent_label",
        "cta_label": ""
      }
    ]
  }
}
```

Validation:

* card_grid.items min 2
* each sub_section_id must match a sub_sections id

### 5B. AMBIENT CARD

Used only when content_option = "2"; else null.

```json
"ambient_card": {
  "type": "stat_card",
  "value": "",
  "value_style": "large_accent_numeral",
  "explanation": "",
  "source": "",
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

### 5.7 DEEP DIVE BUTTON

Used only when sub_sections present; else null.

```json
"deep_dive_button": {
  "label": "",
  "sub_section_id": "",
  "chevron": "›",
  "display": {
    "style": "outlined_pill_button",
    "chevron_animates": true,
    "chevron_animation": "rotate_90_on_open"
  }
}
```

### 5C. SUB-SECTIONS

```json
{
  "id": "",
  "title": "",
  "type": "",
  "variant": "A",
  "word_count": 0,
  "summary": "",
  "display": {
    "panel_header_style": "dark_bar_with_back_button",
    "panel_body_style": "light_card_on_overlay"
  },
  "content": {},
  "ambient_card": null,
  "time_label": null,
  "images": []
}
```

Validation:

* type enum: how_to_guide | recipe_step_by_step | standalone_deepdive
* variant enum: A | B | C
* word_count <= 500

#### 5C.1 VARIANT A

```json
"content": {
  "variant": "A",
  "intro": "",
  "steps": [
    {
      "step_title": "",
      "step_heading_format": "step_n_dash_title",
      "step_body": ""
    }
  ],
  "additional_section": null,
  "closing_note": null
}
```

Validation: steps 2–6

#### 5C.2 VARIANT B

```json
"content": {
  "variant": "B",
  "intro": "",
  "section_heading": "",
  "items": [
    { "label": "", "body": "", "label_style": "bold_sentence" }
  ],
  "list_style": "unordered_bullet",
  "closing_paragraph": null,
  "closing_paragraph_inline_formats": []
}
```

Validation: items 3–6

#### 5C.3 VARIANT C

```json
"content": {
  "variant": "C",
  "intro": "",
  "sub_sections": [
    {
      "heading": "",
      "body": "",
      "inline_formats": [],
      "has_list": false,
      "list": null
    }
  ],
  "closing_line": null
}
```

Validation: sub_sections 2–4

## 6. QUICK REFERENCE

```json
"quick_reference": {
  "variant": "A",
  "heading": "",
  "single_column": { "items": [] },
  "two_column": null,
  "display": {
    "style": "dark_card",
    "heading_colour": "gold_accent",
    "item_prefix": "→",
    "item_prefix_colour": "accent"
  }
}
```

or

```json
"quick_reference": {
  "variant": "B",
  "heading": "",
  "single_column": null,
  "two_column": {
    "left_column": { "label": "Do Today", "items": [] },
    "right_column": { "label": "Do This Week", "items": [] }
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

## 7. SOURCES

```json
"sources": [
  {
    "url": "",
    "type": "",
    "is_branded": false,
    "used_in_content": true
  }
],
"content_sources": [],
"excluded_sources": ["Reddit", "Quora"]
```

## 8. IMAGES

For this batch, keep:

```json
"images": [],
"images_ignored": []
```

If images are enabled in future, use full image schema from canonical spec.

## 9. NARRATIVE METADATA

```json
"tonal_arc": [],
"content_option_sequence": []
```

Validation:

* both lengths must equal sections.length
* no consecutive identical values in content_option_sequence

## 10. FILE REFERENCES + GENERATION META

```json
"file_references": {
  "md": "",
  "json": ""
},
"generation_meta": {
  "generation_date": "",
  "model": "",
  "spec_versions": {
    "content_spec": "v3.0",
    "narration_flow_spec": "v1.1",
    "json_schema_spec": "v1.0"
  }
}
```

## 11. DISPLAY TOKEN ENUMS

Allowed display tokens:

* ambient_card
* ambient_banner
* warm_tinted_surface
* left_accent
* dark_card
* outlined_pill_button
* dark_bar_with_back_button
* light_card_on_overlay
* bold_display
* italic_accent
* accent_label
* accent_bold
* large_accent_numeral
* muted_parenthetical
* bold_sentence
* step_n_dash_title
* italic_quote
* bold_lede
* grid
* auto_fill_200px

## 12. VALIDATION SUMMARY

Reject if any of the following fail:

* word_count > 1200
* sub_section word_count > 500
* safety flags invalid
* has_sensitive_advice_content != false
* selected_runtime_values not in pools
* theme invalid
* theme_override invalid
* consecutive identical content options
* quote mismatch between hero and hook
* ambient_card present when content_option != 2
* deep_dive_button present when sub_sections null
* card_grid sub_section_ids invalid
* tonal_arc/content_option_sequence/sections length mismatch
* file_references missing
* excluded_sources missing Reddit or Quora
* Option 4 steps > 6
* Variant A steps > 6
* Option 3 items not in 3–5
* Option 5 items not in 2–4
* Variant B items not in 3–6
* Pattern B with sub_sections length < 2

````

---

## 3) Small snippet that clubs both for final prompt

Use this when building the final formatted prompt in code:

```python
final_prompt = f"""
{generation_yaml_system_prompt}

{runtime_input_block}

[JSON_SCHEMA_SPEC_COMPACT]
{json_schema_spec_compact}

{output_block}
""".strip()
````

Or if you want it aligned to your YAML placeholders:

```yaml
attachments_block: |
  [JSON_SCHEMA_SPEC_COMPACT]
  {json_schema_spec_compact}
```

---

## Final lock-in

### Pass in generation runtime

* compact generation prompt
* compact-but-complete JSON schema spec

### Do not pass in generation runtime

* long content spec
* long narration spec
* generation skill
* sample markdown/json reference blocks

That is the best cost/compliance tradeoff for your batch workflow given the UI renderer’s strict dependency on JSON integrity.

Next, send the moderation prompt.
