# SKILL: Content Moderation
## India Discovery Platform — Safety & Quality Gate
### Version 1.0 · March 2026

---

## PURPOSE

This skill is the safety gate. It runs after Content Generation and before
Creativity & Narration evaluation. It checks every piece of generated content
— article body, deep dives, image metadata, and JSON fields — against the
full safety ruleset.

**If any check fails: STOP. Return a violation report. Do not proceed.**
The Content Generation skill must regenerate from scratch with the
violation flagged before this skill is run again.

**Spec this skill references:**
- `/specs/content_spec_v3.md` — Part 3 (Safety), all sections 3.1–3.5

---

## INPUT

The complete output from the Content Generation skill:
- Article body (markdown)
- JSON object

---

## CHECK SEQUENCE

Run every check in order. Do not skip any. All must pass.

---

### CHECK 1: HARD SAFETY FLAGS

Scan the full article body (including deep dive content_md fields in JSON)
for any instance of the following. Any hit = VIOLATION.

```
CATEGORY              WHAT TO LOOK FOR
─────────────────────────────────────────────────────────────────────
Sexual/Adult          Any sexually explicit, suggestive, or adult content.
                      Any content inappropriate for a general audience.

Harmful               Instructions or content that could facilitate harm
                      to a person, group, or property.

Abusive               Harassing, bullying, threatening, or abusive language.

Intimidating          Content designed to create fear, anxiety, or a sense
                      of helplessness in the reader.

Child-Inappropriate   Any content that is unsafe, unsuitable, or potentially
                      harmful to minors — even subtly.

Hate Speech           Any content that demeans, dehumanises, or targets a
                      group based on religion, community, caste, gender,
                      region, language, or identity. Applies regardless of
                      framing or claimed intent.
```

RESULT: Pass / VIOLATION (specify category and offending text)

---

### CHECK 2: TOPIC EXCLUSIONS

Scan article body and all deep dive content for any reference to:

```
EXCLUDED TOPIC        WHAT TO LOOK FOR
─────────────────────────────────────────────────────────────────────
Politics              Political parties, politicians, elections, political
                      ideologies, government policy debates.

Geopolitical Tensions Relations between nations, border disputes, diplomatic
                      conflicts, sanctions, trade wars.

Ongoing Wars          Any reference to active armed conflicts, military
                      operations, or war casualties anywhere in the world.
                      "Ongoing" = active at time of generation.

Sports                Sports events, teams, athletes, leagues, tournaments,
                      match results, or sports incidents of any kind.

Movies/TV/Media       Named movies, TV shows, streaming series, named
                      fictional works or characters.
```

RESULT: Pass / VIOLATION (specify topic and offending text)

---

### CHECK 3: REAL PERSON POLICY

Check article body for any directly named real private individual.
Check article body for any directly named public figure (other than in
a fully professional, masked context).

```
RULE: Named real persons must NOT appear in article body text.
→ Public professionals: must be masked — "a Bengaluru-based food blogger"
→ Private individuals: never appear under any circumstance
→ Full names: only in JSON masked_persons[] field, nowhere else
```

Check JSON masked_persons[] array:
→ Every entry must have masked_as, real_name, and context fields
→ masked_as must be the exact phrase used in article body

RESULT: Pass / VIOLATION (specify name and location in content)

---

### CHECK 4: CONTROVERSY CHECK

Determine content_variant from JSON:

IF content_variant is "CURATED_WEB_WITH_IMAGES" or "CURATED_WEB_NO_IMAGES":
  → Scan for any reference to ongoing controversies — social, cultural,
    corporate, or political — that are currently active.
  → "Ongoing" = controversy that has active public discourse at time of
    generation, not yet resolved or settled.

IF content_variant is "AI_GENERATED":
  → Scan for any reference to historical controversies — events, episodes,
    or figures that carry documented contested history.
  → If there is any documented public disagreement about the event or figure:
    it qualifies as a historical controversy and must be excluded.

When in doubt about whether something qualifies: flag it as a VIOLATION.
The standard is exclusion, not inclusion.

RESULT: Pass / VIOLATION (specify the controversy and content_variant rule)

---

### CHECK 5: NEGATIVITY & BIAS SCAN

Evaluate the overall tone and conclusion of the article:

```
NEGATIVITY
  → Does the article end in negativity, fear, or helplessness?
  → Does any section leave the reader feeling worse rather than better?
  → Rule: Every article must leave the reader with something useful,
    hopeful, or actionable. Negative framing of a problem is permitted
    as setup — the resolution must be constructive.

BIAS
  → Does any content carry explicit or subtle bias against any religion,
    community, caste, gender, region, language, or identity group?
  → Does any India-specific reference generalise or stereotype?
  → Does any content present one group more favourably than another
    in a way that is not factually grounded and relevant to the topic?
```

RESULT: Pass / VIOLATION (specify the tone issue or bias pattern)

---

### CHECK 6: HUMOUR EVALUATION

If the article contains any humorous content:

```
PERMITTED
  ✓ Warmth and wit that makes the reader smile
  ✓ Self-aware observations about shared experiences
  ✓ Gentle irony about universal situations

NOT PERMITTED
  ✗ Humour that works through humiliation of any person or group
  ✗ Humour that punches down at those with less power or visibility
  ✗ Sarcasm directed at a specific community, belief, or identity
  ✗ Jokes whose punchline requires a group to be the butt
```

RESULT: Pass / VIOLATION (specify the humour instance and why it fails)

---

### CHECK 7: SOURCE EXCLUSIONS

Review sources[] array in JSON:

```
→ No source URL should contain reddit.com or quora.com
→ Verify excluded_sources[] contains "Reddit" and "Quora"
```

RESULT: Pass / VIOLATION (specify the excluded source found)

---

### CHECK 8: COPYRIGHT COMPLIANCE

Scan article body for direct reproduction of source text:

```
→ Max ONE short quote per source (under 15 words) in the entire article
→ No paragraph or extended passage reproduced from any source
→ No song lyrics, poem stanzas, or full sentences lifted verbatim
→ All source material must be synthesised and rewritten in the
  article's own voice
```

RESULT: Pass / VIOLATION (specify reproduced text and source)

---

### CHECK 9: IMAGE SAFETY

Review images[] array in JSON:

```
For each image entry:
→ safety_checks.is_content_safe must be true or "unknown"
  → "unknown" is acceptable — it triggers refinement pass
  → false = VIOLATION

→ If is_external_cited_image_source is true:
  → is_image_rendered must be false
  → Rendering an externally-cited image = VIOLATION

→ Images containing identifiable real persons: VIOLATION
→ Images containing sports content: VIOLATION
→ Images containing explicit or adult content: VIOLATION
```

RESULT: Pass / VIOLATION (specify image_id and issue)

---

### CHECK 10: CONTENT SAFETY JSON FLAGS

Verify content_safety{} object in JSON:

```
is_sexually_explicit:           must be false
is_harmful:                     must be false
is_abusive:                     must be false
is_intimidating:                must be false
is_content_safe:                must be true
has_real_person_references:     must be false
has_sports_references:          must be false
has_movie_references:           must be false
```

If any flag is set incorrectly relative to the actual content:
→ Correct the flag AND flag the underlying content violation.

RESULT: Pass / VIOLATION (specify incorrect flag and value)

---

## OUTPUT: MODERATION REPORT

Produce a structured moderation report:

```
CONTENT MODERATION REPORT
─────────────────────────
Article: [slug]
Variant: [content_variant]
Date: [generation_date]

CHECK RESULTS:
  Check 1 — Hard Safety Flags:        [PASS / VIOLATION]
  Check 2 — Topic Exclusions:         [PASS / VIOLATION]
  Check 3 — Real Person Policy:       [PASS / VIOLATION]
  Check 4 — Controversy Check:        [PASS / VIOLATION]
  Check 5 — Negativity & Bias:        [PASS / VIOLATION]
  Check 6 — Humour Evaluation:        [PASS / VIOLATION]
  Check 7 — Source Exclusions:        [PASS / VIOLATION]
  Check 8 — Copyright Compliance:     [PASS / VIOLATION]
  Check 9 — Image Safety:             [PASS / VIOLATION]
  Check 10 — JSON Safety Flags:       [PASS / VIOLATION]

OVERALL RESULT: [PASS / FAIL]

VIOLATIONS FOUND: [N]

VIOLATION DETAILS:
  [If any violations — specify check number, offending content,
   location in article, and recommended action]

NEXT STEP:
  → PASS: Proceed to Creativity & Narration skill
  → FAIL: Return to Content Generation skill with violation report.
          Regenerate from scratch. Do not patch individual violations.
```
