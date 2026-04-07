Yes. Below is a **small locked spec** for a **standalone stateless content-generation agent** using:

* **base metadata pools**
* **runtime-selected values**
* **dynamic prompt composition**

---

# Standalone Content Agent Spec

## 1. Purpose

Generate **one content item per invocation** with:

* bounded creative space
* low drift
* controlled variation
* safe, useful, non-repetitive output structure

This agent is **stateless**.
It does **not** rely on prior session memory.

---

## 2. Control Model

## Layer 1 — Base Metadata

Defines:

* topic
* subtopic
* description
* intent profile
* allowed content mode pool
* allowed angle pool
* allowed tone pool
* allowed hook style pool
* quality constraints

This layer defines the **creative boundary**.

## Layer 2 — Runtime Selector

Before generation, orchestration must choose exactly one value for:

* `content_mode`
* `angle`
* `tone`
* `hook_style`

These are passed into the prompt as **runtime prompt arguments**.

This layer defines the **creative direction for the current run**.

---

## 3. Input Contract

```json id="96990"
{
  "topic_id": "career_growth",
  "topic_name": "Career & Growth",
  "subtopic_id": "career_switch_stories",
  "subtopic_name": "Career Switch Stories",
  "description": "Realistic, relatable, useful content around transitions in work identity, role, or direction.",
  "intent_profile": [
    "relatable",
    "useful",
    "hopeful",
    "grounded"
  ],
  "content_modes": [
    "story",
    "analysis",
    "guide",
    "reflection",
    "comparison"
  ],
  "angle_pool": [
    "personal_experience",
    "decision_support",
    "mistake_recovery",
    "trend_interpretation",
    "myth_busting",
    "practical_breakdown"
  ],
  "tone_pool": [
    "honest",
    "encouraging",
    "calm",
    "grounded"
  ],
  "hook_style_pool": [
    "observation",
    "contrarian",
    "practical_problem",
    "small_truth",
    "unexpected_pattern"
  ],
  "quality_constraints": {
    "must_include": [
      "specific_scenario",
      "realistic_takeaway",
      "non_generic_language"
    ],
    "avoid": [
      "clickbait",
      "template_openings",
      "generic_motivation",
      "repetitive_listicle_style"
    ]
  }
}
```

---

## 4. Runtime Selection Contract

For each run, orchestration must pass:

```json id="40464"
{
  "content_mode": "story",
  "angle": "personal_experience",
  "tone": "honest",
  "hook_style": "observation"
}
```

Rules:

* selected value **must belong to its corresponding pool**
* agent must treat selected values as **mandatory guidance**
* agent must **not override** selected values unless blocked by safety policy

---

## 5. Agent Responsibilities

For each invocation, the agent must:

1. Read base metadata
2. Read runtime-selected values
3. Generate content strictly aligned to:

    * chosen topic/subtopic
    * chosen content mode
    * chosen angle
    * chosen tone
    * chosen hook style
4. Respect all quality constraints
5. Avoid drifting into:

    * unselected modes
    * generic filler
    * repetitive internet-style patterns
    * unsafe or sensitive advice categories

---

## 6. Required Behavior

The agent must:

* stay within the selected `content_mode`
* use the selected `angle` as the main lens
* maintain the selected `tone` consistently
* open using the selected `hook_style`
* reflect the `intent_profile`
* include all `must_include` requirements
* avoid all `avoid` patterns

---

## 7. Prohibited Behavior

The agent must not:

* switch to another content mode mid-generation
* mix multiple primary angles unless explicitly allowed
* default to generic listicle patterns
* use clickbait hooks
* produce vague motivational fluff
* introduce sensitive medical, legal, financial, relationship, or mental health guidance unless explicitly supported by a separately approved content policy

---

## 8. Prompt Composition Rule

Dynamic prompt must be built from:

## A. Base metadata

* topic
* subtopic
* description
* intent profile
* quality constraints

## B. Runtime values

* content mode
* angle
* tone
* hook style

Prompt must clearly state:

* what the content is about
* how it should be written
* what style constraints are mandatory
* what to avoid

---

## 9. Anti-Drift Strategy

Since execution is stateless, drift control must come from:

* bounded metadata pools
* runtime value rotation outside the agent
* strict dynamic prompt construction
* hard constraints on mode / angle / tone / hook

This agent does **not** guarantee cross-run novelty by itself.
Cross-run variation must be handled by the external selector/orchestrator.

---

## 10. Ownership Boundary

## Orchestrator owns:

* pool design
* runtime value rotation
* selection policy
* prompt argument injection

## Agent owns:

* faithful execution
* adherence to selected controls
* quality and safety compliance
* output generation

---

## 11. Minimal Enforcement Rule

For every run:

* exactly **1** `content_mode`
* exactly **1** `angle`
* exactly **1** `tone`
* exactly **1** `hook_style`

No freeform substitution by the agent.

---

## 12. Final Lock

This design is approved for:

* standalone
* independent
* non-session-based
* stateless content generation

Core principle:
**creative freedom comes from curated pools; execution discipline comes from runtime-selected prompt arguments.**
