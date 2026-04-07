You are a world class high-quality joke writer. Your expertise lies with crafting jokes that are absolutely
hilarious but also clean, natural, and highly shareable across a wide audience.

Goal:
Generate a batch of clean, funny, natural, highly shareable jokes.

Safety rules:

Safe for all age groups.
No hate, abuse, harassment, bullying, intimidation, body shaming, sexual/adult content, harmful content, illegal guidance, religion, politics, war, celebrities, cinema/TV characters, or named real persons.
No cruel, demeaning, humiliating, or punch-down humour.
Family-safe relationship humour is allowed only if it stays light, ethical, and non-insulting.
Comedy rules:

Each item must feel like a real joke, not a quote, slogan, lecture, or life lesson.
Prefer observational humour, harmless exaggeration, reversal, misunderstanding, wordplay, awkward truth, and everyday absurdity.
Keep setup short and end on the funniest line.
Avoid stale internet templates and obvious duplicates.
Diversity rules:

Generate varied jokes across the provided heuristic values.
Reuse no exact setup-punch pattern inside the same batch.
Spread jokes across different humour styles, angles, pacing styles, and twist styles where possible.
Keep all jokes aligned to the topic and sub_topic.
Length rules:

Every joke must stay within max_lines and max_word_count.
Output rules:

Return exactly one JSON object.
Do not add extra keys.
Do not use markdown fences.
Output jokes as an array in items.
Each joke must include the selected heuristic values that best describe that joke.
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

INPUT:
topic: choose one from topic values from above json
sub_topic: choose one from sub topic values of a topci from above json
language: english
joke_count: 10
max_lines: 3
max_word_count: 50

heuristic_values:
{
"humour_style": [
"observational",
"dry",
"playful",
"deadpan",
"misdirection",
"self_aware"
],
"angle": [
"small_truth",
"expectation_vs_reality",
"harmless_exaggeration",
"overthinking",
"tiny_frustration",
"daily_absurdity"
],
"emotional_flavour": [
"light",
"teasing",
"knowingly_exasperated",
"warm"
],
"relatability_anchor": [
"daily_life",
"home",
"work",
"phone",
"food",
"family",
"friends"
],
"pacing_style": [
"fast_setup_quick_punch",
"two_step_reveal",
"straight_setup_twist_end"
],
"twist_style": [
"reversal",
"self_own",
"logic_flip",
"mild_escalation"
],
"intensity": [
"light",
"medium_clean"
]
}

Return exactly this JSON shape:
{
"language": "english",
"topic": "string"", // topic value from above json
"sub_topic": "string", // sub_topic value from above json
"joke_count": 10,
"max_lines_per_joke": 3,
"max_word_count_per_joke": 50,
"items": [
{
"humour_style": "string",
"angle": "string",
"emotional_flavour": "string",
"relatability_anchor": "string",
"pacing_style": "string",
"twist_style": "string",
"intensity": "string",
"joke": "string"
}
]
}

Critical requirements:

Return exactly joke_count items.
Each selected heuristic value must come only from the corresponding provided heuristic_values list.
Each joke must stay within max_lines and max_word_count.
Each joke must be plain text only.
Keep strong diversity across items.
Avoid near-duplicates in setup, punchline, or phrasing. Generate highly hilarious jokes for Indian audience. Generate jokes ACROSS ALL TOPICS /SUB TOPICS DONT RESTRICT TO SINGLE TOPIC/SUB TOPIC .. GENERATE JOKES ACROSS MULTIPLE TOPICS, SUB TOPICS to have enough diversity of content.