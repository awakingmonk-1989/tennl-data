"use client";
import React, { useEffect, useRef } from "react";
import Link from "next/link";

// Bento Grid Audit (3-col):
// Row 1: [XLife col-span-2] + [XAI col-span-1] = 3/3 ✓
// Row 2: [XDiscover col-span-1] + [Stats col-span-2] = 3/3 ✓

const features = [
  {
    id: "xlife",
    label: "XLife",
    emoji: "📖",
    headline: "Content that refreshes, not stresses.",
    body: "AI-curated articles (300–500 words) and jokes across languages. A circle timer auto-advances your feed — pause anytime with 'I'm Interested.'",
    color: "text-xlife",
    bgColor: "bg-primary-pale",
    borderColor: "border-border-warm",
    gradientClass: "bg-coral-gradient",
    href: "/x-life-feed",
    colSpan: "lg:col-span-2",
    pills: ["Articles", "Jokes", "60s Timer", "Multilingual"],
  },
  {
    id: "xai",
    label: "XAI",
    emoji: "🤖",
    headline: "Agents that work while you sleep.",
    body: "Spin up AI agents for anything — bedtime stories, deal alerts, order placements. 24/7 automation on your terms.",
    color: "text-xai",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-100",
    gradientClass: "bg-purple-gradient",
    href: "/homepage#xai",
    colSpan: "lg:col-span-1",
    pills: ["24/7 Agents", "Notifications"],
  },
];

export default function FeaturesTrioSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const els = entry.target.querySelectorAll(".reveal-on-scroll");
            els.forEach((el, i) => {
              setTimeout(() => el.classList.add("revealed"), i * 100);
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
    <section ref={sectionRef} className="py-20 lg:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="reveal-on-scroll mb-12 lg:mb-16 flex flex-col sm:flex-row sm:items-end justify-between gap-6">
          <div>
            <span className="section-label text-fg-subtle mb-3 block">Three pillars</span>
            <h2 className="font-display font-extrabold text-display-md text-fg leading-tight">
              Everything you need,<br className="hidden sm:block" /> nothing you don't.
            </h2>
          </div>
          <p className="text-fg-muted max-w-sm text-base leading-relaxed">
            XPlatform is built around three focused experiences — each powered by AI, each designed to feel warm and effortless.
          </p>
        </div>

        {/* Bento grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-5">
          {/* XLife — col-span-2 */}
          <div className={`reveal-on-scroll card-warm p-8 lg:p-10 ${features?.[0]?.colSpan} flex flex-col justify-between min-h-64 lg:min-h-72 group`}>
            <div>
              <div className="flex items-center gap-3 mb-5">
                <div className={`w-12 h-12 rounded-2xl ${features?.[0]?.bgColor} flex items-center justify-center text-2xl`}>
                  {features?.[0]?.emoji}
                </div>
                <span className={`font-display font-extrabold text-xl ${features?.[0]?.color}`}>{features?.[0]?.label}</span>
              </div>
              <h3 className="font-display font-bold text-2xl lg:text-3xl text-fg mb-3 leading-tight">{features?.[0]?.headline}</h3>
              <p className="text-fg-muted text-base leading-relaxed">{features?.[0]?.body}</p>
            </div>
            <div className="mt-6 flex flex-wrap gap-2 items-center justify-between">
              <div className="flex flex-wrap gap-2">
                {features?.[0]?.pills?.map((pill) => (
                  <span key={pill} className={`tag-pill ${features?.[0]?.bgColor} ${features?.[0]?.color}`}>{pill}</span>
                ))}
              </div>
              <Link href={features?.[0]?.href} className={`inline-flex items-center gap-1.5 ${features?.[0]?.gradientClass} text-white px-5 py-2.5 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all shadow-warm-sm hover:-translate-y-0.5`}>
                Explore <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </Link>
            </div>
          </div>

          {/* XAI — col-span-1 */}
          <div className={`reveal-on-scroll card-warm p-8 ${features?.[1]?.colSpan} flex flex-col justify-between min-h-64 group relative overflow-hidden`}>
            <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-10 bg-purple-gradient" />
            <div>
              <div className="flex items-center gap-3 mb-5">
                <div className={`w-12 h-12 rounded-2xl ${features?.[1]?.bgColor} flex items-center justify-center text-2xl`}>
                  {features?.[1]?.emoji}
                </div>
                <span className={`font-display font-extrabold text-xl ${features?.[1]?.color}`}>{features?.[1]?.label}</span>
              </div>
              <h3 className="font-display font-bold text-xl text-fg mb-3 leading-tight">{features?.[1]?.headline}</h3>
              <p className="text-fg-muted text-sm leading-relaxed">{features?.[1]?.body}</p>
            </div>
            <div className="mt-5">
              <div className="flex items-center gap-3 bg-purple-50 rounded-xl p-3">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse flex-shrink-0" />
                <span className="text-xs font-medium text-fg-muted">1 agent running · Last update 2m ago</span>
              </div>
            </div>
          </div>

          {/* XDiscover — col-span-1 */}
          <div className="reveal-on-scroll card-warm p-8 lg:col-span-1 flex flex-col justify-between min-h-56 group relative overflow-hidden">
            <div className="absolute -bottom-8 -right-8 w-32 h-32 rounded-full opacity-10 bg-teal-gradient" />
            <div>
              <div className="flex items-center gap-3 mb-5">
                <div className="w-12 h-12 rounded-2xl bg-teal-50 flex items-center justify-center text-2xl">🔍</div>
                <span className="font-display font-extrabold text-xl text-xdiscover">XDiscover</span>
              </div>
              <h3 className="font-display font-bold text-xl text-fg mb-3 leading-tight">Find anything, in plain English.</h3>
              <p className="text-fg-muted text-sm leading-relaxed">AI searches across rentals, services, jobs, and freelancers — then connects you to multiple providers at once.</p>
            </div>
            <Link href="/x-discover-marketplace" className="mt-5 inline-flex items-center gap-1.5 bg-teal-gradient text-white px-5 py-2.5 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all shadow-sm hover:-translate-y-0.5 self-start">
              Discover <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
            </Link>
          </div>

          {/* Stats card — col-span-2 */}
          <div className="reveal-on-scroll lg:col-span-2 bg-coral-gradient rounded-2xl p-8 lg:p-10 text-white flex flex-col sm:flex-row gap-8 items-center justify-between">
            <div>
              <p className="font-display font-extrabold text-5xl lg:text-6xl leading-none">2.4M+</p>
              <p className="mt-2 text-white/80 font-medium">Content pieces served this month</p>
            </div>
            <div className="w-px h-16 bg-white/20 hidden sm:block" />
            <div>
              <p className="font-display font-extrabold text-5xl lg:text-6xl leading-none">340K</p>
              <p className="mt-2 text-white/80 font-medium">Active marketplace listings</p>
            </div>
            <div className="w-px h-16 bg-white/20 hidden sm:block" />
            <div>
              <p className="font-display font-extrabold text-5xl lg:text-6xl leading-none">98%</p>
              <p className="mt-2 text-white/80 font-medium">AI match accuracy</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
