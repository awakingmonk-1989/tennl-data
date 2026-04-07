# SKILL: Creativity & Narration Flow Alignment
## India Discovery Platform — Narrative Quality & Visual Flow Evaluation
### Version 1.0 · March 2026

---

## PURPOSE

This skill evaluates the narrative quality, creative strength, and visual
flow alignment of a generated article. It runs after Content Moderation
passes. It does not check safety — that is Content Moderation's job.

This skill answers three questions:
1. Is the storytelling genuinely good — warm, specific, surprising?
2. Does the narrative flow align with how the page will look and feel visually?
3. Does the content option sequence create the right visual rhythm for the reader?

**Spec this skill references:**
- `/specs/narration_flow_spec_v1_1.md` — all parts

Output: a scored evaluation report with specific improvement notes.
If score is below threshold, specific revisions are recommended.

---

## INPUT

The complete output from Content Generation (after Content Moderation PASS):
- Article body (markdown)
- JSON object

---

## EVALUATION FRAMEWORK

### Score Scale

Each dimension scored 1–5:
- 5: Excellent — meets the standard fully, no improvement needed
- 4: Good — meets standard with minor gaps
- 3: Acceptable — meets minimum bar but notable improvement possible
- 2: Weak — below standard, revision recommended
- 1: Failing — does not meet standard, revision required

Threshold for proceeding without revision: all dimensions ≥ 3,
overall average ≥ 3.5. Below threshold: return specific revision notes.

---

## DIMENSION 1: HOOK QUALITY (page-level)

Evaluate the hook block (quote_banner or lede paragraph).

**Scoring criteria:**

5 — First sentence is genuinely unexpected. Avoids all generic openers.
    Makes the reader feel understood. Creates curiosity without promising
    something the article cannot deliver. Reads like a person, not a system.

4 — Strong opening, minor predictability in phrasing. Still compelling.

3 — Acceptable but could be more specific or surprising. No forbidden
    openers but lacks a genuine moment of delight.

2 — Generic or summarising. Could have been written about any article
    on this topic. Weak voice.

1 — Begins with a forbidden opener ("In today's fast-paced world...",
    "It is important to note...", "We all know...") or is purely
    descriptive of the article content.

**Specific checks:**
→ Does the hook make the reader feel seen rather than lectured?
→ Is there a counterintuitive truth, surprising angle, or specific detail?
→ Is it max 3 sentences?
→ Does it set a warm, witty, or pointed voice for the page?

SCORE: __ / 5
NOTES: [specific observation]

---

## DIMENSION 2: TITLE QUALITY (page-level)

Evaluate title_line_1, title_line_2, and descriptor.

**Scoring criteria:**

5 — Two-line title creates visual impact and intrigue. Line 2 completes
    line 1 in an unexpected or satisfying way. Descriptor is a genuine
    promise — specific, benefit-focused, max 15 words. Together they
    would stop a thumb mid-scroll.

4 — Strong but line 2 is slightly predictable. Descriptor solid.

3 — Title is coherent but not memorable. Descriptor is accurate but
    generic. Would not stand out in a feed.

2 — Title is essentially a label ("Focus & Attention Tips"). Descriptor
    describes the article rather than promising value.

1 — Generic, clickbait, or misleading. Descriptor is too long or absent.

**Specific checks:**
→ Is line 2 typically shorter than line 1?
→ Is the title specific — does it name a concept, not just a topic?
→ Does the descriptor start from the reader's perspective?
→ Does the title earn the article (can the content deliver on its promise)?

SCORE: __ / 5
NOTES: [specific observation]

---

## DIMENSION 3: THREE-BEAT STRUCTURE (per post)

Evaluate each post for the three-beat structure:
- Beat 1: Observation or Setup (why this matters)
- Beat 2: Insight or Technique (the specific thing)
- Beat 3: Payoff or Human Touch (what changes, landing moment)

**Scoring criteria (applied to each post, then averaged):**

5 — All three beats clearly present. Beat 3 is a short, memorable
    closing line. The post feels complete and purposeful.

4 — All three beats present. Beat 3 could be sharper.

3 — Beats 1 and 2 present. Beat 3 is weak or trails off.

2 — Only beats 1 and 2. Post ends without landing. Reader left hanging.

1 — No discernible three-beat structure. Post is a flat information dump.

**Specific checks per post:**
→ Does Beat 1 create genuine context (not just state a fact)?
→ Is Beat 2 specific enough to be actionable or memorable?
→ Is the closing line short? (1 sentence maximum)
→ Does the post feel complete if read independently (standalone post test)?

SCORE: __ / 5 (average across all posts)
NOTES: [per-post observations if any fail]

---

## DIMENSION 4: SENTENCE RHYTHM & VOICE

Evaluate the prose quality across all posts and deep dives.

**Scoring criteria:**

5 — Sentence length varies naturally. Short sentences at openings and
    closings. Longer sentences in the middle. Voice is warm and specific.
    India-specific references feel organic. Never wastes a sentence.

4 — Good rhythm with occasional long-sentence runs. Voice mostly warm.
    Minor stiffness in 1–2 passages.

3 — Adequate prose. Some passages read as formulaic. India-specific
    references feel slightly forced in places.

2 — Long sentence runs dominate. Prose feels like a document rather
    than a read. Voice is generic or formal.

1 — No rhythm variation. Sounds like AI output or a listicle. India
    context absent or artificially inserted.

**Specific checks:**
→ Are there any 3+ consecutive long sentences? (flag each instance)
→ Does each post end with a short, punchy line?
→ Are India-specific references (chai, commute, UPI, etc.) natural?
→ Is passive voice used anywhere? (flag each instance)
→ Are forbidden phrases present? ("In conclusion", "It is important
  to note", transition phrases like "Moving on to...")

SCORE: __ / 5
NOTES: [specific flagged passages]

---

## DIMENSION 5: CONTENT OPTION VARIETY & VISUAL RHYTHM

Evaluate the content_option_sequence for visual rhythm.

**Scoring criteria:**

5 — Sequence creates clear visual rhythm. No two consecutive options
    are identical. Mix of narrative, list, and visual elements feels
    intentional. Tonal arc matches the sequence (warm → instructional
    → reflective or similar natural arc).

4 — Good variety. One section could be a different option for better
    contrast but not a significant issue.

3 — Acceptable variety but some monotony. Two consecutive similar
    options (e.g. two Option 1s in a row) present.

2 — Limited variety. Three or more of the same option in adjacent
    sections. Visual rhythm flat.

1 — All or most sections use the same content option. No visual rhythm.

**Specific checks:**
→ Verify content_option_sequence has no two consecutive identical values
  (this is also a JSON validation rule — flag here if still present)
→ Does the sequence match the tonal_arc in pacing?
→ Is Option 5 (Highlight Banner) used to mark a distinctly India-specific
  or standout section? If used elsewhere, flag.
→ Is Option B (Sub-section Cards) justified? (≥2 items, each genuinely
  unusable as a summary)

SCORE: __ / 5
NOTES: [sequence and arc observations]

---

## DIMENSION 6: DEEP DIVE QUALITY

Evaluate each deep dive (if present) for variant appropriateness and quality.

**Scoring criteria:**

5 — Correct variant chosen for the content type. Variant B intro is
    genuinely catchy (3–4 lines, hooks immediately). Variant A step
    titles are named, not just "Step 1". All deep dives add meaningful
    depth without repeating the parent post. time_label present for
    how_to and recipe types.

4 — Correct variant. Minor quality gaps (B intro slightly flat,
    A step names slightly generic).

3 — Variant is acceptable but not optimal. Content adds some depth
    but partially repeats parent post.

2 — Wrong variant for content type. Deep dive largely repeats parent
    post in more words. Variant B intro is a summary not a hook.

1 — Deep dive adds no value. Should not exist or needs full rewrite.

**Specific checks per deep dive:**
→ Is the variant (A/B/C) the correct choice for this content?
  (A: sequential process, B: parallel items, C: distinct concepts)
→ Variant B: is the intro catchy and under 4 lines?
→ Variant A: are step titles named specifically (not "Step 1 — Step One")?
→ Does the deep dive genuinely expand on the parent post, not repeat it?
→ Is time_label populated for how_to_guide and recipe types?
→ Is word count within 200–500?

SCORE: __ / 5 (average if multiple deep dives)
NOTES: [per-deep-dive observations]

---

## DIMENSION 7: INDIA WARMTH & SPECIFICITY

Evaluate how well the article speaks to its specific audience.

**Scoring criteria:**

5 — The article could only have been written for an urban Indian adult.
    References are specific (Bengaluru commute, not "your daily commute").
    The reader feels the article understands their actual life.
    Warm and knowing — never generic "here is how Indians do things."

4 — Good India specificity with occasional generic moments.

3 — Some India-specific references but could mostly be an article for
    any urban professional anywhere.

2 — Minimal India context. Reads as a generic article with Indian
    words inserted.

1 — No meaningful India context. Generic in voice and reference.

**Specific checks:**
→ Are references specific to India (UPI, WhatsApp groups, joint family,
  pressure cooker, bhindi, masala base, chai) or generic?
→ Does the article acknowledge real Indian contexts (late meetings,
  commute time, household dynamics)?
→ Is the tone "knowing and warm" — like writing for someone whose
  life you understand — rather than explaining India to outsiders?

SCORE: __ / 5
NOTES: [specific observations on India context]

---

## DIMENSION 8: QUICK REFERENCE QUALITY (page-level)

Evaluate the quick_reference block.

**Scoring criteria:**

5 — Items are distilled from the article, not generic. Each starts with
    an action verb. Ordered from immediate to commitment-level.
    Variant B (two-column) used when the content genuinely splits
    into immediate vs week-level actions.

4 — Good items, minor ordering or phrasing issues.

3 — Items are relevant but some are vague or not directly from
    the article content.

2 — Items feel invented rather than distilled. Generic action items
    that could apply to any article on the topic.

1 — Items do not relate to the article content or are absent.

SCORE: __ / 5
NOTES: [specific observations]

---

## OUTPUT: CREATIVITY & NARRATION EVALUATION REPORT

```
CREATIVITY & NARRATION EVALUATION REPORT
─────────────────────────────────────────
Article: [slug]
Sub-topic: [sub_topic]
Date: [evaluation_date]

DIMENSION SCORES:
  1. Hook Quality:                    __ / 5
  2. Title Quality:                   __ / 5
  3. Three-Beat Structure:            __ / 5
  4. Sentence Rhythm & Voice:         __ / 5
  5. Content Option Visual Rhythm:    __ / 5
  6. Deep Dive Quality:               __ / 5
  7. India Warmth & Specificity:      __ / 5
  8. Quick Reference Quality:         __ / 5

OVERALL AVERAGE: __ / 5

RESULT: [PASS (avg ≥ 3.5, all dims ≥ 3) / REVISION RECOMMENDED]

REVISION NOTES:
  [For each dimension scoring < 4, provide:]
  — Specific passage or element that needs improvement
  — What the issue is (too generic, wrong rhythm, missing beat, etc.)
  — A concrete direction for the fix (not a full rewrite — a direction)

STRENGTHS:
  [1–3 specific things the article does well — always include this
   even when revisions are needed. Warmth in evaluation matters.]

NEXT STEP:
  → PASS: Proceed to Schema Validation skill
  → REVISION: Return specific notes to Content Generation skill.
              Agent may revise the flagged dimensions only.
              Re-run Content Moderation and this skill after revision.
```
