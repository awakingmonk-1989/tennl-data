"use client";
import React, { useState } from "react";

interface Agent {
  id: string;
  name: string;
  description: string;
  emoji: string;
  isActive: boolean;
  lastAction: string;
}

export default function AgentPanel() {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: "rental-scout",
      name: "Rental Scout",
      description: "Monitors new listings matching your criteria 24/7. Alerts you the moment a match appears.",
      emoji: "🏠",
      isActive: true,
      lastAction: "Found 2 new matches 30 min ago",
    },
    {
      id: "bulk-connect",
      name: "Bulk Connect Agent",
      description: "Sends personalized expressions of interest to up to 20 providers simultaneously.",
      emoji: "📤",
      isActive: false,
      lastAction: "Ready to activate",
    },
    {
      id: "chat-summarizer",
      name: "Chat Summarizer",
      description: "Reads all incoming responses, summarizes key points, and surfaces the best options.",
      emoji: "💬",
      isActive: true,
      lastAction: "Summarized 8 responses today",
    },
  ]);

  const [taskInput, setTaskInput] = useState("");

  const toggleAgent = (id: string) => {
    setAgents((prev) =>
      prev.map((a) => (a.id === id ? { ...a, isActive: !a.isActive } : a))
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-border p-5 lg:p-6 shadow-card">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-gradient flex items-center justify-center text-white text-lg">
            ⚡
          </div>
          <div>
            <h3 className="font-display font-bold text-base text-fg">Background Agents</h3>
            <p className="text-xs text-fg-muted">Working 24/7 on your behalf</p>
          </div>
        </div>
        <span className="tag-pill bg-green-50 text-green-600 text-xs">
          {agents.filter((a) => a.isActive).length} active
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`rounded-xl p-4 border-2 transition-all ${
              agent.isActive
                ? "border-primary-pale bg-primary-pale" :"border-border bg-gray-50"
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">{agent.emoji}</span>
                <p className="font-display font-bold text-xs text-fg leading-tight">
                  {agent.name}
                </p>
              </div>
              <button
                onClick={() => toggleAgent(agent.id)}
                className={`agent-toggle flex-shrink-0 ${agent.isActive ? "active" : ""}`}
                aria-label={`Toggle ${agent.name}`}
              >
                <div className="agent-toggle-thumb" />
              </button>
            </div>
            <p className="text-xs text-fg-muted leading-relaxed mb-2">
              {agent.description}
            </p>
            <div className="flex items-center gap-1.5">
              <div
                className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                  agent.isActive ? "bg-green-400 animate-pulse" : "bg-gray-300"
                }`}
              />
              <span className="text-xs text-fg-subtle">{agent.lastAction}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Custom agent input */}
      <div className="bg-gray-50 rounded-xl p-4 border border-border">
        <p className="text-xs font-bold text-fg-muted mb-2 font-display uppercase tracking-wider">
          Create custom agent
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            placeholder="e.g. Alert me when a 3BHK under ₹40k appears near Whitefield..."
            className="flex-1 bg-white border border-border rounded-xl px-4 py-2.5 text-sm text-fg placeholder-fg-subtle focus:outline-none focus:border-xdiscover font-body"
          />
          <button
            onClick={() => setTaskInput("")}
            className="bg-teal-gradient text-white px-4 py-2.5 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all whitespace-nowrap"
          >
            Deploy
          </button>
        </div>
      </div>
    </div>
  );
}
