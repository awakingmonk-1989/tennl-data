"use client";
import React, { useState, useRef, useEffect } from "react";

const agents = [
  {
    id: "stories",
    emoji: "🌙",
    name: "Bedtime Story Agent",
    description: "Creates personalized bedtime stories for your kids every night and sends a notification at 8 PM.",
    status: "active",
    lastRun: "Tonight 8:00 PM",
    bgColor: "bg-purple-50",
    accentColor: "text-xai",
  },
  {
    id: "deals",
    emoji: "💰",
    name: "Deal Hunter Agent",
    description: "Monitors prices across platforms for your wishlist items. Alerts you the moment a deal drops.",
    status: "idle",
    lastRun: "Found 3 deals today",
    bgColor: "bg-amber-50",
    accentColor: "text-amber-600",
  },
  {
    id: "whatsapp",
    emoji: "💬",
    name: "WhatsApp Auto-Reply",
    description: "Reads incoming messages, drafts smart replies based on your tone, sends on approval.",
    status: "active",
    lastRun: "12 replies sent today",
    bgColor: "bg-green-50",
    accentColor: "text-green-600",
  },
  {
    id: "jewellery",
    emoji: "💎",
    name: "Style Finder Agent",
    description: "Curates jewellery and fashion options from your preferences. Places orders on confirmation.",
    status: "idle",
    lastRun: "Ready to activate",
    bgColor: "bg-rose-50",
    accentColor: "text-rose-500",
  },
];

export default function XAISection() {
  const [activeAgents, setActiveAgents] = useState<Set<string>>(new Set(["stories", "whatsapp"]));
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.querySelectorAll(".reveal-on-scroll").forEach((el, i) => {
              setTimeout(() => el.classList.add("revealed"), i * 100);
            });
          }
        });
      },
      { threshold: 0.1 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  const toggleAgent = (id: string) => {
    setActiveAgents((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <section id="xai" ref={sectionRef} className="py-16 lg:py-24 bg-bg-amber">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="reveal-on-scroll mb-12 lg:mb-16 flex flex-col lg:flex-row lg:items-end justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-8 h-1 rounded-full bg-xai block" />
              <span className="section-label text-xai">XAI — AI for Everyone</span>
            </div>
            <h2 className="font-display font-extrabold text-display-md text-fg leading-tight">
              Your personal AI.<br className="hidden sm:block" /> Works 24/7.
            </h2>
          </div>
          <p className="text-fg-muted max-w-sm text-base leading-relaxed">
            Spin up background agents that handle tasks, send messages, find deals, and create content — all while you live your life.
          </p>
        </div>

        {/* Agents grid */}
        <div className="reveal-on-scroll grid grid-cols-1 sm:grid-cols-2 gap-4 lg:gap-5 stagger-children mb-12">
          {agents.map((agent) => {
            const isActive = activeAgents.has(agent.id);
            return (
              <div
                key={agent.id}
                className={`card-warm p-6 lg:p-7 transition-all duration-300 ${isActive ? "border-border-warm shadow-warm-sm" : ""}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-2xl ${agent.bgColor} flex items-center justify-center text-2xl`}>
                      {agent.emoji}
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-base text-fg">{agent.name}</h3>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${isActive ? "bg-green-400" : "bg-gray-300"} ${isActive ? "animate-pulse" : ""}`} />
                        <span className={`text-xs font-medium ${isActive ? "text-green-600" : "text-fg-subtle"}`}>
                          {isActive ? "Active" : "Idle"}
                        </span>
                      </div>
                    </div>
                  </div>
                  {/* Toggle */}
                  <button
                    onClick={() => toggleAgent(agent.id)}
                    className={`agent-toggle ${isActive ? "active" : ""} flex-shrink-0`}
                    aria-label={`Toggle ${agent.name}`}
                  >
                    <div className="agent-toggle-thumb" />
                  </button>
                </div>
                <p className="text-sm text-fg-muted leading-relaxed mb-4">{agent.description}</p>
                <div className={`flex items-center gap-2 ${agent.bgColor} rounded-xl px-3 py-2`}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={agent.accentColor}>
                    <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                  </svg>
                  <span className={`text-xs font-medium ${agent.accentColor}`}>{agent.lastRun}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="reveal-on-scroll bg-white rounded-3xl border border-border p-8 lg:p-10 flex flex-col lg:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-purple-gradient flex items-center justify-center text-3xl text-white flex-shrink-0">
              ⚡
            </div>
            <div>
              <h3 className="font-display font-bold text-xl text-fg mb-1">Create your own agent</h3>
              <p className="text-fg-muted text-sm">Describe any task in plain English. XAI builds and deploys it instantly.</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
            <div className="flex-1 lg:w-72 bg-gray-50 border border-border rounded-xl px-4 py-3 text-sm text-fg-muted font-body">
              Create a morning news digest and...
            </div>
            <button className="bg-purple-gradient text-white px-6 py-3 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all whitespace-nowrap shadow-sm">
              Create Agent
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
