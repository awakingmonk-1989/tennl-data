export interface FeedItem {
  id: string;
  type: "article" | "joke";
  category: string;
  title: string;
  content?: string;
  punchline?: string;
  emoji?: string;
  image?: string;
  imageAlt?: string;
  readTime?: string;
  language?: string;
}

export const feedData: {articles: FeedItem[];jokes: FeedItem[];} = {
  articles: [
  {
    id: "a1",
    type: "article",
    category: "Mindfulness",
    title: "The 5-minute reset that neuroscientists swear by",
    readTime: "4 min",
    image: "https://images.unsplash.com/photo-1715079947268-9b2e384ac20a",
    imageAlt: "Peaceful golden sunrise over misty rolling hills with warm morning light",
    content: `Science has confirmed what meditators have known for centuries: micro-breaks of under 5 minutes can reduce cortisol levels by up to 23%.

The technique is called a "physiological sigh" — two short inhales through the nose followed by one long exhale through the mouth. It activates the parasympathetic nervous system almost instantly.

Researchers at Stanford found that just 3 cycles of this breathing pattern can lower heart rate by 8 beats per minute and significantly reduce feelings of anxiety. The best part? It works anywhere — at your desk, in traffic, or before a difficult conversation.

Try it right now: Inhale deeply, then sniff once more to fully inflate your lungs. Then exhale slowly and completely. Repeat twice. Notice the difference.`
  },
  {
    id: "a2",
    type: "article",
    category: "Technology",
    title: "Why AI remembers your preferences better than you do",
    readTime: "5 min",
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_1c7a6645f-1772225278572.png",
    imageAlt: "Clean white technology visualization with glowing nodes on bright background",
    content: `Modern recommendation systems process over 2,000 behavioral signals per session to understand what you want before you consciously realize it yourself.

This isn't magic — it's pattern recognition at massive scale. Every scroll pause, every re-read, every share creates a data point. Over time, these systems build what researchers call a "preference fingerprint" that is remarkably stable across contexts. The fascinating implication? Your AI knows when you're stressed (shorter attention spans, more scrolling), when you're curious (deeper engagement, more sharing), and when you need comfort (returning to familiar content types).

The question for the next decade isn't whether AI understands you — it's whether you're comfortable with being understood that well.`
  },
  {
    id: "a3",
    type: "article",
    category: "Finance",
    title: "The ₹500 rule that changed how Indians save",
    readTime: "3 min",
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_15f808822-1772282142252.png",
    imageAlt: "Bright clean desk with financial planning notebook and warm sunlight",
    content: `A behavioral economics study conducted across 1,200 households in Pune and Chennai found that one simple rule increased savings rates by 34% over six months.

The rule: Every time you spend ₹500 or more on something non-essential, immediately transfer ₹50 to a separate savings account.

The psychology is elegant. You're not depriving yourself — you're just attaching a small savings action to a spending action you were already going to take. The friction is minimal, but the habit builds rapidly.

Participants reported that after 90 days, the ₹50 transfer felt automatic. Several had increased their self-imposed transfer to ₹100 without prompting. The average savings accumulated over six months: ₹8,400.`
  },
  {
    id: "a4",
    type: "article",
    category: "Science",
    title: "Plants talk to each other. Here's how scientists proved it.",
    readTime: "4 min",
    image: "https://images.unsplash.com/photo-1695607209107-ae42357846c8",
    imageAlt: "Lush bright green forest with sunlight filtering through leaves",
    content: `When a tomato plant is attacked by a caterpillar, it doesn't just defend itself — it sends chemical signals through the air that neighboring plants receive and act upon, pre-activating their own defenses before any caterpillar arrives.

This phenomenon, called "plant communication," was considered fringe science twenty years ago. Today it's one of the most active areas of botanical research. Scientists have identified over 40 distinct volatile compounds that plants use to "speak" to each other. More remarkably, plants connected through underground fungal networks — what researchers call the"wood wide web" — can transfer nutrients and warning signals to related plants even when above-ground communication is blocked.

The forest, it turns out, is not a collection of competing individuals. It's a community.`
  },
  {
    id: "a5",
    type: "article",
    category: "Life",
    title: "The Japanese concept of 'Ma' — and why we've forgotten it",
    readTime: "3 min",
    image: "https://img.rocket.new/generatedImages/rocket_gen_img_11402ea1e-1772095992534.png",
    imageAlt: "Peaceful minimalist Japanese garden with soft morning light and clean white stones",
    content: `In Japanese aesthetics, "Ma" (間) refers to the meaningful pause — the space between notes in music, the silence between words in conversation, the empty space in a painting that makes the filled space significant.

Western productivity culture has largely eliminated Ma from daily life. Every moment must be filled, every silence must be broken, every pause must be justified.

The cost is invisible but cumulative. Without pause, we lose the ability to integrate experience. Without silence, we can't hear our own thoughts. Without empty space, nothing stands out.

Ma is not emptiness — it is the container that gives everything else meaning. The Japanese architect Tadao Ando built entire buildings around it. The musician Miles Davis made it the foundation of jazz.

Today's practice: Find one Ma. Sit with it for two minutes. Don't fill it.`
  }],

  jokes: [
  {
    id: "j1",
    type: "joke",
    category: "Tech",
    emoji: "💻",
    title: "Why do programmers prefer dark mode?",
    content: "Because light attracts bugs.",
    punchline: "And we've had enough of those. 🐛",
    language: "English"
  },
  {
    id: "j2",
    type: "joke",
    category: "Hindi",
    emoji: "😂",
    title: "Ek baar ek AI ne doctor se kaha...",
    content: "Doctor sahab, mujhe bahut thakaan ho rahi hai.",
    punchline: "Doctor bole: 'Aap overloaded hain. Kuch tabs band karo.' 🖥️",
    language: "Hindi"
  },
  {
    id: "j3",
    type: "joke",
    category: "Life",
    emoji: "☕",
    title: "My relationship with coffee",
    content: "I asked my coffee this morning: 'Are you even helping?'",
    punchline: "It said nothing. I said nothing. We understood each other perfectly.",
    language: "English"
  },
  {
    id: "j4",
    type: "joke",
    category: "Tamil",
    emoji: "🤣",
    title: "Software engineer office la...",
    content: "Manager: 'Enna problem? Bug fix aagala?'\nEngineer: 'Aagudhu sir, but naan fix pannumbodhe rendu new bugs varudhu.'",
    punchline: "Manager: 'That's called job security da.' 😅",
    language: "Tamil"
  },
  {
    id: "j5",
    type: "joke",
    category: "Universal",
    emoji: "🧠",
    title: "My brain at 3 AM",
    content: "Brain: Remember that embarrassing thing you did in 2009?\nMe: I was trying to sleep.\nBrain: What if we revisit ALL of them?",
    punchline: "Me: Fine. What's the WiFi password again? 📡",
    language: "English"
  },
  {
    id: "j6",
    type: "joke",
    category: "Marriage",
    emoji: "💍",
    title: "Secret to a happy marriage",
    content: "Wife: What's your secret to our 30 years of happy marriage?\nHusband: Whenever we argue, I go for a walk.",
    punchline: "Wife: That's beautiful. Where do you walk?\nHusband: I have no idea. I've been to 14 countries. 🌍",
    language: "English"
  }]

};
