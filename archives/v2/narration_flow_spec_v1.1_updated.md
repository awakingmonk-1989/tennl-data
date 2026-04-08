# Content Narration & Visual Flow Spec
## India Discovery Platform — Article Narrative & UI Alignment Guide
### Version 1.2 · Companion to Content Spec · April 2026

---

## ABOUT THIS SPEC

This spec is a **companion to Content Spec v3.0**, not a replacement.

| Content Spec v3.0 | This Spec (Narration & Visual Flow v1.1) |
|---|---|
| What to cover, word counts, safety rules, image/JSON schema | How to sequence, frame, and present that content |
| When to use sub-sections (Pattern B) | How sub-section deep dives are formatted and outlined |
| File structure (MD / HTML / JSON) | How textual narrative maps to visual components and UX flow |

**The goal:** An agent following both specs produces articles where the narrative was written *for* the visual layout — not poured into it afterwards. The reading experience should feel warm, progressive, and fresh throughout.

---

## PART 0: CONTENT SAFETY BRIEF (ALWAYS ACTIVE)

All content — article, section, deep dive, cards, banners — must satisfy:
- No harmful, explicit, adult, intimidating, or child-inappropriate content
- No sports references, no movie references, no direct named real-person references in body text
- No health, mental wellness, therapy, relationship, or social counselling advice
- All real professionals masked in body text (e.g. "a Bengaluru-based food blogger"); full name only in JSON `masked_persons[]`
- No Reddit or Quora content used as sources under any circumstance
- Images flagged with full safety schema; external-cited images (Shutterstock, AFP, Getty) never rendered

*Full rules: Content Spec v3.0, Part 3.*

---

## PART 0A: RUNTIME CREATIVE CONTROLS (NEW LOCKED SECTION)

This system runs in a **standalone stateless** mode. Each invocation is independent.
So the narration layer must consume runtime-selected creative controls rather than
invent them ad hoc.

For each run, the agent receives:
- `content_mode`
- `angle`
- `tone`
- `hook_style`

These are article-level controls and are authoritative for the run.

Definitions:
- `content_mode` = article-level macro mode (story / analysis / guide / reflection / comparison)
- `angle` = primary lens
- `tone` = emotional and stylistic voice
- `hook_style` = opening hook family
- `content_option` = section-level rendering structure and is not the same as `content_mode`

Narration rule:
- section sequencing, openings, and closings must support the selected runtime controls
- do not let section-level variety replace the selected article-level direction

## PART 1: PAGE vs POST vs DEEP DIVE — HIERARCHY CLARIFIED

The platform has three content levels. This spec governs the narrative and visual flow of all three.

```
PAGE
│   A full article — e.g. "Outsmart Your Day"
│   Has a hero, multiple sections, a quick reference block, a sources footer
│   Corresponds to one sub-topic article (one .md / .html / .json file)
│
└── POST (Section)
│       One section within the page — e.g. "Win Your Morning the Night Before"
│       Has a label, section title, content block, optional deep dive button
│       Rendered as a distinct visual unit within the page
│
    └── DEEP DIVE (Sub-section)
            Accessed by clicking the deep dive button on a post
            Opens inline or in an overlay — stays within the page context
            Has its own internal formatting (see Part 6)
            Corresponds to a sub-section in the JSON
```

A page can be viewed as a **composite of its posts** — all sections visible together. Individual posts can also be surfaced in feeds or discovery contexts as standalone reads.

---

## PART 2: PAGE-LEVEL ELEMENTS — TITLE, SUBTITLE & QUOTE BANNER

### 2.1 Page Title (Mandatory)

Every page must have a two-part title that creates visual and narrative impact:

**Title Line 1** — Bold, dominant, display serif. A strong noun or verb phrase.
**Title Line 2** — Typically italic, accent colour. The completing thought.

Together they form a title that is catchy, invokes curiosity, and guides the reader into the content. The split should feel natural when spoken aloud.

```
title_line_1: "Outsmart"
title_line_2: "Your Day."
```

Effective patterns:

| Pattern | Line 1 | Line 2 |
|---|---|---|
| Command + Object | "Outsmart" | *"Your Day."* |
| Subject + Call | "Your Kitchen" | *"Called."* |
| Question reframe | "What If" | *"Your Morning Started the Night Before?"* |
| Counterintuitive | "Stop Running." | *"Start Living."* |
| Bold noun + qualifier | "Seven Tricks" | *"Your Grandmother Knew."* |

Line 2 is typically shorter than Line 1. The italic/accent treatment creates contrast and a moment of delight.

### 2.2 Page Subtitle / Descriptor (Mandatory)

One sentence. Maximum 15 words. Appears below the title in the hero zone. Warm, direct, benefit-focused — a promise to the reader, not a description of the article.

```
descriptor: "The life hacks that actually fit Indian life — for calmer mornings, sharper focus, and a daily rhythm that just works."
```

**Rules:**
- Must start from the reader's perspective, not the article's
- Avoid: "This article covers...", "In this guide you'll find..."
- Good form: benefit + context + promise

### 2.3 Opening Quote Banner (Optional — Use Only When It Earns Its Place)

A styled quote callout that appears after the trust badges, before the first section. It is **not mandatory**. It must only be included when there is a single crystallising insight that:
- Can be expressed in 1–2 sentences
- Would make a reader want to screenshot and send it
- Is the thematic core of the entire article, not just one section

**Do not add a quote banner for the sake of adding one.** If the article's hook is an observation or counterintuitive truth that requires context, use a Bold Lede instead (see Part 3).

Quote banner format:
- Italicised serif text inside a left-bordered callout box
- Not attributed to a named real person — it reads as the article's editorial voice
- Example: *"The most effective people aren't doing more. They're doing less, better — with small, intelligent defaults that quietly compound."*

```json
"hero": {
  "title_line_1": "Outsmart",
  "title_line_2": "Your Day.",
  "descriptor": "The life hacks that actually fit Indian life...",
  "quote_banner": {
    "enabled": true,
    "text": "The most effective people aren't doing more. They're doing less, better — with small, intelligent defaults that quietly compound."
  }
}
```

When `quote_banner.enabled` is `false` or omitted, the Bold Lede paragraph format is used instead.

---

## PART 3: THE OPENING HOOK BLOCK

Appears directly after the trust badges, before the first post/section.

**Type A — Quote Banner** (see Part 2.3 — optional, earned)

**Type B — Bold Lede Paragraph**
- A slightly larger paragraph, elevated typographic weight
- Used when the hook is a counterintuitive truth, a surprising fact, or a scene-setting observation requiring context
- 2–3 sentences maximum
- Must NOT open with: "In today's fast-paced world...", "We all know that...", "It's no secret that..."

**Hook quality test:** Does this hook make the reader feel slightly seen — like the article already understands their life? If not, rewrite.

---

### 3.1 Hook Style Mapping (new runtime-controlled layer)

The opening hook must follow the selected `hook_style`:

| hook_style | Opening behaviour |
|---|---|
| observation | Start with a precise lived observation or overlooked everyday pattern |
| contrarian | Open by reversing a common assumption without sounding smug |
| practical_problem | Open with a concrete friction point the reader recognises immediately |
| small_truth | Open with a quiet but resonant truth |
| unexpected_pattern | Open by connecting two things the reader does not usually link |

Do not substitute a different hook family unless blocked by safety or clarity.

## PART 4: POST (SECTION) STRUCTURE — FULL ANATOMY

```
[Section Label]          ← emoji + small caps 1–2 words, accent colour, letter-spaced
[Section Title h2]       ← serif, specific promise, max 8 words
[Content Block]          ← one of 5 options (see Part 5)
[Ambient Card]           ← optional stat/highlight card (see Part 5B)
[Deep Dive Button]       ← only if this post has a Pattern B sub-section
```

### 4.1 Section Label

Format: `[emoji] LABEL`
- 1–2 words, all caps, letter-spaced, accent colour
- The emoji is a semantic anchor, not decoration
- Examples: `🌙 MORNING`, `📵 FOCUS`, `🏠 HOME`, `⚡ INDIA`, `🍋 TECHNIQUE`

### 4.2 Section Title (h2) Tone Patterns

| Pattern | Example |
|---|---|
| The Named Technique | "The Two-List Technique" |
| The Specific Promise | "Garlic Peeled in Under a Minute" |
| The Observation Punchline | "The Interruption Tax Nobody's Counting" |
| The Direct Statement | "Your Home Should Work For You" |
| The India-Specific Angle | "India-Specific Hacks Worth Stealing Right Now" |

---

## PART 5: CONTENT BLOCK OPTIONS — MAIN POST BODY

Choose one option per section. **Vary across sections** — never the same option for two consecutive sections.

---

### OPTION 1 — Pure Narrative (Flowing Prose)

**Visual feel:** 1–2 paragraphs. No embellishments. Text carries all the weight.

**Use when:** The idea requires a chain of reasoning to land. Tone needs to be warm, personal, or reflective. A list would feel clinical.

**Structure:**
- Paragraph 1: context — *why this matters*
- Paragraph 2: insight/action — *what to do about it*
- Closing line: short, lands cleanly, carries the reader into the next section

**Example:**
> Most to-do lists fail because they try to *capture* and *prioritize* simultaneously. Each evening: **List 1** — dump everything on your mind without filtering. **List 2** — just three tasks for tomorrow. Sleep on List 1. Work from List 2.
>
> Pair it with the **Two-Minute Rule:** if it takes under two minutes, do it now — not later, not listed. The micro-tasks that clog your mental bandwidth cost more energy queued than completed.

---

### OPTION 2 — Narrative + Ambient Stat Card

**Visual feel:** Prose paragraph followed by a visually distinct card with a large number/stat, then optionally a closing paragraph or deep dive button.

**Use when:** A compelling data point anchors the section's argument. The number is surprising enough to be a visual moment in itself. Use sparingly — maximum once per article.

**Ambient Card rules:**
- The number/stat is displayed large in accent colour (e.g. `28%`)
- Below it: 1–2 lines of explanation in muted tone, source in parentheses
- The card has a warm, ambient background — a soft tinted surface (light warm cream in light themes, deep warm dark in dark themes) with a left accent border
- It should feel like a pulled-out insight — not a table, not a callout box, not a chart
- The card blends into the section's visual warmth rather than interrupting it

**Example:**
> Every interruption doesn't just cost 2 seconds. Research on cognitive recovery shows the brain takes 15–23 minutes to return to deep focus after an interruption. The fix takes three minutes: revoke notification permissions for every app except calls, messages, and calendar.
>
> [AMBIENT CARD]
> **28%**
> India's wellness market annual growth rate — nearly 4× the global average. Indians are investing in doing life better. *(FICCI-EY / Global Wellness Institute, 2025–26)*

```json
"content_option": "2",
"stat_card": {
  "value": "28%",
  "explanation": "India's wellness market annual growth rate — nearly 4× the global average. Indians are investing in doing life better.",
  "source": "FICCI-EY / Global Wellness Institute, 2025–26",
  "display": "ambient_card"
}
```

---

### OPTION 3 — Point-Wise Facts (Bold Label + Content)

**Visual feel:** A brief intro sentence, followed by bullet items. Each item: **Bold label.** followed by a descriptive sentence.

**Use when:** The section covers multiple distinct parallel items — techniques, rules, principles. Each item is short enough to not need its own section but specific enough to need its own label. Reader benefits from scanning.

**Rules:**
- 3–5 items maximum
- Each item: **Bold label (1–4 words).** Then 1–2 sentences
- Brief 1-sentence intro before the list to frame what's being listed
- Items in parallel grammatical structure

**Example:**
> Three techniques that save dishes when something goes wrong:
>
> - **Over-salted dish.** Add chunks of raw potato and simmer 10–15 minutes. The starch absorbs excess salt — chemistry, not folklore.
> - **Watery curry.** Don't boil down on high heat. Dry-roast poppy seeds, grind fine, stir in. Thickens naturally without altering flavour.
> - **Perfect biryani grains.** Add a few drops of lemon juice + a drop of oil to cooking water. Breaks down surface starch and keeps every grain distinct.

---

### OPTION 4 — Mixed Narrative + Embedded Steps

**Visual feel:** A short prose paragraph followed by numbered steps, then an optional closing line.

**Use when:** The section describes a process or ritual with a specific sequence. Order matters and must be preserved. Prose alone would be unclear; a pure list would lose warmth.

**Rules:**
- Opening paragraph: 2–3 sentences — what the process is and why it works
- Steps: numbered, 1 sentence each, in strict sequence, maximum 6 steps (beyond 6 → move to deep dive)
- Optional closing: 1 sentence that frames the payoff or adds a human touch

**Example:**
> The 10-minute evening reset returns your home to neutral before sleep. Not cleaning — resetting. There's a difference.
>
> 1. Kitchen (3 min): rinse dishes, wipe counter, put away anything left out
> 2. Living space (2 min): clothes off the floor, surfaces cleared
> 3. Tomorrow prep (2 min): bag packed, charger plugged in, keys on hook
> 4. Walk-through (1 min): one pass through each room — close it down visually
> 5. Your signal (2 min): whatever marks the day as done for you
>
> Ten minutes the night before saves 25 stressed minutes the next morning.

---

### OPTION 5 — Highlight Banner + Point-Wise (India-Specific / Callout Pattern)

**Visual feel:** A visually distinct highlighted banner callout (containing 1 key insight, tip, or fact in an ambient warm box), followed by a short point-wise list below it.

**Use when:** The section has one single standout insight that deserves visual emphasis AND 2–3 supporting points that complement it. This option gives the section a clear visual anchor before the supporting detail.

**The Highlight Banner:**
- A short callout box — warm ambient background, slightly elevated treatment
- Contains 1–3 sentences only — the standout tip, observation, or fact
- The opening phrase can be in accent colour as an emphasis label (e.g. *"The commute is curriculum."*), followed by the detail
- Must be a genuinely interesting or surprising insight — not a generic tip dressed up visually

**Following Point-Wise List:**
- 2–4 bullet items below the banner
- Each item: **Bold label.** followed by 1–2 sentences
- The banner and list together tell the section's story

**Example:**
> [HIGHLIGHT BANNER]
> **The commute is curriculum.** Bengaluru's average commute is 90 minutes a day. Audiobooks, podcasts, language apps — the commute won't get shorter. What you do with it is entirely yours.
>
> - **Auto-pay everything fixed.** Electricity, internet, insurance — set it and forget it. Zero mental overhead. Zero late fees.
> - **Sunday meta-work.** 30 minutes: meal plan, laundry started, devices charged, week's priorities written. Monday becomes a glide instead of a crash.

```json
"content_option": "5",
"highlight_banner": {
  "label": "The commute is curriculum.",
  "body": "Bengaluru's average commute is 90 minutes a day. Audiobooks, podcasts, language apps — the commute won't get shorter. What you do with it is entirely yours.",
  "display": "ambient_banner"
}
```

**Ambient display guidance for banners and stat cards:**
Both the Option 2 stat card and the Option 5 highlight banner use an "ambient" display treatment. In both cases, the background should be a warm, soft tinted surface — not stark white, not a loud colour. In light themes: warm cream or the palest tint of the accent colour. In dark themes: a deep, warm dark surface slightly lighter than the page background. Both should feel like they belong to the article's warmth rather than interrupting it. The left accent border is the primary distinguishing mark.

---

## PART 5B: AMBIENT CARD / BANNER — DISPLAY GUIDELINES (CROSS-OPTION)

The ambient card/banner pattern appears in Option 2 (stat card) and Option 5 (highlight banner). Consistent treatment across both:

| Property | Specification |
|---|---|
| Background | Warm tinted surface — never white or stark. Light themes: soft warm cream. Dark themes: warm dark surface |
| Left border | Accent colour, 3–4px, full height of card |
| Border radius | Subtle (4–6px) — not pill-shaped, not sharp |
| Typography | Stat value / Banner label: accent colour, large / bold. Explanation: muted ink, smaller |
| Width | Full column width |
| Padding | Generous — the content should breathe inside the card |
| Placement | Always after the prose that sets it up, never as the opening element of a section |
| Tone | The card is an ambient moment — it should feel like a warm editorial aside, not a data table |

---

## PART 6: DEEP DIVE (SUB-SECTION) — FORMATTING VARIANTS

A deep dive opens when a reader clicks the deep dive button on a post. It reveals expanded content in an inline panel with a dark header bar (showing the deep dive title + Back button) and a white/light content body below.

Deep dives are short (200–500 words). Their internal structure uses one of three formatting variants.

---

### DEEP DIVE VARIANT A — Stepped Process

**Use when:** The deep dive contains a sequential how-to process where order matters.

**Internal structure:**
```
[Deep Dive Title]           ← h2, specific and descriptive
[Brief intro paragraph]     ← 2–3 lines max, sets up the process
[Step 1 — Named Step]       ← h3, format: "Step N — [Name of Step]"
[Step content]              ← 1–4 sentences
[Step 2 — Named Step]       ← repeat
...
[Closing note]              ← optional 1-line payoff
[Time/Difficulty label]     ← "Total time: X · Difficulty: Low"
```

**Narrative rules:**
- Each step has a named h3 title — not just "Step 1", but "Step 1 — Write Your One Thing"
- Step content: 1–4 sentences. Specific. Actionable. No padding.
- The brief intro tells the reader *why* the process works before showing *how*
- Closing note: 1 sentence that frames the compound effect or payoff

**From screenshots (Image 3 — The 5-Minute Night Ritual):**
```
The 5-Minute Night Ritual
[intro: the brain doesn't switch off — give it direction]

Step 1 — Write Your One Thing
Not a list. One task...

Step 2 — Set Up the Morning
Bag packed. Keys on hook...

Step 3 — Note One Win
One small thing that went well...

The Phone-Free Morning Buffer
[closing section: 20-min no-phone window]
```

---

### DEEP DIVE VARIANT B — Intro + Bold-Item List

**Use when:** The deep dive contains multiple parallel items (settings, tips, techniques) that are individually actionable and benefit from bold labels.

**Internal structure:**
```
[Deep Dive Title]           ← h2
[Brief catchy intro]        ← max 3–4 lines — the hook and the "why"
[Section Heading]           ← h3 — e.g. "Four Specific Changes"
[Bold-item list]            ← bold label. followed by 1–3 sentences per item
[Closing paragraph]         ← optional 1–2 line synthesis or payoff
```

**Narrative rules:**
- The intro is punchy and direct — not a summary, a hook
- The h3 sub-heading groups the items under a named category
- Each bold item: label in bold, period, then content in regular weight
- The closing paragraph (if present) synthesises the items or adds a reflective note
- This variant works especially well when the items together tell a unified story

**From screenshots (Image 2 — Your Phone Is Not Neutral):**
```
Your Phone Is Not Neutral — Here's How to Take It Back
[intro: well-engineered machine, your attention is the product]

Four Specific Changes
• Turn off all non-essential notifications. Every app that can interrupt you, will...
• Move social apps off your home screen. Second-screen folder. Tiny friction breaks...
• Charge your phone outside your bedroom. Buy a cheap alarm clock. Screen time...
• Set a digital evening cutoff. 9:30 PM. After that, no work email or messages...

[closing: 28% growth note — India recognising attention needs protecting]
```

**Note:** An ambient stat card (Part 5B) can appear inside a Variant B deep dive after the intro paragraph or after the item list — to add a credibility anchor within the deep dive itself.

---

### DEEP DIVE VARIANT C — Multi-Headed Sections

**Use when:** The deep dive contains 2–4 conceptually distinct sub-topics that each need their own heading and a short paragraph. Not a list — each sub-topic is a small beat of prose.

**Internal structure:**
```
[Deep Dive Title]           ← h2
[Brief intro]               ← 2–3 lines — context for what follows
[Sub-heading 1]             ← h3
[Prose paragraph 1]         ← 2–4 sentences
[Sub-heading 2]             ← h3
[Prose paragraph 2]         ← 2–4 sentences
[Sub-heading 3]             ← h3 (optional)
[Prose paragraph 3]         ← 2–4 sentences
[Closing line or note]      ← optional 1-line payoff/label
```

**Narrative rules:**
- Each sub-heading names the concept specifically: "The Two-List System", "The Two-Minute Rule", "Batching for Indian Schedules"
- The prose under each heading is complete — it doesn't trail off or promise more
- Sub-headings should have tonal variety — not all in the same grammatical form
- The closing line is the article-level payoff, not a summary

**From screenshots (Image 1 — Task Systems That Don't Fall Apart by Tuesday):**
```
Task Systems That Don't Fall Apart by Tuesday
[intro: to-do apps make capturing and prioritising the same action — exhausting]

The Two-List System
• List 1 — The Dump: everything on your mind. No filtering. No ordering. Just out.
• List 2 — The Day: three things only...
Sleep on List 1. Work from List 2...

The Two-Minute Rule
For tasks under two minutes — do them now...

Batching for Indian Schedules
Group similar tasks together rather than interleaving them...
```

---

### DEEP DIVE VARIANT SELECTION — DECISION GUIDE

| Use Variant A (Steps) when | Use Variant B (Intro + List) when | Use Variant C (Multi-headed) when |
|---|---|---|
| The deep dive is a process or ritual with a specific order | The deep dive is a set of parallel actionable items | The deep dive covers 2–4 distinct concepts that each need context |
| Steps need to be followed in sequence | Each item is individually actionable without reading others | Each concept is substantive enough to need prose, not a bullet |
| The "how" is as important as the "what" | Bold labels help the reader scan and select | The concepts build on each other in a narrative flow |

---

### DEEP DIVE — ADDITIONAL INTERNAL ELEMENTS

**Ambient Stat Card in Deep Dives:**
A stat card (Part 5B) can appear inside a deep dive — typically after the intro paragraph (Variant B) or as a closing element (any variant). Rules are identical to the main section stat card. Use only when a specific, credible data point adds genuine weight to the deep dive's argument.

**Time/Difficulty Label:**
Recipe and how-to deep dives should always end with:
```
Total time: X minutes · Difficulty: Low / Medium
```
This is displayed as a styled italic line or a small label — not a heading. It gives the reader the commitment level at a glance.

**Deep Dive JSON Schema:**
```json
{
  "id": "sub_lm_01",
  "title": "The 5-Minute Night Ritual That Fixes Your Mornings",
  "type": "how_to_guide",
  "variant": "A",
  "word_count": 280,
  "summary": "1–2 line card summary for the main section",
  "content_md": "## The 5-Minute Night Ritual\n\n[intro]\n\n### Step 1 — Write Your One Thing\n...",
  "has_ambient_card": false,
  "stat_card": null,
  "time_label": "5 minutes · Difficulty: Very Low",
  "images": []
}
```

---

## PART 7: THE DEEP DIVE BUTTON

Appears at the bottom of a post's content block, after all prose.

**Label format:** `Deep dive: [Specific Topic] ›`
- Maximum 6 words after the colon
- Specific — not "Read more", "Learn more", "Expand"
- The topic named should match the deep dive's title closely
- The `›` chevron signals interactivity; it rotates when expanded

**Examples:**
- `Deep dive: The 5-Minute Night Ritual ›`
- `Deep dive: Renegotiate Your Phone Relationship ›`
- `Deep dive: Task Systems That Don't Fall Apart ›`
- `Deep dive: Notification Audit on iOS & Android ›`

```json
"deep_dive_button": {
  "label": "Deep dive: The 5-Minute Night Ritual",
  "sub_section_id": "sub_lm_01"
}
```

---

## PART 7A: CONTENT MODE → SECTION OPTION TENDENCIES

The selected `content_mode` is article-level. Section `content_option` should support it.

| content_mode | Preferred section options | Notes |
|---|---|---|
| story | 1, 2, 5 | Warm narrative spine, selective structure |
| analysis | 1, 2, 3 | Explanatory, comparative, evidence-friendly |
| guide | 3, 4, B | Actionable, process-oriented, structured |
| reflection | 1, 5 | More prose-led, quieter landing |
| comparison | 3, 5, 1 | Trade-offs, distinctions, decision clarity |

This is guidance for alignment, not a license to ignore the selected runtime controls.

## PART 8: VISUAL RHYTHM — VARYING OPTIONS ACROSS SECTIONS

Never use the same content option for two consecutive sections. The sequence creates the article's visual rhythm.

### 8.1 Content Option Sequence — Recommended Patterns

**Lifestyle / Life Hacks (4–5 sections):**
```
Section 1: Option 1 (Narrative)             ← warm entry
Section 2: Option 2 (Narrative + Stat Card) ← credibility anchor
Section 3: Option 3 or 4 (List or Steps)    ← actionable specifics
Section 4: Option 5 (Banner + List)         ← India-specific or standout tip
Section 5: Option 1 (Narrative)             ← reflective close
```

**Kitchen / Food (3–5 sections):**
```
Section 1: Option 1 (Narrative)             ← warm context
Section 2: Option 4 (Steps)                 ← technique with sequence
Section 3: Option 3 (Point-Wise)            ← multiple tips
Section 4: Option 1 (Narrative)             ← wisdom / reflection
```

**Articles with Pattern B (sub-section recipe cards):**
- The Pattern B section uses its own card-grid layout — it is not assigned an Option number
- Sections before and after Pattern B use Option 1 for clean transitions

### 8.2 Content Option Assignment in JSON

```json
{
  "section_id": "sec_lf_02",
  "title": "The Interruption Tax Nobody's Counting",
  "content_option": "2",
  "stat_card": { ... },
  "highlight_banner": null,
  "deep_dive_button": { "label": "Deep dive: Renegotiate Your Phone Relationship", "sub_section_id": "sub_lf_02" }
}
```

Valid values for `content_option`: `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"B"`

---

## PART 9: THE QUICK REFERENCE BLOCK

Appears after all sections, before the sources footer.

**Two variants:**

**Variant A — Single column:**
- Heading: "Quick Reference" / "Start Here" / "Your Action List" / "Try These First"
- 5 items maximum, each starting with an action verb
- Ordered from most immediate to most requiring commitment

**Variant B — Two-column "Do Today / Do This Week":**
- Used when the article has a natural split between immediate actions and slightly longer-horizon commitments
- Left column: "Do Today" — 4–5 immediate actions
- Right column: "Do This Week" — 4–5 actions requiring a few days of commitment
- Displayed on a dark background with accent-coloured headings and `→` prefixed items
- This variant should feel like a warm, direct takeaway — not a corporate action plan

**When to use Variant B:** When the article's content naturally divides into things that can be done in minutes (settings changes, small habits, one-time actions) and things that need to be tried across a week (new systems, routine changes, experiments).

**JSON:**
```json
"quick_reference": {
  "variant": "B",
  "heading": "Your Quick-Start List",
  "columns": {
    "left": { "label": "Do Today", "items": ["Revoke all non-essential notifications", "..."] },
    "right": { "label": "Do This Week", "items": ["Try the Two-List method for 5 days straight", "..."] }
  }
}
```

---

## PART 10: NARRATION FLOW PRINCIPLES

### 10.1 The Three-Beat Section

Every post/section — regardless of content option — should have three beats:
```
Beat 1 — Observation or Setup     (why this matters / the problem / the context)
Beat 2 — Insight or Technique     (the specific thing to know or do)
Beat 3 — Payoff or Human Touch    (what changes / a moment of warmth or landing)
```

### 10.2 The Tonal Arc Across Sections

```
Opening sections:   Warm, relatable, slightly disarming — meet the reader where they are
Middle sections:    Specific, actionable, confident — deliver the value
Final section(s):   Reflective, human, grounding — leave something that lingers
```

The final section should never be the most instructional. It should feel like a breath out.

### 10.3 Sentence Rhythm Rules

- Short sentences for impact — at the start of a section or as the closing beat
- Longer sentences for nuance — to carry complex ideas, qualification, or context
- Never more than 3 long sentences in a row
- The closing line of each section should be short — the line the reader carries forward

### 10.4 Transitions Between Sections

- The visual separator handles the break — no transition phrases needed
- Never: "Now let's look at...", "Moving on to...", "Another important thing is..."
- Let the label + title reorient the reader
- The last line of a section: a sense of completion
- The first line of the next section: starts fresh

---

## PART 11: AGENT GENERATION SEQUENCE

When generating a page/article, follow this order:

**Step 0 — Validate runtime creative controls:**
```
content_mode ∈ content_mode_pool
angle ∈ angle_pool
tone ∈ tone_pool
hook_style ∈ hook_style_pool
```
Treat the selected values as authoritative for the run.

**Step 1 — Plan the narrative stack:**
```
title_line_1, title_line_2, descriptor
quote_banner: enabled or disabled (and why)
hook_type: A or B
sections: [label, title, content_option, ambient_card?, deep_dive?, deep_dive_variant]
quick_reference: variant A or B
content_option_sequence: [check no two consecutive same]
tonal_arc: [warm → actionable → reflective]
```

**Step 2 — Write the hook first.** Voice of the article is set here and must follow the selected hook_style.

**Step 3 — Write sections in reading order.** Tonal arc depends on sequence awareness and must remain aligned with the selected tone and angle.

**Step 4 — Write deep dives.** For each deep dive: select variant (A/B/C), write in full, assign `time_label` if applicable.

**Step 5 — Verify rhythm.** No two consecutive sections with the same content_option.

**Step 6 — Write quick reference last.** Distilled from the article — not invented.

**Step 7 — Assign all JSON fields.** Including `content_option`, `stat_card`, `highlight_banner`, `deep_dive_button.label`, `quick_reference.variant`, and `hero` fields.

---

## PART 12: FULL SECTION JSON SCHEMA (UPDATED)

Complete section object with all Narration Spec v1.1 fields:

```json
{
  "section_id": "sec_lf_02",
  "title": "The Interruption Tax Nobody's Counting",
  "anchor": "interruption-tax",
  "emoji": "📵",
  "label": "Focus",
  "expansion_pattern": "A",
  "content_option": "2",
  "stat_card": {
    "value": "28%",
    "explanation": "India's wellness market annual growth rate — nearly 4× the global average. Indians are investing in doing life better.",
    "source": "FICCI-EY / Global Wellness Institute, 2025–26",
    "display": "ambient_card"
  },
  "highlight_banner": null,
  "deep_dive_button": {
    "label": "Deep dive: Renegotiate Your Phone Relationship",
    "sub_section_id": "sub_lf_02"
  },
  "sub_sections": [
    {
      "id": "sub_lf_02",
      "title": "Your Phone Is Not Neutral — Here's How to Take It Back",
      "type": "how_to_guide",
      "variant": "B",
      "word_count": 290,
      "summary": "Four settings changes. Reclaim hours of focus, better sleep, and real evenings.",
      "content_md": "## Your Phone Is Not Neutral...\n\n[intro]\n\n### Four Specific Changes\n- **Turn off all non-essential notifications.**...",
      "has_ambient_card": false,
      "stat_card": null,
      "time_label": "20 minutes to set up · Payoff: Daily and compounding",
      "images": []
    }
  ]
}
```

Page-level hero fields:

```json
"hero": {
  "title_line_1": "Outsmart",
  "title_line_2": "Your Day.",
  "descriptor": "The life hacks that actually fit Indian life — for calmer mornings, sharper focus, and a daily rhythm that just works.",
  "quote_banner": {
    "enabled": true,
    "text": "The most effective people aren't doing more. They're doing less, better — with small, intelligent defaults that quietly compound."
  },
  "hook_type": "A",
  "hook_text": null
},
"tonal_arc": ["warm", "credibility", "instructional", "india-specific", "reflective"],
"content_option_sequence": ["1", "2", "3", "5", "1"],
"quick_reference": {
  "variant": "B",
  "heading": "Your Quick-Start List",
  "columns": {
    "left": { "label": "Do Today", "items": ["..."] },
    "right": { "label": "Do This Week", "items": ["..."] }
  }
}
```

---

## PART 13: WORKED NARRATIVE PLAN — FOCUS ARTICLE

Full pre-writing blueprint for `lifehacks_focus`:

```
HERO
  title_line_1:  "Reclaim"
  title_line_2:  "Your Focus."
  descriptor:    "What costs you 4 hours a day without you noticing — and the 3-minute fix."
  quote_banner:  enabled = false
  hook_type:     B (Bold Lede)
  hook_text:     "You're not distracted. You're interrupted. There's a difference — and it matters."

SECTION 1 · 📵 FOCUS
  title:          "The Interruption Tax Nobody's Counting"
  content_option: 2
  beat_1:         15–23 min recovery cost per interruption; 10/day = 4 lost hours
  beat_2:         3-minute notification audit — iOS + Android specific steps
  beat_3:         "You're not losing the notification moment. You're losing everything that follows."
  stat_card:      28% / India's wellness market annual growth
  deep_dive:      "Deep dive: Renegotiate Your Phone Relationship" → Variant B

SECTION 2 · 🎯 ATTENTION
  title:          "The One-Screen Rule"
  content_option: 1
  beat_1:         Home screen = most visited real estate, filled with trap apps
  beat_2:         Move social apps to second screen — friction is the feature
  beat_3:         "You choose to open Instagram. You don't just find yourself in it."
  deep_dive:      none

SECTION 3 · ⏱ WORK
  title:          "Deep Work in an Indian Office Context"
  content_option: 3
  items:
    · 90-minute block · schedule + protect + communicate
    · Check-in windows · 11 AM and 4 PM — tell your team
    · Headphones = DND · understood in most Indian offices
  deep_dive:      none

SECTION 4 · ⚡ INDIA
  title:          "India-Specific Hacks Worth Stealing Right Now"
  content_option: 5
  highlight_banner: "The commute is curriculum. Bengaluru's average commute is 90 min/day..."
  items:
    · Auto-pay everything fixed
    · Sunday meta-work
  deep_dive:      none

SECTION 5 · 🌿 REST
  title:          "Schedule Your Offline Time Like a Meeting"
  content_option: 1
  beat_1:         Brain restores through genuine unstimulation — not a different screen
  beat_2:         15-minute daily offline window, same time, treated like a meeting
  beat_3:         "Treat it like any other meeting: block it, protect it, show up for it."
  deep_dive:      none

QUICK REFERENCE: Variant B — "Your Quick-Start List" / Do Today + Do This Week

CONTENT OPTION SEQUENCE: [2, 1, 3, 5, 1] ✓ — no two consecutive same
TONAL ARC: credibility → warm insight → practical list → India-specific → reflective ✓
```

---

## PART 14: CONTENT OPTIONS & DEEP DIVE VARIANTS — QUICK REFERENCE

| Content Option | Best for | Visual feel |
|---|---|---|
| 1 — Pure Narrative | Insights, observations, reflective points | Warm, literary, flowing |
| 2 — Narrative + Stat Card | Data-backed arguments, credibility | Grounded, ambient anchor |
| 3 — Point-Wise Facts | Multiple parallel tips / rules | Scannable, structured |
| 4 — Narrative + Steps | Processes and sequences | Clear, methodical, still warm |
| 5 — Banner + Point-Wise | India-specific or standout callout tip + supporting points | Bold anchor + structured list |
| B — Sub-section Cards | Multiple items needing 200+ words each | Visual grid, interactive |

| Deep Dive Variant | Best for | Key structure |
|---|---|---|
| A — Stepped Process | Sequential how-to, rituals, techniques | Intro → Named Steps → Closing note |
| B — Intro + Bold List | Parallel actionable items | Catchy intro (3–4 lines) → Sub-heading → Bold-item list |
| C — Multi-headed Prose | 2–4 distinct concepts needing context | Intro → h3 + prose × N → Closing line |

---

*Spec version: 1.1 · Companion to Content Spec v3.0*
*March 2026 — India Discovery Platform*
*Changes from v1.0: Added Content Option 5 (Banner + Point-Wise), Deep Dive Variants A/B/C, Ambient Card/Banner display guidelines, Page-level Title/Subtitle/Quote Banner rules, Quick Reference Variant B (two-column), updated JSON schema throughout, Content Safety Brief (Part 0), Page/Post/Deep Dive hierarchy clarified (Part 1).*
