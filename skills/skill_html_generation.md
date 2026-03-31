# SKILL: HTML Content Rendering (Optional)
## India Discovery Platform — Render `.html` from MD + JSON
### Version 1.0 · March 2026

---

## PURPOSE

This skill defines how to generate a **polished standalone HTML page** for an
article **after** the content has already been generated as:
- `{slug}.md` (markdown article body with embedded JSON metadata block), and
- `{slug}.json` (standalone typed metadata, same schema as embedded JSON).

This skill is **optional** and **decoupled** from core content generation.
It must **preserve** all narrative hierarchy and typed structure defined by:
- `/specs/content_gen_spec.md`
- `/specs/narration_flow_spec_v1.1.md`
- `/specs/json_schema_spec_v1.md`

**Important contract:**
- Core content generation outputs **MD + JSON only**.
- This skill may generate an additional `{slug}.html` artifact for UI/rendering purposes.
- The JSON schema remains the UI single source of truth; HTML must be a faithful render of it.

---

## INPUTS

You must have:
- The complete article markdown body (from `{slug}.md`)
- The complete root JSON object (from `{slug}.json`, typed per JSON Schema Spec v1.0)

---

## OUTPUTS

Generate:
- `{slug}.html` — a standalone HTML page that visually renders the article.

Do **not** change the article’s content meaning during rendering.
No new claims, no new advice, no additional sections. Rendering is presentation.

---

## RENDERING PRINCIPLES (MUST FOLLOW)

### 1) Preserve hierarchy exactly (PAGE → POST → DEEP DIVE)

- PAGE = hero + hook + 3–5 posts + quick reference + sources footer
- POST = one section (label, title, typed body, optional ambient card, optional deep-dive entrypoint)
- DEEP DIVE = sub-section panels belonging to exactly one post

Never mix levels in the HTML presentation (e.g. no deep dive content shown as a page-level section).

### 2) Render from JSON (UI reads fields, never parses prose)

Treat the root JSON as the canonical data model:
- Use JSON fields to assemble and render components.
- Do not “infer” structure from the markdown beyond basic formatting.

### 3) Safety & exclusions remain in force

Rendering must not introduce forbidden topics, named persons, sports/movies references, controversy framing, fear-based framing, or unsafe imagery.

If images are present:
- If `is_external_cited_image_source` is true → never render that image.
- If `safety_checks.is_content_safe` is `"unknown"` → do not render (placeholder only).

---

## HTML STRUCTURE (REQUIRED SECTIONS)

Your HTML must include, in order:
1. **Hero header** (from `hero.*`)
2. **Trust badges** / safety label (from `content_label` and `content_safety`)
3. **Hook block** (from `hook.*`)
4. **Posts/sections** rendered in `sections[]` order
5. **Quick reference** (from `quick_reference`)
6. **Sources** (from `sources[]` and/or `content_sources[]` as your product requires)

---

## VISUAL IDENTITY (QUALITY BAR — KEEP CONSISTENT WITH PRIOR GUIDANCE)

Each HTML page should feel like a designed editorial artifact:
- Distinct font pairing and palette per article
- Mobile responsive down to 375px
- Use CSS variables for colors
- Avoid generic “AI template” aesthetics

If this conflicts with a dedicated UI template system, defer to the UI system — this skill is a guideline layer.

---

## SECTION RENDERING RULES

### Pattern A sections (`expansion_pattern: "A"`)
- Render the full post body inline.
- No accordions. No “read more” truncation.

### Pattern B sections (`expansion_pattern: "B"`, `content_option: "B"`)
- Render the post intro (`body.intro`).
- Render a grid of summary cards from `body.card_grid.items`.
- Clicking a card opens the corresponding deep dive panel (overlay or inline panel).
- Only one deep dive open at a time.
- Provide an explicit Back/Close control.

---

## BODY OPTION RENDERING (POST-LEVEL)

Render each post’s `body` by its `content_option` schema (Options 1–5 or B) exactly as described in the JSON schema spec.

If `ambient_card` is present (only for option "2"):
- Render it after prose and before any deep dive button.

If `deep_dive_button` is present:
- Render as an outlined pill button and wire it to open the relevant sub-section panel.

---

## DEEP DIVE PANEL RENDERING

Each deep dive panel renders from `sub_sections[]` with required UI:
- Header: dark bar with Back button (per `display.panel_header_style`)
- Body: light card on overlay (per `display.panel_body_style`)

Render deep dive `content` per variant A/B/C schema.

---

## NO PLACEHOLDERS RULE (STRICT)

The HTML must not contain any placeholder content such as:
- `[Section prose here]`
- `TODO`
- empty blocks where prose should be

If a piece of content is missing from JSON, the content generation step is incomplete — do not “patch it” during rendering.

---

## RECOMMENDED IMPLEMENTATION APPROACH (GUIDANCE)

1. Load JSON as a single inlined script tag (or separate JSON file if allowed).
2. Render hero, hook, sections, quick reference, sources.
3. Build deep dive panels from `sub_sections[]`.
4. Wire card clicks to open corresponding panel.
5. Run a final pass:
   - Verify sections order and completeness
   - Verify no externally cited/unsafe images are rendered
   - Verify mobile layout at 375px

