Here's your complete standalone file. A few notes on what's inside:

**Zero dependencies** — pure HTML5 Canvas + vanilla JS, no libraries. Open it in any browser, works offline.

**What's included in the file:**
- Dark/light mode toggle (🌙/☀️ button top-right), auto-detects system preference
- All 5 jokes built in, cycles through on each button press
- Full state machine: `idle → suspense → laugh → idle`
- Pencil-sketch wobble on every shape for the hand-drawn feel
- Stomach laugh lines, tear streaks, HA/HO/HE bursts, blush cheeks, teeth — all tied to `mouthOpen` progress

**To embed it elsewhere:**
- **React** — paste the `<canvas>` + script into a `useEffect(() => { /* loop */ }, [])` inside a component
- **Mobile (React Native / Flutter WebView)** — just load this HTML file in a `WebView`
- **Trigger from outside** — call `startJoke()` from any JS event (API response, timer, button, etc.) since it's a plain global function