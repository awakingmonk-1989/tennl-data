# SKILL: Content Generation
## India Discovery Platform — Article Generation Procedure
### Version 1.0 · March 2026

---

## PURPOSE

This skill governs the step-by-step procedure for generating one complete
article (page + posts + deep dives + JSON). Follow every step in order.
Do not skip steps. Do not reorder steps.

**Specs this skill references:**
- `/specs/content_spec_v3.md` — safety, word counts, source rules
- `/specs/narration_flow_spec_v1_1.md` — structure, options, tonal arc
- `/specs/json_schema_spec_v1.md` — JSON field types and schemas

**Skills to run after this skill completes (in order):**
1. Content Moderation skill
2. Creativity & Narration skill
3. Schema Validation skill

---

## STEP 1: READ INPUT

Receive and confirm the three required input fields:
```
topic:            STRING — e.g. "Life Hacks"
sub_topic:        STRING — e.g. "Focus & Attention"
content_variant:  ENUM   — "CURATED_WEB_WITH_IMAGES" |
                            "CURATED_WEB_NO_IMAGES"   |
                            "AI_GENERATED"
```

If content_variant is "CURATED_WEB_WITH_IMAGES" or "CURATED_WEB_NO_IMAGES":
→ Research the topic using web sources before writing.
→ Exclude Reddit and Quora entirely.
→ Prioritise: news sites, independent blogs, academic sources, brand sites.
→ Synthesise and rewrite — never reproduce source text.
→ Populate sources[], content_sources[], and images_ignored[] in JSON.

If content_variant is "AI_GENERATED":
→ Generate from training knowledge only. No web research.
→ sources[] and content_sources[] will be empty arrays.
→ No historical controversies permitted in AI_GENERATED mode.

---

## STEP 2: PLAN THE PAGE (internal — do not output this)

Before writing any content, map the full page structure:

```
PAGE LEVEL
  title_line_1:          ← bold display, strong noun or verb phrase
  title_line_2:          ← italic accent, completing thought, shorter
  descriptor:            ← 1 sentence, max 15 words, benefit-focused promise
  quote_banner: yes/no   ← yes ONLY if one crystallising insight earns it
  hook_type:             ← "lede" or "quote_banner"
  hook_text:             ← max 3 sentences, must be surprising or specific
  quick_reference_variant: A or B

POST LEVEL (plan each post before writing any)
  Post 1: [emoji] LABEL | Title | content_option | stat_card? | deep_dive?
  Post 2: [emoji] LABEL | Title | content_option | stat_card? | deep_dive?
  Post 3: [emoji] LABEL | Title | content_option | stat_card? | deep_dive?
  ... (3–5 posts total)

  content_option_sequence: [x, y, z]
    → Validate: no two consecutive values are identical
    → If any two consecutive are identical: change one before proceeding

  tonal_arc: [warm, credibility, instructional, india_specific, reflective]
    → One value per post, in reading order
```

Content options available per post:
- "1" Pure Narrative — 1–2 paragraphs + closing line
- "2" Narrative + Ambient Stat Card — prose + warm stat card
- "3" Point-Wise Facts — intro + bold label items (3–5 items)
- "4" Narrative + Embedded Steps — intro + named numbered steps (max 6)
- "5" Highlight Banner + Point-Wise — accent banner + 2–4 bold items
- "B" Sub-section Cards — only when 2+ items each need 200+ words inline

Deep dive variants (one per post maximum):
- "A" Stepped Process — intro + named steps + optional additional section
- "B" Intro + Bold List — catchy intro + heading + bold-item list
- "C" Multi-headed Prose — intro + 2–4 headed prose sub-sections

---

## STEP 3: WRITE THE HOOK (page-level)

Write the hook before any post content. It sets the page's voice.

Quality test before proceeding:
→ Is the first sentence unexpected or counterintuitive?
→ Does the reader feel understood rather than lectured?
→ Would a reader pause mid-scroll to read this?
→ Does it avoid all forbidden openers? ("In today's fast-paced world...",
   "It is important to note...", "We all know...")

If any test fails: rewrite the hook. Do not proceed with a weak hook.

---

## STEP 4: WRITE POSTS IN READING ORDER

Write each post following its planned content_option. Never skip to a later
post before completing the current one.

For each post, apply the THREE-BEAT structure:
- Beat 1: Observation or Setup — why this matters
- Beat 2: Insight or Technique — the specific thing
- Beat 3: Payoff or Human Touch — what changes, the landing moment

Sentence rhythm per post:
- Short sentences: openings and closings
- Longer sentences: middle of the post only
- Never 3+ long sentences in a row
- Final line of every post: short, clean, carries the reader forward

OPTION-SPECIFIC RULES:

Option 1 (Pure Narrative):
  → 1–2 paragraphs max
  → closing_line is the beat-3 payoff, 1 short sentence

Option 2 (Narrative + Stat Card):
  → Write prose paragraphs that set up WHY the stat matters
  → The stat card renders AFTER the prose, BEFORE the deep dive button
  → Populate ambient_card{} in JSON: value, explanation, source, display tokens

Option 3 (Point-Wise Facts):
  → 1-sentence intro framing the list
  → 3–5 items: bold label (1–4 words) + 1–2 sentence explanation
  → list_style: "unordered_bullet" unless sequence matters

Option 4 (Narrative + Steps):
  → 2–3 sentence intro explaining what the process is and why it works
  → 2–6 named steps: step_number, step_label (named not just numbered),
    step_body (1 sentence, actionable)
  → closing_line: 1-sentence payoff

Option 5 (Highlight Banner + Point-Wise):
  → highlight_banner: label (3–7 words, accent bold) + 2–3 sentence body
  → banner display: ambient_banner, warm_tinted_surface, left_accent border
  → 2–4 point-wise items below the banner

Option B (Sub-section Cards):
  → Write a 1–2 sentence intro for the post
  → Build card_grid: one card per sub-section
  → Each card: sub_section_id, card_title, card_summary (1–2 sentences,
    genuinely useful teaser), card_tag, cta_label
  → Write all deep dive content for each sub-section (see Step 5)

---

## STEP 5: WRITE DEEP DIVES (post-level — inside parent post only)

Write deep dives immediately after the post they belong to.
Each deep dive lives in sub_sections[] of its parent post.

Variant A (Stepped Process):
  → intro: 2–3 sentences — why the process works
  → steps[]: step_title (named), step_heading_format: "step_n_dash_title",
    step_body (1–4 sentences, specific)
  → optional additional_section: extra concept with heading + body
  → closing_note: 1-sentence payoff (optional)
  → time_label: required for how_to_guide and recipe types

Variant B (Intro + Bold List):
  → intro: max 3–4 lines — the hook and why, NOT a summary
  → section_heading: h3 grouping the items
  → items[]: label + body + label_style: "bold_sentence"
    (bold label + period + regular body)
  → closing_paragraph: 1–2 sentence synthesis (optional)

Variant C (Multi-headed Prose):
  → intro: 2–3 sentences of context
  → sub_sections[]: 2–4 items each with heading (h3) + body (2–4 sentences)
  → each sub-section can have has_list: true with nested list items
  → closing_line: 1-sentence final payoff

Deep dive word count: 200–500 words. Hard cap 500.
Deep dive button label: "Deep dive: [Specific Topic] ›"
  → Max 6 words after the colon
  → Never "Read more", "Learn more", "Expand"

---

## STEP 6: WRITE QUICK REFERENCE (page-level — write last)

Write the quick reference AFTER all posts and deep dives are complete.
Distil from the article content — never invent separately.

Variant A (Single Column):
  → heading: "Quick Reference" / "Start Here" / "Your Action List"
  → 4–5 items, each starting with an action verb
  → ordered: most immediate action first → most commitment-level last

Variant B (Two Column):
  → heading: "Your Quick-Start List"
  → left_column.label: "Do Today" — 4–5 immediate actions (minutes)
  → right_column.label: "Do This Week" — 4–5 commitment-level changes
  → display.style: "dark_card"
  → Use when content naturally splits immediate vs habit-level

---

## STEP 7: BUILD THE JSON

Construct the complete JSON object using JSON Schema Spec v1.0.
Follow the three-level hierarchy:

```
ROOT (page-level)
  → hero{}
  → hook{}
  → sections[] (posts)
      → body{}           (typed per content_option)
      → ambient_card{}   (null unless option "2")
      → deep_dive_button{} (null unless sub_sections present)
      → sub_sections[]   (deep dives — null if none)
          → content{}    (typed per variant A/B/C)
  → quick_reference{}
  → tonal_arc[]
  → content_option_sequence[]
  → word_count_meta{}
  → content_safety{}
  → sources[]
  → images[]
  → images_ignored[]
  → file_references{}
  → generation_meta{}
```

Populate generation_meta.spec_versions:
```json
{
  "content_spec": "v3.0",
  "narration_flow_spec": "v1.1",
  "json_schema_spec": "v1.0"
}
```

---

## STEP 8: PRE-OUTPUT CHECKLIST

Verify every item before producing output. Fix anything that fails.

STRUCTURE
  [ ] Page-level fields are at root — not inside sections[]
  [ ] Post-level fields are inside sections[] — one object per post
  [ ] Deep dive fields are inside sub_sections[] of their parent post
  [ ] 3–5 posts total

CONTENT
  [ ] Hook is specific, surprising, passes quality test from Step 3
  [ ] Every post is fully written — zero placeholder text
  [ ] No two consecutive posts have the same content_option
  [ ] Final post is reflective, not instructional
  [ ] India-specific references feel natural, not forced
  [ ] Closing line of each post is short
  [ ] Word count: 600–900 preferred, 1200 hard cap

DEEP DIVES
  [ ] Correct variant (A/B/C) chosen per content type
  [ ] Variant B intro is catchy, not a summary
  [ ] Word count 200–500, hard cap 500
  [ ] time_label present for how_to_guide and recipe types
  [ ] Button label is specific

JSON
  [ ] content_option_sequence: no two consecutive identical
  [ ] tonal_arc.length == content_option_sequence.length == sections.length
  [ ] ambient_card null when content_option != "2"
  [ ] deep_dive_button null when sub_sections null
  [ ] All card sub_section_ids match actual sub_sections ids
  [ ] All safety flags false except is_content_safe: true
  [ ] generation_meta.spec_versions all three populated

---

## OUTPUT

Produce in this order:
1. Article body in clean markdown (per Narration Flow Spec v1.1 format)
2. JSON object (fully typed per JSON Schema Spec v1.0)

Then pass output to:
→ Content Moderation skill
→ Creativity & Narration skill
→ Schema Validation skill
