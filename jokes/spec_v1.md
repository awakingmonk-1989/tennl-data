Perfect — that's a clean contract to work with. So your metadata JSON looks like:

```json
{
  "joke_start": "Why don't scientists trust atoms?",
  "punchline": "Because they make up everything!",
  "joke_end": "Classic!"
}
```

**Here's exactly how the bear logic maps to this:**

---

**State machine driven purely by which field arrives:**

```
joke_start received   →  bear: suspense
                          (head bobs, big eyes, ? floats, hmm...)

punchline received    →  bear: laugh outburst
                          (tilt, shake, stomach bounce, HA HO HE)

joke_end received     →  bear: gentle settle
  (optional, rare)       (small nod, soft smile, back to idle)
                          since it's just 2 words — no big reaction
```

---

**The trigger logic in code terms — dead simple:**

```javascript
function onJokeMetadata(json) {

  if (json.joke_start) {
    showText(json.joke_start);
    setState('suspense');       // bear wonders...
  }

  if (json.punchline) {
    showText(json.punchline);
    setState('laugh');          // bear explodes
  }

  if (json.joke_end) {
    showText(json.joke_end);    // tiny closing note
    scheduleSettle(800);        // brief nod then idle
  }
}
```

---

**Key design decisions based on your spec:**

- `joke_end` is rare + 2 words → **no full laugh replay**, just a small head nod and fade back to idle. Overreacting to "Classic!" would look wrong.
- Fields can arrive **sequentially** (streaming) or **all at once** (batch) — the logic works either way since each field is checked independently.
- If `joke_end` is absent (most cases) → laugh animation naturally settles on its own timer anyway, no special handling needed.

---

Want me to now build this version — where you can paste or type a JSON and the bear reacts to each field in sequence?