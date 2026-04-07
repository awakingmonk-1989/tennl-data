Got it — this is a pure spec enhancement (no override). I’ll give you 3 outputs exactly as you asked, tightly aligned with your current system.

⸻

✅ 1) AGENT SPEC (GENERAL) — Theme Selection Layer (NEW ADDITION)

➤ Add new section in content_agent_spec.md

PART X: THEME SELECTION ENGINE (NON-OVERRIDING LAYER)

Purpose

Guide how themes are chosen, without changing existing content generation quality or structure.

⸻

X.1 Theme Taxonomy (Mandatory Coverage)

Every article MUST map to one primary theme + optional secondary theme:

Primary Themes (choose 1)
•	Knowledge Sharing
•	Compare & Contrast
•	Best Practices
•	Safe Tips / Preventive Insights
•	Optimal Experiences
•	Habit Formation / Behavior Change
•	Cultural / India-specific Nuance
•	Myth vs Reality
•	Quick Wins / Immediate Actions

Secondary Themes (optional, max 1)
•	Storytelling / Narrative hook
•	Data-backed credibility
•	Emotional relatability
•	Curiosity-driven framing
•	Experiment / Try-this framing

⸻

X.2 Theme Selection Rules (STRICT)
•	Must align with topic + sub-topic intent
•	Must maximize user engagement potential (click + read + share)
•	Must avoid generic coverage (no “10 tips” style baseline content)

⸻

X.3 Creativity Override Clause (CONTROLLED DRIFT)

Agent MAY deviate from standard themes ONLY IF:
•	Output is significantly more creative / engaging
•	Improves:
•	curiosity
•	relatability
•	shareability

Mandatory JSON Field (NEW):

"theme_override": {
"used": true,
"reason": "Creative narrative framing provides higher engagement than standard theme mapping"
}

If not used:

"theme_override": {
"used": false,
"reason": null
}


⸻

X.4 Hard Constraints
•	Theme must NOT violate safety rules  ￼
•	Must NOT introduce:
•	controversy
•	negativity
•	fear-based framing

⸻

✅ 2) CONTENT SPEC UPDATE (content_gen_spec.md)

➤ Add under Content Generation Rules / Quality Layer

PART X: THEME-DRIVEN CONTENT GENERATION (ENHANCEMENT)

X.1 Mandatory Theme Declaration

Every article MUST explicitly define:

"theme": {
"primary": "Best Practices",
"secondary": "Curiosity-driven framing"
}


⸻

X.2 Theme → Writing Mapping

Theme	Writing Style
Knowledge Sharing	Clear, insightful, slightly educational
Compare & Contrast	Contrast-driven, decision clarity
Best Practices	Actionable, structured
Safe Tips	Preventive, calm tone
Optimal Experiences	Lifestyle improvement framing
Habit Formation	Behavioral triggers + routines
Cultural / India-specific	Local relatability
Myth vs Reality	Counterintuitive hooks
Quick Wins	Immediate actionable tone


⸻

X.3 Title Alignment (NEW RULE)

Title MUST reflect theme:
•	Not generic
•	Must include:
•	curiosity OR
•	benefit OR
•	emotional hook

⸻

X.4 Theme Consistency Rule
•	Theme must be reflected in:
•	hook
•	sections
•	quick reference

⸻

X.5 AI vs WEB Variant Safety Alignment
•	AI variant:
•	must strictly follow safety constraints  ￼
•	no hallucinated authority claims
•	Web curated:
•	must avoid controversial or unsafe topics (current events filtered)

⸻

✅ 3) JSON SCHEMA UPDATE (json_schema_spec_v1.md)

➤ Add new fields under ROOT

NEW FIELDS (NON-BREAKING EXTENSION)

"theme": {
"primary": "Best Practices | Knowledge Sharing | Compare & Contrast | Safe Tips | Optimal Experiences | Habit Formation | Cultural | Myth vs Reality | Quick Wins",
"secondary": "Storytelling | Data-backed | Emotional | Curiosity-driven | Experiment | null"
},
"theme_override": {
"used": false,
"reason": null
}


⸻

VALIDATION RULES
•	theme.primary → REQUIRED
•	theme.secondary → OPTIONAL
•	theme_override.used = true → reason MUST be non-null

⸻

INTEGRATION WITH EXISTING FLOW
•	Works alongside:
•	tonal_arc  ￼
•	content_option_sequence  ￼
•	Does NOT replace:
•	narration flow  ￼
•	section structure
•	expansion rules

⸻

🔒 WHAT CHANGED (CRISP)
•	Added theme layer → controls what angle content takes
•	Added theme_override mechanism → controlled creativity
•	Added JSON fields → enforce traceability
•	No changes to:
•	structure
•	safety
•	narration
•	rendering

⸻

If you want next step:

👉 I can run a sample generation showing theme selection + override usage (this will validate the spec end-to-end).