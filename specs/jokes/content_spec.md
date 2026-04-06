Below is the **optimal compact batch-friendly prompt** for joke generation.

## 1) Optimal prompt

```yaml id="j8h2rc"
joke_gen_v1:
  name: joke_gen_v1
  version: 1

  system_prompt: |
    You are a high-quality joke writer.

    Goal:
    Generate one short joke that is clean, funny, natural, and highly shareable.

    Hard safety rules:
    - Safe for all age groups.
    - No hate, abuse, harassment, intimidation, bullying, body shaming, sexual content, adult content, harmful content, illegal guidance, religion, politics, war, celebrities, cinema/TV characters, or named real persons.
    - No demeaning jokes about identity, disability, illness, appearance, class, profession, or family role.
    - No cruel humour, punch-down humour, or humiliation-based humour.
    - Keep it ethical, light, and broadly relatable.

    Comedy rules:
    - The joke must feel like a real joke, not a quote, slogan, lecture, or life lesson.
    - Prioritize observational humour, harmless exaggeration, reversal, misunderstanding, wordplay, awkward truth, or everyday absurdity.
    - Keep it crisp.
    - End on the funniest line.
    - Avoid generic filler and over-explaining the setup.
    - Avoid repeating common internet joke templates.

    Style rules:
    - Write in {language}.
    - Keep the humour natural for the language, not translated literally from another language.
    - Use only culturally safe, everyday references.
    - Keep it suitable for text cards, social posts, or chat forwards.

    Length rules:
    - Max lines: {max_lines}
    - Max words: {max_word_count}
    - Never exceed either limit.

    Diversity rules:
    - Follow the selected topic, sub_topic, and heuristics for this run.
    - Use the selected humour style and angle.
    - Do not drift into a different joke type.
    - Avoid obvious duplicates of standard jokes on the same theme.

    Output rules:
    - Return plain text only.
    - Return exactly one joke.
    - No title.
    - No bullets.
    - No explanation.
    - No hashtags.
    - No emojis unless explicitly requested.

  runtime_input_block: |
    topic: {topic}
    sub_topic: {sub_topic}
    language: {language}
    max_lines: {max_lines}
    max_word_count: {max_word_count}

    heuristics:
      humour_style: {humour_style}
      angle: {angle}
      emotional_flavour: {emotional_flavour}
      relatability_anchor: {relatability_anchor}
      pacing_style: {pacing_style}
      twist_style: {twist_style}
      intensity: {intensity}
      taboo_filter: strict_safe_clean
```

## 2) Best structure for your use case

Use **one prompt only** for joke generation.
Do not split into moderation/eval/refine unless you later observe bad outputs at scale.

Reason:

* jokes are short
* cost sensitivity is high
* the guard rails can be enforced directly in one compact prompt
* batch diversity can come from rotating topic/subtopic + heuristics

## 3) Recommended output modes

### Mode A

* `max_lines = 3`
* `max_word_count = 50`

### Mode B

* `max_lines = 5`
* `max_word_count = 100`

That is enough. No need for separate prompts.

---

## 4) Topic + sub-topic JSON seed

Use this as your rotating topic bank.

```json id="knm1mo"
{
  "topics": [
    {
      "topic": "Everyday Life",
      "sub_topics": [
        "Morning rush",
        "Overthinking small things",
        "Being too tired to be productive",
        "Trying to be organized",
        "Weekend plans vs reality"
      ]
    },
    {
      "topic": "Home Life",
      "sub_topics": [
        "Household chores",
        "Misplaced items",
        "Kitchen confusion",
        "Laundry delays",
        "Random things kept for later"
      ]
    },
    {
      "topic": "Work Life",
      "sub_topics": [
        "Meetings that should have been messages",
        "Replying professionally while confused",
        "Deadlines and last-minute panic",
        "Pretending to understand jargon",
        "Work from home habits"
      ]
    },
    {
      "topic": "Digital Life",
      "sub_topics": [
        "Too many notifications",
        "OTP frustration",
        "Weak internet timing",
        "Group chat chaos",
        "Battery anxiety"
      ]
    },
    {
      "topic": "Shopping and Money",
      "sub_topics": [
        "Impulse buying logic",
        "Discount traps",
        "Adding to cart and never buying",
        "Budgeting optimism",
        "Tiny expenses that multiply"
      ]
    },
    {
      "topic": "Food and Eating",
      "sub_topics": [
        "Ordering food vs cooking",
        "Snacking without planning to",
        "Tea or coffee dependency",
        "Eating healthy tomorrow",
        "Fridge reality"
      ]
    },
    {
      "topic": "Travel and Commute",
      "sub_topics": [
        "Traffic patience",
        "Leaving early and still being late",
        "Packing too much",
        "Public transport timing",
        "Cab driver small talk"
      ]
    },
    {
      "topic": "Friends and Social Life",
      "sub_topics": [
        "Making plans that never happen",
        "Replying late to messages",
        "Saying on my way while not ready",
        "Group photo behaviour",
        "Social energy running out"
      ]
    },
    {
      "topic": "Family-safe Relationship Humor",
      "sub_topics": [
        "Wife and husband everyday misunderstandings",
        "Who remembers what at home",
        "Tiny arguments over simple things",
        "Different definitions of ready in 5 minutes",
        "Selective listening moments"
      ]
    },
    {
      "topic": "Self vs Reality",
      "sub_topics": [
        "High expectations, low effort",
        "Trying to fix life in one day",
        "Motivation disappearing quickly",
        "Talking big, doing small",
        "Confidence before the task starts"
      ]
    }
  ]
}
```

---

## 5) Heuristics for diversity rotation

Use these pools.

```json id="p0i73p"
{
  "heuristics": {
    "humour_style_pool": [
      "observational",
      "dry",
      "playful",
      "deadpan",
      "mild_wordplay",
      "misdirection",
      "self_aware"
    ],
    "angle_pool": [
      "small_truth",
      "daily_absurdity",
      "expectation_vs_reality",
      "harmless_exaggeration",
      "misunderstanding",
      "overthinking",
      "tiny_frustration"
    ],
    "emotional_flavour_pool": [
      "light",
      "warm",
      "teasing",
      "gentle",
      "knowingly_exasperated"
    ],
    "relatability_anchor_pool": [
      "home",
      "work",
      "phone",
      "food",
      "commute",
      "shopping",
      "family",
      "friends"
    ],
    "pacing_style_pool": [
      "fast_setup_quick_punch",
      "slow_build_sharp_end",
      "two_step_reveal",
      "straight_setup_twist_end"
    ],
    "twist_style_pool": [
      "reversal",
      "literal_interpretation",
      "unexpected_comparison",
      "self_own",
      "logic_flip",
      "mild_escalation"
    ],
    "intensity_pool": [
      "very_light",
      "light",
      "medium_clean"
    ]
  }
}
```

---

## 6) Best runtime rotation strategy

For each batch run, rotate:

* `topic`
* `sub_topic`
* `language`
* `humour_style`
* `angle`
* `twist_style`
* `pacing_style`

Keep fixed most of the time:

* `intensity = light`
* `taboo_filter = strict_safe_clean`

This gives diversity without needing multi-pass repair.

## 7) Good default config

```json id="qkduju"
{
  "language": "English",
  "max_lines": 3,
  "max_word_count": 50,
  "humour_style": "observational",
  "angle": "expectation_vs_reality",
  "emotional_flavour": "light",
  "relatability_anchor": "daily_life",
  "pacing_style": "fast_setup_quick_punch",
  "twist_style": "reversal",
  "intensity": "light"
}
```

## 8) Important note on wife/husband jokes

Yes, you can allow them **if** they stay:

* harmless
* everyday
* non-abusive
* non-sexual
* non-demeaning
* non-stereotype-heavy

So the prompt should not ban them outright; it should ban **cruel or insulting framing**.

## 9) Final recommendation

For batch workloads, this is the best structure:

* single compact prompt
* runtime-controlled topic/subtopic/language
* rotating humour heuristics
* strict safe-clean rules inline
* no second-pass by default

Next pass, we can build the **top 10 India-viral-safe joke topics** plus a stronger anti-duplication heuristic pack.
