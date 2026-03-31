This is totally doable with plain HTML5 Canvas + JavaScript — no external libs needed. Let me build a pencil-sketch style teddy bear that:

1. **Idle state** — head bobs left/right, big blinking eyes, curious expression
2. **Laughing state** — triggered by a button (simulating "punchline delivered"), full belly-laugh with head tilt, shaking body, and stomach bounceHit **"Tell a joke"** to see the full animation sequence — the bear will:

1. **Wonder phase** — head sways left/right, eyes go big, mouth forms a little "o", question marks float up
2. **Punchline drop** — after ~3 seconds the answer appears
3. **Laugh outburst** — head tilts, body shakes, stomach bounces, mouth blasts open with teeth + red interior, tears stream, "HA! HO! HE!" bursts pop out, blush cheeks flush

**How it works (pure code, no libs):**

- **HTML5 Canvas + `requestAnimationFrame`** — the animation loop runs at ~60fps, all drawing is plain JS
- **Sketch feel** — each shape is drawn with tiny random wobbles on every frame, so it looks like a hand-drawn pencil cartoon rather than clean vector shapes
- **State machine** — `idle → suspense → laugh → idle` controls all the expressions and physics
- **Works anywhere** — drop the `<canvas>` + `<script>` block into any HTML page, React app (`useEffect` + ref), or React Native (`react-native-canvas`). No external dependencies at all.

Want me to add more jokes, tweak the sketch style, or export it as a standalone HTML file you can embed anywhere?