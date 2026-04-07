"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import ContentCard from "./ContentCard";
import CircleTimer from "./CircleTimer";
import { feedData, FeedItem } from "./feedData";

type TabType = "articles" | "jokes";

export default function XLifeFeedClient() {
  const [activeTab, setActiveTab] = useState<TabType>("articles");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [timeLeft, setTimeLeft] = useState(60);
  const [isInterested, setIsInterested] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const items: FeedItem[] = feedData[activeTab];
  const duration = activeTab === "articles" ? 60 : 30;

  const goToNext = useCallback(() => {
    const next = (currentIndex + 1) % items.length;
    setCurrentIndex(next);
    setTimeLeft(duration);
    setIsInterested(false);
    setIsPaused(false);
    if (scrollRef.current) {
      const cards = scrollRef.current.querySelectorAll<HTMLElement>(".feed-snap-card");
      if (cards[next]) {
        cards[next].scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" });
      }
    }
  }, [currentIndex, items.length, duration]);

  const goToPrev = useCallback(() => {
    const prev = (currentIndex - 1 + items.length) % items.length;
    setCurrentIndex(prev);
    setTimeLeft(duration);
    setIsInterested(false);
    setIsPaused(false);
  }, [currentIndex, items.length, duration]);

  // Timer
  useEffect(() => {
    setTimeLeft(duration);
    setIsInterested(false);
    setIsPaused(false);
  }, [activeTab, duration]);

  useEffect(() => {
    if (isPaused || isInterested) return;
    if (timeLeft <= 0) {
      goToNext();
      return;
    }
    const interval = setInterval(() => {
      setTimeLeft((t) => t - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timeLeft, isPaused, isInterested, goToNext]);

  const handleInterested = () => {
    setIsInterested(true);
    setIsPaused(true);
  };

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    setCurrentIndex(0);
    setIsInterested(false);
    setIsPaused(false);
  };

  const currentItem = items[currentIndex];

  return (
    <div className="pt-20 min-h-screen">
      {/* Page header */}
      <div className="bg-bg-warm border-b border-border py-8 lg:py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="w-6 h-1 rounded-full bg-primary block" />
                <span className="section-label text-primary">XLife</span>
              </div>
              <h1 className="font-display font-extrabold text-3xl lg:text-4xl text-fg tracking-tight">
                Your Daily Feed
              </h1>
              <p className="text-fg-muted text-sm mt-1">AI-curated content. Refreshed every hour.</p>
            </div>

            {/* Tab switcher */}
            <div className="flex bg-white border border-border rounded-2xl p-1 gap-1 self-start sm:self-auto">
              <button
                onClick={() => handleTabChange("articles")}
                className={`px-5 py-2.5 rounded-xl font-display font-bold text-sm transition-all ${
                  activeTab === "articles" ?"bg-coral-gradient text-white shadow-warm-sm" :"text-fg-muted hover:text-fg"
                }`}
              >
                📖 Articles
              </button>
              <button
                onClick={() => handleTabChange("jokes")}
                className={`px-5 py-2.5 rounded-xl font-display font-bold text-sm transition-all ${
                  activeTab === "jokes" ?"bg-coral-gradient text-white shadow-warm-sm" :"text-fg-muted hover:text-fg"
                }`}
              >
                😄 Jokes
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main feed area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 items-start">
          {/* Main content */}
          <div className="flex-1 min-w-0">
            {/* Timer bar + controls */}
            <div className="flex items-center justify-between mb-6 bg-white rounded-2xl px-5 py-4 border border-border shadow-card">
              <div className="flex items-center gap-4">
                <CircleTimer
                  duration={duration}
                  timeLeft={timeLeft}
                  isPaused={isPaused || isInterested}
                />
                <div>
                  <p className="font-display font-bold text-sm text-fg">
                    {isPaused || isInterested ? "Paused" : `Next in ${timeLeft}s`}
                  </p>
                  <p className="text-xs text-fg-muted">
                    {currentIndex + 1} of {items.length} · {activeTab === "articles" ? "Articles" : "Jokes"}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {!isInterested && !isPaused && (
                  <button
                    onClick={handleInterested}
                    className="flex items-center gap-2 bg-primary-pale border-2 border-primary text-primary px-4 py-2.5 rounded-xl font-bold font-display text-sm hover:bg-primary hover:text-white transition-all group"
                  >
                    <span className="text-base group-hover:scale-110 transition-transform">💛</span>
                    <span className="hidden sm:block">I&apos;m Interested</span>
                  </button>
                )}
                {(isPaused || isInterested) && (
                  <button
                    onClick={() => { setIsPaused(false); setIsInterested(false); setTimeLeft(duration); }}
                    className="flex items-center gap-2 bg-white border-2 border-border text-fg-muted px-4 py-2.5 rounded-xl font-bold font-display text-sm hover:border-fg hover:text-fg transition-all"
                  >
                    ▶ Resume
                  </button>
                )}
                <button onClick={goToPrev} className="p-2.5 rounded-xl border border-border text-fg-muted hover:text-fg hover:border-fg transition-all" aria-label="Previous">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M15 18l-6-6 6-6" /></svg>
                </button>
                <button onClick={goToNext} className="p-2.5 rounded-xl bg-coral-gradient text-white hover:opacity-90 transition-all" aria-label="Next">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 18l6-6-6-6" /></svg>
                </button>
              </div>
            </div>

            {/* Active card */}
            {currentItem && (
              <ContentCard
                item={currentItem}
                isActive
                onInterested={handleInterested}
                isInterested={isInterested}
              />
            )}

            {/* Horizontal scroll strip */}
            <div className="mt-8">
              <p className="text-xs font-bold text-fg-muted uppercase tracking-widest mb-4 font-display">Up next</p>
              <div ref={scrollRef} className="feed-scroll-container">
                {items.map((item, i) => (
                  <button
                    key={item.id}
                    onClick={() => { setCurrentIndex(i); setTimeLeft(duration); setIsInterested(false); setIsPaused(false); }}
                    className={`feed-snap-card feed-card-snap flex-shrink-0 w-44 text-left rounded-2xl border-2 overflow-hidden transition-all duration-200 ${
                      i === currentIndex ? "border-primary shadow-warm-sm" : "border-border bg-white hover:border-border-warm"
                    }`}
                  >
                    <div className="p-4">
                      {item.type === "joke" ? (
                        <div className="text-2xl mb-2">{item.emoji || "😄"}</div>
                      ) : null}
                      <p className={`font-display font-bold text-xs text-fg leading-tight line-clamp-3 ${item.type === "joke" ? "text-center" : ""}`}>
                        {item.title}
                      </p>
                      <div className="mt-2 flex items-center gap-1">
                        <span className={`w-1.5 h-1.5 rounded-full ${i === currentIndex ? "bg-primary" : "bg-gray-300"}`} />
                        <span className="text-xs text-fg-subtle">{item.category}</span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="w-full lg:w-72 flex-shrink-0 space-y-4">
            {/* Progress card */}
            <div className="bg-white rounded-2xl border border-border p-5 shadow-card">
              <p className="font-display font-bold text-sm text-fg mb-4">Today&apos;s reading</p>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs text-fg-muted mb-1.5">
                    <span>Articles read</span>
                    <span className="font-bold text-fg">4 / 10</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-coral-gradient rounded-full" style={{ width: "40%" }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs text-fg-muted mb-1.5">
                    <span>Jokes enjoyed</span>
                    <span className="font-bold text-fg">7 / 10</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-gradient rounded-full" style={{ width: "70%", background: "linear-gradient(90deg, #FFB347, #FF6B35)" }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Category filter */}
            <div className="bg-white rounded-2xl border border-border p-5 shadow-card">
              <p className="font-display font-bold text-sm text-fg mb-4">Categories</p>
              <div className="flex flex-wrap gap-2">
                {["All", "Tech", "Mindfulness", "Humor", "Science", "Life", "Finance"].map((cat) => (
                  <button
                    key={cat}
                    className={`tag-pill transition-all text-xs ${
                      cat === "All" ?"bg-primary text-white" :"bg-gray-50 text-fg-muted hover:bg-primary-pale hover:text-primary"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Mood tip */}
            <div className="bg-primary-pale rounded-2xl border border-border-warm p-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">☀️</span>
                <p className="font-display font-bold text-sm text-primary">Good morning!</p>
              </div>
              <p className="text-xs text-fg-muted leading-relaxed">
                You&apos;ve been on a 5-day reading streak. Keep it up — your personalized feed gets better every day.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
