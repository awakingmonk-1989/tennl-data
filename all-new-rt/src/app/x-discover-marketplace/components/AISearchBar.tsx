"use client";
import React, { useState } from "react";

interface AISearchBarProps {
  onSearch: (query: string) => void;
  isSearching: boolean;
}

const suggestions = [
  "2BHK near school with parking under ₹30k Bangalore",
  "Interior designer for home renovation under ₹2L",
  "Remote React developer with 3+ years experience",
  "Dog groomer who does home visits in HSR Layout",
  "Used MacBook Pro under ₹80k",
];

export default function AISearchBar({ onSearch, isSearching }: AISearchBarProps) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);

  const handleSubmit = () => {
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="relative">
      <div
        className={`search-glow bg-white rounded-2xl border-2 transition-all duration-300 ${
          focused ? "border-xdiscover" : "border-border"
        } p-3 flex flex-col sm:flex-row gap-3`}
      >
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center flex-shrink-0">
            {isSearching ? (
              <svg
                className="animate-spin"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#2DD4BF"
                strokeWidth="2"
              >
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" opacity="0.3" />
                <path d="M21 12a9 9 0 00-9-9" />
              </svg>
            ) : (
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#2DD4BF"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
            )}
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="Describe what you need in plain English — AI will find the best matches..."
            className="flex-1 bg-transparent text-fg placeholder-fg-subtle font-body text-base focus:outline-none min-w-0"
          />
        </div>
        <button
          onClick={handleSubmit}
          disabled={isSearching}
          className="bg-teal-gradient text-white px-6 py-3 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all whitespace-nowrap flex items-center justify-center gap-2 disabled:opacity-60"
        >
          {isSearching ? "Searching..." : "AI Search"}
        </button>
      </div>

      {/* Suggestion chips */}
      <div className="mt-3 flex flex-wrap gap-2 items-center">
        <span className="text-xs text-fg-muted font-medium">Try:</span>
        {suggestions.slice(0, 3).map((s) => (
          <button
            key={s}
            onClick={() => {
              setQuery(s);
              onSearch(s);
            }}
            className="text-xs text-xdiscover hover:underline font-medium font-body truncate max-w-[200px]"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
