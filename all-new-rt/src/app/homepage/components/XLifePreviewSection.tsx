"use client";
import React, { useRef, useEffect } from "react";
import Link from "next/link";
import AppImage from "@/components/ui/AppImage";

const previewArticles = [
{
  id: 1,
  category: "Mindfulness",
  title: "The 5-minute reset that changes everything",
  excerpt: "Science confirms that micro-breaks of under 5 minutes can reduce cortisol by up to 23%. Here\'s the exact sequence used by neuroscientists...",
  readTime: "4 min",
  image: "https://images.unsplash.com/photo-1631950958451-c779ef54e725",
  imageAlt: "Peaceful mountain sunrise with golden light over calm misty valley",
  emoji: "🧘"
},
{
  id: 2,
  category: "Tech",
  title: "Why your phone knows you better than your best friend",
  excerpt: "Modern AI systems process over 2,000 behavioral signals per hour to build your digital twin. The implications are fascinating — and slightly unsettling...",
  readTime: "5 min",
  image: "https://images.unsplash.com/photo-1636462060335-a0e53fcba38f",
  imageAlt: "Bright clean smartphone on white surface with soft natural light",
  emoji: "📱"
},
{
  id: 3,
  category: "Humor",
  title: "Why do programmers prefer dark mode?",
  excerpt: "Because light attracts bugs. 🐛 Told my wife I was debugging my life. She said she'd been doing that for years and still found no solution...",
  readTime: "1 min",
  image: "https://images.unsplash.com/photo-1692713209659-ff77c6eb995b",
  imageAlt: "Bright cozy desk setup with warm lamp light and coffee mug",
  emoji: "😄",
  isJoke: true
}];


export default function XLifePreviewSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.querySelectorAll(".reveal-on-scroll").forEach((el, i) => {
              setTimeout(() => el.classList.add("revealed"), i * 120);
            });
          }
        });
      },
      { threshold: 0.1 }
    );
    if (sectionRef?.current) observer?.observe(sectionRef?.current);
    return () => observer?.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="py-16 lg:py-24 bg-bg-warm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="reveal-on-scroll flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-8 h-1 rounded-full bg-primary block" />
              <span className="section-label text-primary">XLife</span>
            </div>
            <h2 className="font-display font-extrabold text-display-md text-fg leading-tight">
              Content that moves<br className="hidden sm:block" /> with your mood.
            </h2>
          </div>
          <div className="flex items-center gap-4">
            {/* Timer demo */}
            <div className="flex items-center gap-3 bg-white rounded-2xl px-5 py-3 shadow-card border border-border-warm">
              <div className="circle-timer relative">
                <svg width="36" height="36" viewBox="0 0 36 36">
                  <circle className="circle-timer-track" cx="18" cy="18" r="14" />
                  <circle
                    className="circle-timer-progress"
                    cx="18" cy="18" r="14"
                    strokeDasharray="87.96"
                    strokeDashoffset="30"
                    style={{ transform: "rotate(-90deg)", transformOrigin: "50% 50%" }} />
                  
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-primary">60</span>
              </div>
              <div>
                <p className="text-xs font-bold text-fg font-display">Auto-advance</p>
                <p className="text-xs text-fg-muted">Articles: 60s · Jokes: 30s</p>
              </div>
            </div>
          </div>
        </div>

        {/* Horizontal scroll preview */}
        <div className="reveal-on-scroll feed-scroll-container stagger-children pb-4">
          {previewArticles?.map((article) =>
          <div
            key={article?.id}
            className={`feed-card-snap ${article?.isJoke ? "joke-canvas" : "article-card bg-white"} w-[300px] sm:w-[340px] lg:w-[380px] flex-shrink-0 overflow-hidden`}>
            
              {!article?.isJoke &&
            <div className="relative h-44 overflow-hidden">
                  <AppImage
                src={article?.image}
                alt={article?.imageAlt}
                fill
                className="object-cover transition-transform duration-700 hover:scale-105"
                sizes="380px" />
              
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                  <span className="absolute top-3 left-3 tag-pill bg-white/90 text-fg text-xs">{article?.category}</span>
                </div>
            }
              <div className={`p-6 ${article?.isJoke ? "flex flex-col items-center text-center min-h-64 justify-center" : ""}`}>
                {article?.isJoke &&
              <div className="text-5xl mb-5">{article?.emoji}</div>
              }
                <h3 className={`font-display font-bold text-fg leading-tight mb-3 ${article?.isJoke ? "text-2xl" : "text-lg"}`}>
                  {article?.title}
                </h3>
                <p className={`text-fg-muted leading-relaxed ${article?.isJoke ? "text-lg" : "text-sm"}`}>
                  {article?.excerpt}
                </p>
                {!article?.isJoke &&
              <div className="mt-4 flex items-center justify-between">
                    <span className="text-xs text-fg-subtle font-medium">{article?.readTime} read</span>
                    <button className="text-xs font-bold text-primary hover:underline font-display">I&apos;m Interested →</button>
                  </div>
              }
              </div>
            </div>
          )}
          {/* CTA card */}
          <div className="feed-card-snap w-[260px] flex-shrink-0 bg-coral-gradient rounded-2xl p-8 flex flex-col justify-center items-center text-center text-white">
            <span className="text-4xl mb-4">✨</span>
            <p className="font-display font-bold text-xl mb-2">100+ new articles daily</p>
            <p className="text-white/80 text-sm mb-6">Personalized just for you</p>
            <Link href="/x-life-feed" className="bg-white text-primary font-bold font-display text-sm px-5 py-2.5 rounded-xl hover:bg-primary-pale transition-colors">
              Open XLife
            </Link>
          </div>
        </div>

        <p className="reveal-on-scroll mt-4 text-xs text-fg-subtle text-center">← Swipe to preview more content</p>
      </div>
    </section>);

}
