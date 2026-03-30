# Content Narration & Visual Flow Spec
## India Discovery Platform — Article Narrative & UI Alignment Guide
### Version 1.0 · Companion to Content Spec v3.0 · March 2026

---

## ABOUT THIS SPEC

This spec is a **companion to Content Spec v3.0**, not a replacement. The two specs serve different purposes:

| Content Spec v3.0 | This Spec (Narration & Visual Flow) |
|---|---|
| What topics to cover | How to sequence and frame that content |
| Word count, safety rules, image schema | How narration maps to visual components |
| When to use sub-sections | How to vary content presentation for visual rhythm |
| JSON/MD/HTML file structure | How textual flow aligns with the reading UX |

**The goal of this spec:** An agent following both specs should produce articles where the narrative feels like it was written *for* the visual layout — not poured into it afterwards. The reading experience should feel warm, progressive, and fresh throughout.

---

## PART 1: THE ANATOMY OF AN ARTICLE — TOP TO BOTTOM

Every article has a fixed visual stack. The narrative must be written to fit each layer of this stack in order. Never write content as a flat document and then try to assign it to zones later.

```
┌─────────────────────────────────────┐
│  HERO ZONE                          │
│  Category path · Topic title        │
│  One-line descriptor                │
│  Meta strip                         │
├─────────────────────────────────────┤
│  TRUST BADGES                       │
│  Content Safe · Curated             │
├─────────────────────────────────────┤
│  OPENING HOOK BLOCK                 │
│  (Quote callout OR bold lede)       │
├─────────────────────────────────────┤
│  SECTION 1                          │
│  Label · Title · Content Block      │
│  [Deep dive button — if applicable] │
├─────────────────────────────────────┤
│  SECTION 2                          │
│  Label · Title · Content Block      │
│  [Stat card — if applicable]        │
│  [Deep dive button — if applicable] │
├─────────────────────────────────────┤
│  SECTION 3 ... N                    │
├─────────────────────────────────────┤
│  QUICK REFERENCE BLOCK              │
├─────────────────────────────────────┤
│  SOURCES FOOTER                     │
└─────────────────────────────────────┘
```

---

## PART 2: THE HERO ZONE

### 2.1 Components (in order, top to bottom)

**Category Path Label**
- Small caps, accent colour, letter-spaced
- Format: `LIFESTYLE · LIFE HACKS` or `FOOD & CULINARY · HOME COOKING`
- Maximum 4 words total
- This is the navigational anchor — it tells the reader exactly where they are

**Article Title**
- Large serif display type, dominant visual element
- The title has **two layers** in the visual hierarchy:
  - **Line 1:** A strong noun or verb phrase (e.g. "Outsmart")
  - **Line 2:** The completing phrase, often in italic accent colour (e.g. *"Your Day."*)
- Together they form the catchy title — but the two-line split is intentional for visual impact
- The split should feel natural when spoken aloud — not forced by line-break rules

**One-Line Descriptor**
- This is the subtitle/standfirst
- 1 sentence, max 15 words
- Expands on the title — tells the reader what they'll get
- Example: *"The life hacks that actually fit Indian life — for calmer mornings, sharper focus, and a daily rhythm that just works."*
- Tone: warm, direct, benefit-focused — not a description of the article, a promise to the reader

**Meta Strip**
- Curated Content · India · Urban 18–45 · ~5 min read · March 2026
- Small, muted — purely informational

### 2.2 Hero Title Writing Rules

The two-line title split must be written into the content — not left to the renderer to decide. The content agent must specify:
```
title_line_1: "Outsmart"
title_line_2: "Your Day."
```

Or as a single field with the split character:
```
title: "Outsmart | Your Day."
```

**Effective two-line title patterns:**

| Pattern | Example |
|---|---|
| Command + Object | "Reclaim \| Your Focus." |
| Question + Answer | "What If \| Your Morning Started the Night Before?" |
| Statement + Twist | "Stop Running. \| Start Living." |
| Subject + Call | "Your Kitchen \| Called." |
| Bold noun + italic qualifier | "Seven Tricks \| *Your Grandmother Knew*" |

The second line is typically shorter than the first. The italic/accent treatment on Line 2 creates visual contrast and a moment of delight.

---

## PART 3: THE OPENING HOOK BLOCK

This block appears directly after the trust badges, before the first section. It is the reader's first experience of the article's voice. It must be earned — not generic.

### 3.1 Hook Block Types

**Type A — Quote Callout**
- Used when the article has a single, quotable, crystallising insight
- Displayed as an italicised serif quote inside a left-bordered callout box
- The quote should be the kind of thing a reader screenshots and sends to someone
- Example: *"The most effective people aren't doing more. They're doing less, better — with small, intelligent defaults that quietly compound."*
- Not attributed to a real person — it reads as the article's editorial voice

**Type B — Bold Lede Paragraph**
- Used when the hook is a counterintuitive truth, a surprising fact, or a scene-setting observation
- Displayed as a slightly larger paragraph with elevated typographic weight
- Example: *"Here's a counterintuitive truth about morning routines: the best ones start the night before. Not at 5 AM with a cold shower and a gratitude journal — just five quiet minutes before you sleep."*

### 3.2 Hook Writing Rules

- Maximum 3 sentences
- The hook must earn the reader's attention — it cannot be a summary of what follows
- It should create a micro-tension (a surprise, a reframe, an unexpected angle) that makes the reader want to continue
- It must NOT start with: "In today's fast-paced world...", "We all know that...", "It's no secret that..."
- The best hooks make the reader feel slightly seen — like the article already understands their life

### 3.3 Which Hook Type to Use

| Use Quote Callout (Type A) when | Use Bold Lede (Type B) when |
|---|---|
| The article has one central insight that can be crystallised into a single sentence | The hook requires context or a setup to land |
| The insight is the kind of thing worth writing on a sticky note | The hook is a counterintuitive reframe that needs a sentence of setup |
| The article covers multiple small tips and the hook captures their common thread | The article starts with a story or observation |

---

## PART 4: SECTION STRUCTURE

Each section has three fixed elements followed by a variable content block:

```
[Section Label]     ← small caps, emoji, accent colour
[Section Title]     ← serif h2, the specific idea this section covers
[Content Block]     ← one of 4 content options (see Part 5)
[Deep dive button]  ← only if this section has a Pattern B sub-section
```

### 4.1 Section Label

- Format: `[emoji] LABEL`
- Label is 1–2 words maximum, all caps, letter-spaced, accent colour
- The emoji is a visual anchor — it should be semantically accurate, not decorative
- Examples: `🌙 MORNING`, `📵 FOCUS`, `🏠 HOME`, `🍋 TECHNIQUE`
- The label categorises the section within the article — it's a navigation aid as much as a heading

### 4.2 Section Title (h2)

- Bold serif, larger than body text
- Should be a specific, pointed statement about what this section delivers
- NOT a generic label ("Tips for Better Sleep") — a specific promise ("The 5-Minute Night Ritual")
- The title should work as a standalone headline — a reader skimming should understand each section from its title alone
- Maximum 8 words

### 4.3 Section Title Tone Patterns

| Pattern | Example |
|---|---|
| The Named Technique | "The Two-List Technique" |
| The Specific Promise | "Garlic Peeled in Under a Minute" |
| The Observation + Punchline | "The Interruption Tax Nobody's Counting" |
| The Question Framed as Title | "What the Best Indian Home Cooks Actually Know" |
| The Counterintuitive Statement | "Your Home Is Either Working For You or Against You" |

---

## PART 5: CONTENT BLOCK OPTIONS — THE CORE OF THIS SPEC

Each section's body uses one of four content block options. Choosing the right option is a **narrative and visual rhythm decision**, not just a formatting decision. The options should be varied across sections within an article — never use the same content option for every section.

---

### OPTION 1 — Pure Narrative (Flowing Prose)

**Visual appearance:** One or two paragraphs of body text. No visual embellishments. The text itself carries all the weight.

**When to use:**
- When the idea requires context, setup, or a chain of reasoning to land
- When the tone needs to be warm, personal, or reflective
- When a list would feel clinical and the idea deserves to breathe
- When the section is making a philosophical or insight-driven point, not an instructional one

**Narrative rules:**
- Maximum 2 paragraphs
- First paragraph: context or observation — *why this matters*
- Second paragraph: the specific insight or action — *what to do about it*
- The two paragraphs should feel connected, not separate — one thought flowing into the next
- Vary sentence length — short punchy sentences create rhythm; longer ones carry nuance

**Example (correct):**
> Five minutes before bed changes everything. Write down **one task for tomorrow**. Set out what you'll need. Note one small thing that went well today. You wake up with direction instead of fog.
>
> A growing number of urban Indian millennials are also reclaiming the first 20 minutes after waking as a phone-free zone. No feed. No notifications. Just warm water, a stretch, or quiet chai. Start the day from your own centre.

**Example (incorrect — too listy for Option 1):**
> Here are the things to do before bed: write your task, set out your bag, note one win.

---

### OPTION 2 — Narrative + Stat Card

**Visual appearance:** One paragraph of prose followed by a visually distinct card containing a large number/statistic and a short explanatory line beneath it.

**When to use:**
- When there is a compelling data point that anchors the section's argument
- When the number makes the insight more real or urgent than prose alone can
- When the stat is surprising enough to be a visual moment in itself
- Use sparingly — maximum once per article, ideally in the section that most needs credibility reinforcement

**Narrative rules:**
- The paragraph before the stat card sets up *why* the number matters
- The stat card itself contains: the number/stat (large, accent-coloured) + a 1–2 line explanation beneath it
- The paragraph should not repeat what the stat card says — it should create the context that makes the stat land
- After the stat card, the section can continue with 1 more paragraph OR proceed to the deep dive button

**Stat card writing rules:**
- The number should be the most visually arresting element: `28%` or `15–23 minutes` or `₹72 billion`
- The explanation line beneath: 1–2 sentences maximum, muted tone, source attribution in parentheses
- Example:
  ```
  28%
  India's wellness market annual growth rate — nearly 4× the global average.
  Indians are investing in doing life better. (FICCI-EY / Global Wellness Institute, 2025–26)
  ```

**Example (correct):**
> Every interruption doesn't just cost 2 seconds. Research on cognitive recovery shows the brain takes 15–23 minutes to return to deep focus after an interruption. Ten interruptions a day means up to four hours of scattered thinking. The fix takes three minutes: go into your settings and revoke notification permissions for every app except calls, messages, and calendar.
>
> [STAT CARD: 28% / India's wellness market annual growth rate...]

---

### OPTION 3 — Point-Wise Facts (Structured List)

**Visual appearance:** A list of bullet items where each item follows the pattern: **Bold keyword/label.** followed by a descriptive sentence or two.

**When to use:**
- When the section covers multiple distinct, parallel items (techniques, rules, principles)
- When each item is short enough to not need its own section but specific enough to need its own label
- When the reader will benefit from being able to scan the items individually
- When the section is instructional or reference-like rather than narrative

**Narrative rules:**
- 3–5 bullet items maximum. More than 5 becomes a list dump — break it into a sub-section instead.
- Each item: **Bold label (1–4 words).** followed by 1–2 sentences of context/explanation
- The bold label should be the named concept, technique, or thing — not a generic verb
- Items should be written in parallel grammatical structure
- A brief 1-sentence intro before the list to frame what's being listed

**Example (correct):**
> Three techniques that save dishes when something goes wrong:
>
> - **Over-salted dish.** Add chunks of raw potato and simmer for 10–15 minutes. The starch absorbs excess salt. Remove before serving — this is chemistry, not folklore.
> - **Watery curry.** Don't boil it down on high heat — this overcooks vegetables and makes meat rubbery. Instead, dry-roast a tablespoon of poppy seeds, grind fine, and stir in. It thickens naturally without altering the flavour profile.
> - **Perfect biryani grains.** Add a few drops of lemon juice, a pinch of salt, and a drop of oil to the cooking water before adding rice. The lemon breaks down surface starch and keeps every grain distinct.

**Example (incorrect — too short per item, reads like a checklist):**
> - Salt: use potato
> - Curry: use poppy seeds
> - Biryani: use lemon

---

### OPTION 4 — Mixed Narrative + Embedded Steps

**Visual appearance:** A short prose paragraph followed by a numbered step sequence (1. 2. 3.), then an optional closing observation.

**When to use:**
- When the section describes a process or ritual with a specific sequence
- When the order of steps matters and must be preserved
- When prose alone would be unclear but a pure list would lose the warmth
- Example use cases: the evening reset routine, the Sunday prep sequence, a step-by-step technique

**Narrative rules:**
- Opening paragraph: 2–3 sentences setting up what the process is and why it works
- Steps: numbered, 1 sentence each, in strict sequence
- Closing observation (optional): 1 sentence that frames the payoff or adds a human touch
- The steps should be specific and actionable — not vague verbs

**Example (correct):**
> The 10-minute evening reset returns your home to neutral before sleep. Not cleaning — resetting. There's a difference.
>
> 1. Kitchen (3 min): rinse dishes, wipe counter, put away anything left out
> 2. Living space (2 min): clothes off the floor, surfaces cleared, cushions straightened
> 3. Tomorrow prep (2 min): bag packed, charger plugged in, keys on hook
> 4. Walk-through (1 min): one pass through each room — close it down visually
> 5. Your signal (2 min): whatever marks the day as done for you
>
> Ten minutes the night before saves 25 stressed minutes the next morning.

---

## PART 6: VISUAL RHYTHM — VARYING CONTENT OPTIONS ACROSS SECTIONS

The sequence of content block options across an article creates its visual rhythm. A good article should never feel monotonous. The goal is variation that feels intentional, not random.

### 6.1 The Rhythm Rule

Never use the same content option for two consecutive sections. Exception: Option 1 (Pure Narrative) can appear twice consecutively only if the two sections are very short and tonally different.

### 6.2 Recommended Rhythm Patterns by Article Type

**Lifestyle / Life Hacks articles (4–5 sections):**
```
Section 1: Option 1 (Narrative)        ← warm entry into the article
Section 2: Option 2 (Narrative + Stat) ← credibility anchor
Section 3: Option 3 (Point-Wise)       ← actionable specifics
Section 4: Option 1 or 4 (Narrative or Steps) ← depth or process
Section 5: Option 1 (Narrative)        ← reflective close
```

**Kitchen / Recipe articles (3–5 sections):**
```
Section 1: Option 1 (Narrative)        ← warm context
Section 2: Option 4 (Steps)            ← process/technique
Section 3: Option 3 (Point-Wise)       ← multiple tips
Section 4: Option 1 (Narrative)        ← reflection or wisdom
```

**Articles with a Pattern B section (sub-section cards):**
- The Pattern B section always uses its own layout (intro paragraph + cards) regardless of content options
- Treat the Pattern B section as its own visual block — do not assign a content option to it
- The sections before and after a Pattern B section should use Option 1 to provide clean transitions

### 6.3 Content Option Assignment Field in JSON

Each section in the JSON must include a `content_option` field:
```json
{
  "section_id": "sec_lf_01",
  "title": "The Interruption Tax Nobody's Counting",
  "content_option": "2",
  "stat_card": {
    "value": "28%",
    "explanation": "India's wellness market annual growth rate — nearly 4× the global average. (FICCI-EY / Global Wellness Institute, 2025–26)"
  }
}
```

Valid values: `"1"`, `"2"`, `"3"`, `"4"`, `"B"` (for Pattern B sub-section card sections)

---

## PART 7: THE DEEP DIVE BUTTON

When a section has a Pattern B sub-section, a deep dive button appears at the bottom of that section's content block.

### 7.1 Button Placement

- Always at the **bottom** of the section, after all prose content
- If the section uses Option 2, the button appears after the stat card
- If the section uses Option 3, the button appears after the last bullet item
- Never mid-paragraph, never before the content

### 7.2 Button Label Writing Rules

The button label must be:
- Specific to what the deep dive contains — not generic ("Read more", "Learn more", "Expand")
- Written as: `Deep dive: [specific topic]`
- Maximum 6 words after the colon
- Examples:
  - `Deep dive: The 5-Minute Night Ritual ›`
  - `Deep dive: Renegotiate Your Phone Relationship ›`
  - `Deep dive: Task Systems That Don't Fall Apart ›`
  - `Deep dive: Notification Audit on iOS & Android ›`

The `›` chevron at the end signals interactivity. It rotates when expanded.

### 7.3 Button Spec in JSON

```json
{
  "section_id": "sec_lf_02",
  "deep_dive_button": {
    "label": "Deep dive: Renegotiate Your Phone Relationship",
    "sub_section_id": "sub_lf_02"
  }
}
```

---

## PART 8: NARRATION FLOW PRINCIPLES

Beyond structure, the agent must follow narration principles that create the feeling of reading a smart, warm article rather than a formatted document.

### 8.1 The Three-Beat Section

Every section should have a three-beat structure, even within the chosen content option:

```
Beat 1 — The Observation or Setup     (why this matters / the problem / the context)
Beat 2 — The Insight or Technique     (the specific thing to know or do)
Beat 3 — The Payoff or Human Touch    (what changes as a result / a moment of warmth)
```

Not every beat needs a full paragraph. The setup can be a single sentence. The payoff can be a closing line. But all three should be present.

**Example — three beats in Option 1:**
> [Beat 1] Most to-do lists fail for the same reason: they try to capture tasks and prioritize tasks at the same time — two completely different cognitive operations forced into one action.
>
> [Beat 2] Each evening, make two lists. **List 1:** everything on your mind without filtering. **List 2:** exactly three tasks for tomorrow. Sleep on List 1. Work from List 2.
>
> [Beat 3] When those three tasks are done, the day is a win — regardless of everything else that happened.

### 8.2 The Tonal Arc Across Sections

An article should have a tonal arc — it should not maintain the same emotional register from start to finish.

```
Opening sections:     Warm, relatable, slightly disarming — meet the reader where they are
Middle sections:      Specific, actionable, confident — deliver the value
Final section(s):     Reflective, human, grounding — leave the reader with something that lingers
```

The final section should never be the most instructional — it should feel like a breath out after the article's ideas have landed.

### 8.3 Sentence Rhythm Rules

- **Short sentences for impact.** Use them at the start of a section or as a closing beat. They create emphasis and pause.
- **Longer sentences for nuance.** Use them to carry complex ideas, qualification, or context.
- **Never more than 3 long sentences in a row.** Break them up.
- **The closing line of each section should be short.** It's the line the reader carries into the next section.

### 8.4 Transitions Between Sections

The sections should not feel like separate documents stapled together. The visual separator (a horizontal rule) handles the visual break — the content itself should flow.

Rules for section transitions:
- The last line of a section should create a natural lead-out — a sense of completion, not a cliff-hanger
- The first line of the next section should start fresh — not reference the previous section
- The section label and title reorient the reader so no prose transition phrase is needed ("Now let's look at...", "Moving on to...", "Another important thing is...")
- Never use transition phrases. Let the structure do the work.

---

## PART 9: THE QUICK REFERENCE BLOCK

This block appears after all sections, before the sources footer.

### 9.1 Purpose

The Quick Reference is a scannable action list for readers who want to take something concrete from the article. It is not a summary — it is an action checklist.

### 9.2 Writing Rules

- 5 items maximum. Each item: 1 sentence, starts with an action verb or a specific thing to do
- Written in imperative mood: "Do X", "Try X", "Set X"
- Ordered from most immediate/easy to most requiring of commitment
- No repetition of exact phrasing from the article body — these should feel like distilled instructions, not quotes

### 9.3 Heading

The heading for this block should match the article's tone. Options:
- "Quick Reference"
- "Start Here"
- "Your Action List"
- "Try These First"

---

## PART 10: AGENT INSTRUCTIONS — GENERATING TO THIS SPEC

When generating article content, the agent must follow this sequence:

### Step 1: Plan the Narrative Stack
Before writing a single word of content, map the article's structure:
```
title_line_1: ___
title_line_2: ___
descriptor: ___
hook_type: A or B
hook_text: ___
sections:
  - label, title, content_option, has_stat_card, has_deep_dive
  - (repeat for each section)
quick_reference_items: 5 items
```

### Step 2: Write the Hook First
The hook determines the article's voice. Write it before any section content. If the hook feels flat or generic, the article will feel flat throughout.

### Step 3: Write Sections in Sequence
Write sections in reading order. The tonal arc (Part 8.2) depends on knowing where you are in the sequence. Don't write all sections independently and then assemble them.

### Step 4: Verify Visual Rhythm
Before finalising, check the sequence of content options. No two consecutive sections should use the same option. Adjust if needed.

### Step 5: Write the Quick Reference Last
The Quick Reference items should be written after the full article, extracted and distilled from the content — not invented independently.

### Step 6: Assign JSON Fields
Add to each section in the JSON:
- `content_option`: "1", "2", "3", "4", or "B"
- `stat_card`: populated if content_option is "2"
- `deep_dive_button`: populated if section has a Pattern B sub-section

---

## PART 11: CONTENT OPTION EXAMPLES AT A GLANCE

| Option | Best for | Visual feel | Avoid when |
|---|---|---|---|
| 1 — Pure Narrative | Insights, observations, reflective points | Warm, flowing, literary | The idea has multiple distinct sub-points |
| 2 — Narrative + Stat | Data-backed arguments, credibility moments | Grounded, authoritative, visual anchor | You don't have a genuinely striking data point |
| 3 — Point-Wise Facts | Multiple parallel techniques, rules, or tips | Scannable, structured, reference-like | You have fewer than 3 points (use Option 1) |
| 4 — Mixed + Steps | Processes, rituals, sequences | Clear, methodical, still warm | The process has more than 7 steps (break into sub-section) |
| B — Cards (Pattern B) | Multiple parallel items needing 200+ words each | Visual grid, interactive, lazy-fetch | Fewer than 2 items, or items usable as summaries |

---

## PART 12: FULL SECTION JSON SCHEMA UPDATE

The following fields are added to each section object in the JSON (extending Content Spec v3.0 schema):

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
    "explanation": "India's wellness market annual growth rate — nearly 4× the global average. Indians are investing in doing life better. (FICCI-EY / Global Wellness Institute, 2025–26)"
  },
  "deep_dive_button": null,
  "sub_sections": null
}
```

And at the article level, add:
```json
{
  "hero": {
    "title_line_1": "Reclaim",
    "title_line_2": "Your Focus.",
    "descriptor": "The life hacks that actually fit Indian life — for calmer mornings, sharper focus, and a daily rhythm that just works.",
    "hook_type": "A",
    "hook_text": "The most effective people aren't doing more. They're doing less, better — with small, intelligent defaults that quietly compound."
  },
  "tonal_arc": ["warm", "credibility", "instructional", "reflective"],
  "content_option_sequence": ["1", "2", "3", "1"]
}
```

---

## PART 13: WORKED EXAMPLE — FOCUS ARTICLE NARRATIVE PLAN

This shows the full narrative plan for `lifehacks_focus` before any prose is written:

```
HERO
  title_line_1: "Reclaim"
  title_line_2: "Your Focus."
  descriptor: "What costs you 4 hours a day without you noticing — and the 3-minute fix."
  hook_type: A
  hook_text: "You're not distracted. You're interrupted. There's a difference."

SECTION 1
  label: 📵 FOCUS
  title: "The Interruption Tax Nobody's Counting"
  content_option: 2
  stat_card: "28% / India's wellness market growth rate..."
  beat_1: The hidden cost of interruptions (15–23 min recovery)
  beat_2: The 3-minute notification audit (specific iOS + Android steps)
  beat_3: Closing: "You're not losing the notification moment. You're losing everything that follows."
  deep_dive: null (steps are short enough to be inline)

SECTION 2
  label: 🎯 ATTENTION
  title: "The One-Screen Rule"
  content_option: 1
  beat_1: Home screen as most-visited real estate, filled with trap apps
  beat_2: Move social apps to second screen — the friction is the feature
  beat_3: "You choose to open Instagram. You don't just find yourself in it."

SECTION 3
  label: ⏱ WORK
  title: "Deep Work in an Indian Office Context"
  content_option: 3
  items:
    - 90-minute block · schedule it, protect it, communicate it
    - Check-in windows · 11 AM and 4 PM — tell your team
    - Headphones = DND · understood in most Indian offices

SECTION 4
  label: 🌿 REST
  title: "Schedule Your Offline Time Like a Meeting"
  content_option: 1
  beat_1: Brain restores attention through genuine unstimulation, not screen-switching
  beat_2: 15-minute daily offline window, same time, treated like a meeting
  beat_3: "Treat it like any other meeting: block it, protect it, show up for it."

CONTENT OPTION SEQUENCE: [2, 1, 3, 1] ✓ — no two consecutive same
TONAL ARC: credibility anchor → warm insight → practical list → reflective close ✓
```

---

*Spec version: 1.0 · Companion to Content Spec v3.0*
*March 2026 — India Discovery Platform*
