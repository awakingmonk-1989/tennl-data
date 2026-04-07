# Agent Workflow Spec
## Content Generation Agentic Workflow — Contract Spec
### Version 1.0 · Locked · March 2026

---

## 1. PURPOSE

This is the authoritative contract for workflow execution integrity.
All workflow runs, refinements, and automation upgrades MUST conform to this spec.

This spec defines:
- stage sequence and routing rules,
- evaluation pass criteria (non-negotiable),
- refine loop behavior and terminal outcomes,
- output contracts and composability constraints.

---

## 2. NOMENCLATURE & CONTENT ANATOMY (MANDATORY)

The workflow must enforce the content anatomy from content specs.

- **Article = Page**: the full composed unit (hero/title, hook, sections, quick reference, sources, metadata).
- **Section = Post**: each section is also a post-level unit that can be rendered independently.
- **Deep Dive**: an expandable child of a section/post only.

### 2.1 Composition Strategy (intentional)

We intentionally use decomposable content structure so UI can:
- render the entire article/page, or
- render independent posts/sections only.

This is a product strategy, not an implementation detail. Workflow outputs MUST preserve this structure.

### 2.2 Hard structure rules

- No deep dives in the main intro section (hook/intro area is page-level only).
- Deep dives must belong to sections/posts only.
- Section/post structure must remain independently renderable and valid.

---

## 3. WORKFLOW STAGES

| Node | Stage | Purpose | Output |
|---|---|---|---|
| N1 | Input Validation | Validate request contract and input schema | Validated input OR terminal input failure |
| N2 | Content Generation | Generate article markdown + typed JSON | `article_md`, `article_json` |
| N3 | Evaluation Gate | Route to evaluation passes (parallel or sequential) | Dispatch |
| N4 | Eval Pass 1 | Safety and guard-rail enforcement | `moderation_report` |
| N5 | Eval Pass 2 | Quality + structure + schema checks | `quality_report`, `schema_report` |
| N6 | Eval Merge | Merge pass outcomes and route | PROCEED / REFINE / FAIL |
| N7 | Refiner | Build structured refinement directives | `refinement_directives` |
| N8 | Regeneration | Regenerate with refinement directives | `article_md`, `article_json` |
| N9 | Final Validation | Final integrity checks | Success OR terminal schema failure |

---

## 4. EVALUATION PASSES (NON-NEGOTIABLE)

### 4.1 Eval Pass 1 — Content Safety & Guard Rails

Eval Pass 1 criteria are **strictly mandatory** and must run as explicit checks:

Structural guard checks:
- No deep dives in main intro section.
- Sections/posts missing deep dives are disallowed.
- No prose-only blobs: convert to bullet items or organized sub-sections
  per content tree when required.

Safety and guard-rail checks:
- Hard safety flags.
- Topic exclusions.
- Deny-list topics (configurable).
- Additional guard rails (configurable JSON policy).
- Real person policy.
- Controversy check.
- Negativity & bias scan.
- Humour evaluation.
- Source exclusions.
- Copyright compliance.
- Image safety.
- JSON safety flags.

Pass result:
- `PASS` only if all checks pass,
- else `FAIL` with explicit violation list.

### 4.2 Eval Pass 2 — Quality & Structure

Eval Pass 2 must enforce BOTH:
1) Creativity/narration quality,
2) Structural/schema correctness.

#### Composition checks (must always run)

- No deep dives in main intro section.
- Sections/posts missing deep dives are disallowed.
- No prose-only blobs: convert to bullet items or organized sub-sections
  per content tree when required.
- Nomenclature integrity: Article = Page (composition), Section = Post.
- Composability intent: sections must be independently renderable as posts
  while still composing into a full page/article.

#### Creativity & Narration checks (must always run)

- Hook quality.
- Title quality.
- Three-beat structure.
- Sentence rhythm & voice.
- Content option visual rhythm.
- Deep dive quality.
- India warmth & specificity.
- Quick reference quality.

#### Schema Validation checks (must always run)

- Root envelope.
- Word count meta.
- Hero, hook, sections.
- Body schemas per option.
- Deep dives, quick reference.
- Narrative metadata.
- Sources, images.

Pass result:
- `PASS` only if quality threshold and structure/schema threshold both pass,
- else `FAIL` with explicit correction directives.

---

## 5. REFINEMENT POLICY

If eval criteria are not met:
- Run at most **1 refine attempt**.
- Refine cycle = regenerate + Eval Pass 1 + Eval Pass 2.

Routing:
- Any eval fail and refine attempts < max → `REFINE`
- Any eval fail and refine attempts >= max → terminal `FAILED_WITH_REASON`
- Both eval passes pass → continue to final validation

---

## 6. TERMINAL OUTCOMES

Workflow must terminate in exactly one state:

1. **GENERATED**
   - Final output valid, all checks passed.

2. **FAILED_WITH_REASON**
   - Eval criteria not met after max refine pass, or
   - Input invalid, runtime failure, or final validation failure.

Every failure must include structured reason payload.

---

## 7. OUTPUT CONTRACT

Core content workflow output:
- `article_md`
- `article_json`

No UI rendering artifacts are required in this workflow contract.
UI rendering is downstream and must consume this content contract.

---

## 8. EXECUTION INTEGRITY REQUIREMENTS

- Evaluators must return deterministic, structured reports.
- Failures must include exact reasons and affected scope.
- No silent corrections without trace.
- No bypass of eval passes.
- No bypass of refine-attempt cap.

---

## 9. VERSIONING

| Field | Value |
|---|---|
| Spec version | 1.0 |
| Created | 2026-03-31 |
| Last updated | 2026-03-31 |
| Status | Locked |

