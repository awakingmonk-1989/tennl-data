# SKILL: Schema Validation
## India Discovery Platform — JSON Output Validation Against Schema Spec
### Version 1.0 · March 2026

---

## PURPOSE

This skill validates the complete JSON output from Content Generation
against JSON Schema Spec v1.0. It runs last in the pipeline — after
Content Moderation PASS and Creativity & Narration PASS.

It is a structural validator, not a content evaluator. It checks:
- Every required field is present and has the correct type
- Every enum field contains a permitted value
- Every conditional rule is satisfied (ambient_card null when not option 2, etc.)
- Array lengths match requirements
- Nested hierarchy is correct (page / post / deep dive levels)
- All validation rules from JSON Schema Spec v1.0 Section 12 pass

**Spec this skill references:**
- `/specs/json_schema_spec_v1.md` — all sections, especially Section 12

---

## INPUT

The complete JSON object from the Content Generation skill
(after Content Moderation PASS and Creativity & Narration PASS or revision).

---

## VALIDATION SEQUENCE

Run every rule in order. Document every failure — do not stop at the first.
Produce a complete report of all failures before returning.

---

### BLOCK 1: ROOT ENVELOPE

```
RULE 1.1  $schema field present and equals "content-schema-v1.0"
RULE 1.2  article_id: string, non-empty, format: TOPIC_SUBTOPIC_NNN
RULE 1.3  variant: enum — one of:
            "CURATED_WEB_WITH_IMAGES"
            "CURATED_WEB_NO_IMAGES"
            "AI_GENERATED"
RULE 1.4  content_label: enum — one of:
            "CURATED CONTENT"
            "AI GENERATED"
RULE 1.5  topic: string, non-empty
RULE 1.6  sub_topic: string, non-empty
RULE 1.7  slug: string, URL-safe, no spaces
RULE 1.8  category_path: string, contains › separators
RULE 1.9  target_audience: string, non-empty
RULE 1.10 All nine fields above present — none omitted
```

---

### BLOCK 2: WORD COUNT META

```
RULE 2.1  word_count: integer, 1–1200
          → If > 1200: HARD FAIL — article exceeds maximum word count
RULE 2.2  reading_time_minutes: integer, equals ceil(word_count / 200)
RULE 2.3  is_short_read: boolean
RULE 2.4  is_medium_content: boolean
RULE 2.5  Mutual exclusivity: is_short_read and is_medium_content
          cannot both be true simultaneously
RULE 2.6  is_short_read is true only if word_count < 500
RULE 2.7  is_medium_content is true only if 500 <= word_count <= 1000
RULE 2.8  If word_count > 1000: both flags false (long read — no tag)
```

---

### BLOCK 3: CONTENT SAFETY

```
RULE 3.1  is_sexually_explicit: boolean, must equal false
RULE 3.2  is_harmful: boolean, must equal false
RULE 3.3  is_abusive: boolean, must equal false
RULE 3.4  is_intimidating: boolean, must equal false
RULE 3.5  is_content_safe: boolean, must equal true
RULE 3.6  has_real_person_references: boolean, must equal false
RULE 3.7  has_sports_references: boolean, must equal false
RULE 3.8  has_movie_references: boolean, must equal false
RULE 3.9  masked_persons: array (empty [] is valid)
RULE 3.10 Each masked_persons entry must have:
            masked_as: string, non-empty
            real_name: string, non-empty
            context: string, non-empty
```

---

### BLOCK 4: HERO

```
RULE 4.1  title_line_1: string, non-empty
RULE 4.2  title_line_2: string, non-empty
RULE 4.3  title_display.line_1_style: must equal "bold_display"
RULE 4.4  title_display.line_2_style: must equal "italic_accent"
RULE 4.5  descriptor: string, word count <= 15
RULE 4.6  category_label: string, ALL CAPS, contains ·, max 4 words
RULE 4.7  quote_banner.enabled: boolean
RULE 4.8  quote_banner.text: string when enabled is true,
          null when enabled is false
          → If enabled:true and text is null: FAIL
          → If enabled:false and text is non-null: FAIL
```

---

### BLOCK 5: HOOK

```
RULE 5.1  type: enum — "quote_banner" or "lede"
RULE 5.2  text: string, non-empty
RULE 5.3  display.style: enum —
            "italic_quote" when type is "quote_banner"
            "bold_lede" when type is "lede"
RULE 5.4  display.border: enum or null —
            "left_accent" when type is "quote_banner"
            null when type is "lede"
RULE 5.5  CROSS-CHECK: hero.quote_banner.enabled must match hook.type
            If hero.quote_banner.enabled is true:
              hook.type must be "quote_banner"
            If hero.quote_banner.enabled is false:
              hook.type must be "lede"
            Mismatch = FAIL
```

---

### BLOCK 6: SECTIONS ARRAY (POSTS)

```
RULE 6.1  sections: array, length 3–5
          → < 3 posts: FAIL
          → > 5 posts: FAIL

For each section object:

RULE 6.2  section_id: string, format sec_{abbr}_{nn}, unique within article
RULE 6.3  title: string, word count <= 8
RULE 6.4  anchor: string, URL-safe slug
RULE 6.5  emoji: string, exactly one emoji character
RULE 6.6  label: string, 1–2 words, validates as uppercase
RULE 6.7  expansion_pattern: enum — "A" or "B"
RULE 6.8  content_option: enum — "1","2","3","4","5","B"
RULE 6.9  body: object, non-null, must match schema for content_option value
RULE 6.10 ambient_card: must be null when content_option != "2"
          → If content_option is "2" and ambient_card is null: FAIL
          → If content_option is not "2" and ambient_card is non-null: FAIL
RULE 6.11 deep_dive_button: must be null when sub_sections is null
          → If sub_sections is null and deep_dive_button is non-null: FAIL
          → If sub_sections is non-null and deep_dive_button is null: FAIL
RULE 6.12 sub_sections: null when expansion_pattern is "A"
          → If expansion_pattern "A" and sub_sections non-null: FAIL
          → If expansion_pattern "B" and sub_sections null: FAIL
RULE 6.13 expansion_pattern "B" requires sub_sections.length >= 2
```

---

### BLOCK 7: BODY SCHEMAS PER CONTENT OPTION

```
OPTION 1 BODY:
RULE 7.1.1  option: "1"
RULE 7.1.2  paragraphs: array, length 1–2
RULE 7.1.3  Each paragraph: text (string), inline_formats (array)
RULE 7.1.4  Each inline_format: phrase (string), style (enum: "bold","italic","bold_italic")
RULE 7.1.5  closing_line: string or null

OPTION 2 BODY:
RULE 7.2.1  option: "2"
RULE 7.2.2  paragraphs: array, length 1–2 (same schema as option 1)
RULE 7.2.3  closing_line: string or null

OPTION 3 BODY:
RULE 7.3.1  option: "3"
RULE 7.3.2  intro: string, non-empty
RULE 7.3.3  items: array, length 3–5
RULE 7.3.4  Each item: label (string), body (string), label_style ("bold")
RULE 7.3.5  list_style: enum — "unordered_bullet" or "ordered_number"
RULE 7.3.6  closing_line: string or null

OPTION 4 BODY:
RULE 7.4.1  option: "4"
RULE 7.4.2  intro: string, non-empty
RULE 7.4.3  steps: array, length 2–6
            → > 6 steps: FAIL
RULE 7.4.4  Each step: step_number (integer, sequential from 1),
            step_label (string, non-empty), step_body (string)
RULE 7.4.5  closing_line: string or null

OPTION 5 BODY:
RULE 7.5.1  option: "5"
RULE 7.5.2  highlight_banner.label: string, word count 3–7
RULE 7.5.3  highlight_banner.label_style: must equal "accent_bold"
RULE 7.5.4  highlight_banner.body: string, non-empty
RULE 7.5.5  highlight_banner.display.style: must equal "ambient_banner"
RULE 7.5.6  highlight_banner.display.background: must equal "warm_tinted_surface"
RULE 7.5.7  highlight_banner.display.border: must equal "left_accent"
RULE 7.5.8  highlight_banner.display.border_width: must equal "3px"
RULE 7.5.9  items: array, length 2–4
RULE 7.5.10 list_style: enum — "unordered_bullet" or "ordered_number"

OPTION B BODY:
RULE 7.6.1  option: "B"
RULE 7.6.2  intro: string, non-empty
RULE 7.6.3  card_grid.display: must equal "grid"
RULE 7.6.4  card_grid.columns: enum —
            "auto_fill_200px" or "two_col" or "three_col"
RULE 7.6.5  card_grid.items: array, length >= 2
RULE 7.6.6  Each card item:
              sub_section_id: string, non-empty
              card_title: string, word count <= 6
              card_summary: string, non-empty
              card_tag: string, non-empty
              card_tag_style: must equal "accent_label"
              cta_label: string, non-empty
RULE 7.6.7  CROSS-CHECK: Every card.sub_section_id must match an id
            in the parent section's sub_sections array
            → Any card sub_section_id with no matching sub_sections id: FAIL
```

---

### BLOCK 8: AMBIENT CARD

```
(Only evaluated when content_option is "2")

RULE 8.1  type: must equal "stat_card"
RULE 8.2  value: string, non-empty
RULE 8.3  value_style: must equal "large_accent_numeral"
RULE 8.4  explanation: string, non-empty
RULE 8.5  source: string, non-empty
RULE 8.6  source_style: must equal "muted_parenthetical"
RULE 8.7  display.style: must equal "ambient_card"
RULE 8.8  display.background: must equal "warm_tinted_surface"
RULE 8.9  display.border: must equal "left_accent"
RULE 8.10 display.border_width: "3px" or "4px"
RULE 8.11 display.placement: must equal "after_body_before_deep_dive"
```

---

### BLOCK 9: DEEP DIVE BUTTON

```
(Only evaluated when sub_sections is non-null)

RULE 9.1  label: string, format "Deep dive: [topic]"
          → Must start with "Deep dive: "
          → Words after colon: max 6
          → Must not equal "Deep dive: Read more" or similar generic labels
RULE 9.2  sub_section_id: string, must match an id in sub_sections array
RULE 9.3  chevron: must equal "›"
RULE 9.4  display.style: must equal "outlined_pill_button"
RULE 9.5  display.chevron_animates: must equal true
RULE 9.6  display.chevron_animation: must equal "rotate_90_on_open"
```

---

### BLOCK 10: SUB-SECTIONS (DEEP DIVES)

```
For each sub_section object:

RULE 10.1  id: string, format sub_{abbr}_{nn}, unique within article
RULE 10.2  title: string, non-empty
RULE 10.3  type: enum — "how_to_guide","recipe_step_by_step","standalone_deepdive"
RULE 10.4  variant: enum — "A","B","C"
RULE 10.5  word_count: integer, 200–500
           → > 500: HARD FAIL
           → < 200: FAIL (too short to add value)
RULE 10.6  summary: string, non-empty (used for parent card display)
RULE 10.7  display.panel_header_style: must equal "dark_bar_with_back_button"
RULE 10.8  display.panel_body_style: must equal "light_card_on_overlay"
RULE 10.9  content: object, non-null, must match schema for variant value
RULE 10.10 ambient_card: object or null (same schema as Block 8)
RULE 10.11 time_label: string, non-null for types "how_to_guide" and
           "recipe_step_by_step"
           → If type is how_to_guide or recipe_step_by_step and
             time_label is null: FAIL
RULE 10.12 images: array (empty [] is valid)

SUB-SECTION CONTENT — VARIANT A:
RULE 10.A.1  variant: "A"
RULE 10.A.2  intro: string, non-empty
RULE 10.A.3  steps: array, length 2–6
RULE 10.A.4  Each step: step_title (string), step_heading_format
             (must equal "step_n_dash_title"), step_body (string)
RULE 10.A.5  additional_section: object or null
             If non-null: heading (string) and body (string) required
RULE 10.A.6  closing_note: string or null

SUB-SECTION CONTENT — VARIANT B:
RULE 10.B.1  variant: "B"
RULE 10.B.2  intro: string, non-empty
RULE 10.B.3  section_heading: string, non-empty
RULE 10.B.4  items: array, length 3–6
RULE 10.B.5  Each item: label (string), body (string),
             label_style (must equal "bold_sentence")
RULE 10.B.6  list_style: enum — "unordered_bullet" or "ordered_number"
RULE 10.B.7  closing_paragraph: string or null
RULE 10.B.8  closing_paragraph_inline_formats: array (empty [] valid)

SUB-SECTION CONTENT — VARIANT C:
RULE 10.C.1  variant: "C"
RULE 10.C.2  intro: string, non-empty
RULE 10.C.3  sub_sections: array, length 2–4
RULE 10.C.4  Each sub-section: heading (string), body (string),
             inline_formats (array), has_list (boolean),
             list (object or null)
RULE 10.C.5  If has_list is true: list must be non-null with
             style and items fields
RULE 10.C.6  If has_list is false: list must be null
RULE 10.C.7  closing_line: string or null
```

---

### BLOCK 11: QUICK REFERENCE

```
RULE 11.1  variant: enum — "A" or "B"
RULE 11.2  heading: string, non-empty
RULE 11.3  single_column: populated when variant "A", null when variant "B"
RULE 11.4  two_column: populated when variant "B", null when variant "A"
RULE 11.5  Variant A: single_column.items array, length 4–5
RULE 11.6  Variant B: two_column.left_column.items array, length 4–5
RULE 11.7  Variant B: two_column.right_column.items array, length 4–5
RULE 11.8  Variant B: left_column.label non-empty, right_column.label non-empty
RULE 11.9  display.style: must equal "dark_card"
RULE 11.10 display.item_prefix: must equal "→"
```

---

### BLOCK 12: NARRATIVE METADATA

```
RULE 12.1  tonal_arc: array, each value one of:
           "warm","credibility","instructional","india_specific",
           "reflective","actionable"
RULE 12.2  content_option_sequence: array, each value one of:
           "1","2","3","4","5","B"
RULE 12.3  LENGTH MATCH: tonal_arc.length must equal sections.length
RULE 12.4  LENGTH MATCH: content_option_sequence.length must equal sections.length
RULE 12.5  NO CONSECUTIVE: content_option_sequence[n] must not equal
           content_option_sequence[n+1] for any n
           → Any consecutive identical values: FAIL
RULE 12.6  CONSISTENCY: content_option_sequence[n] must match
           sections[n].content_option for every n
```

---

### BLOCK 13: SOURCES & EXCLUSIONS

```
RULE 13.1  sources: array (empty [] valid for AI_GENERATED variant)
RULE 13.2  Each source: url (string), type (enum from permitted list),
           is_branded (boolean), used_in_content (boolean)
RULE 13.3  type enum permitted values:
           "Finance Media","Food Blog","Branded Blog","Wellness Brand Blog",
           "Productivity Blog","Productivity Media","Lifestyle Blog",
           "Lifestyle Media","Restaurant Blog","Academic","Health NGO",
           "Independent Blog","Business Media","Food Media","Food App Blog"
RULE 13.4  content_sources: array, subset of sources[].url values
           where used_in_content is true
RULE 13.5  excluded_sources: array, must contain "Reddit" and "Quora"
RULE 13.6  No source URL contains "reddit.com" or "quora.com"
```

---

### BLOCK 14: IMAGES

```
RULE 14.1  images: array (empty [] valid)
RULE 14.2  Each image: image_id (string), before_lines_text (string),
           after_lines_text (string), image_source (string),
           is_external_cited_image_source (boolean),
           cited_external_img_source (string or null),
           safety_checks (object), is_image_rendered (boolean),
           image_content_source (string), image_uri_source (string or null)
RULE 14.3  safety_checks: is_sexually_explicit, is_harmful, is_abusive
           must all be false. is_content_safe must be true or "unknown".
RULE 14.4  If is_external_cited_image_source is true:
           is_image_rendered must be false
RULE 14.5  images_ignored: array (empty [] valid)
RULE 14.6  Each ignored image: content_src, image_uri, reason,
           is_external_cited_image_source, cited_external_img_source
RULE 14.7  reason: enum —
           "cannot_fetch","guard_rail","is_external_cited",
           "sports_content","person_identified","explicit","irrelevant","unknown"
```

---

### BLOCK 15: FILE REFERENCES & GENERATION META

```
RULE 15.1  file_references.md: string, ends with ".md"
RULE 15.2  file_references.html: string, ends with ".html"
RULE 15.3  file_references.json: string, ends with ".json"
RULE 15.4  All three file references present and non-empty
RULE 15.5  generation_meta.generation_date: string, valid date format
RULE 15.6  generation_meta.model: string, non-empty
RULE 15.7  generation_meta.spec_versions.content_spec: must equal "v3.0"
RULE 15.8  generation_meta.spec_versions.narration_flow_spec: must equal "v1.1"
RULE 15.9  generation_meta.spec_versions.json_schema_spec: must equal "v1.0"
```

---

## OUTPUT: SCHEMA VALIDATION REPORT

```
SCHEMA VALIDATION REPORT
─────────────────────────
Article: [slug]
Date: [validation_date]

BLOCKS VALIDATED:
  Block 1  — Root Envelope:           [PASS / FAIL (N failures)]
  Block 2  — Word Count Meta:         [PASS / FAIL (N failures)]
  Block 3  — Content Safety:          [PASS / FAIL (N failures)]
  Block 4  — Hero:                    [PASS / FAIL (N failures)]
  Block 5  — Hook:                    [PASS / FAIL (N failures)]
  Block 6  — Sections Array:          [PASS / FAIL (N failures)]
  Block 7  — Body Schemas:            [PASS / FAIL (N failures)]
  Block 8  — Ambient Card:            [PASS / FAIL (N failures)]
  Block 9  — Deep Dive Button:        [PASS / FAIL (N failures)]
  Block 10 — Sub-sections:            [PASS / FAIL (N failures)]
  Block 11 — Quick Reference:         [PASS / FAIL (N failures)]
  Block 12 — Narrative Metadata:      [PASS / FAIL (N failures)]
  Block 13 — Sources & Exclusions:    [PASS / FAIL (N failures)]
  Block 14 — Images:                  [PASS / FAIL (N failures)]
  Block 15 — File Refs & Gen Meta:    [PASS / FAIL (N failures)]

TOTAL RULES CHECKED: [N]
TOTAL FAILURES: [N]
HARD FAILURES (word count > 1200, sub-section > 500): [N]

OVERALL RESULT: [PASS / FAIL]

FAILURE DETAILS:
  [For each failure:]
  Rule [N.N]: [rule description]
  Field: [JSON path to field]
  Expected: [expected value or type]
  Found: [actual value or type]
  Severity: [HARD / STANDARD]

NEXT STEP:
  → PASS: Article is valid. Ready for output.
  → FAIL: Return specific failure list to Content Generation skill.
          Agent must correct all failures and re-run Schema Validation.
          Content Moderation and Creativity & Narration do not need
          to re-run for structural-only fixes unless content was changed.
```
