"use client";
import React, { useState, useRef, useEffect } from "react";
import AISearchBar from "./AISearchBar";
import CategoryTabs from "./CategoryTabs";
import ListingGrid from "./ListingGrid";
import AgentPanel from "./AgentPanel";
import { listingsData, CategoryType } from "./listingsData";

export default function XDiscoverClient() {
  const [activeCategory, setActiveCategory] = useState<CategoryType>("rentals");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [aiQuery, setAiQuery] = useState("");
  const [showAgentPanel, setShowAgentPanel] = useState(false);
  const [connectedListings, setConnectedListings] = useState<Set<string>>(new Set());
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.querySelectorAll(".reveal-on-scroll").forEach((el, i) => {
              setTimeout(() => el.classList.add("revealed"), i * 80);
            });
          }
        });
      },
      { threshold: 0.05 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  const handleAISearch = (query: string) => {
    setAiQuery(query);
    setIsSearching(true);
    setTimeout(() => setIsSearching(false), 1500);
  };

  const handleConnect = (id: string) => {
    setConnectedListings((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  };

  const filteredListings = listingsData[activeCategory] || [];
  const displayListings = searchQuery
    ? filteredListings.filter(
        (l) =>
          l.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          l.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
          l.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : filteredListings;

  return (
    <div ref={sectionRef} className="pt-20 min-h-screen">
      {/* Page header */}
      <div className="bg-bg-warm border-b border-border py-8 lg:py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="w-6 h-1 rounded-full bg-xdiscover block" />
                <span className="section-label text-xdiscover">XDiscover</span>
              </div>
              <h1 className="font-display font-extrabold text-3xl lg:text-4xl text-fg tracking-tight">
                Find anything. Instantly.
              </h1>
              <p className="text-fg-muted text-sm mt-1">AI-powered search across rentals, services, jobs, freelancers and more.</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowAgentPanel(!showAgentPanel)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold font-display text-sm border-2 transition-all ${
                  showAgentPanel
                    ? "bg-primary text-white border-primary" :"border-border text-fg-muted hover:border-primary hover:text-primary"
                }`}
              >
                <span>⚡</span>
                <span>Background Agent</span>
                {showAgentPanel && <span className="w-2 h-2 rounded-full bg-green-300 animate-pulse" />}
              </button>
            </div>
          </div>

          {/* AI Search */}
          <AISearchBar onSearch={handleAISearch} isSearching={isSearching} />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
        {/* Agent panel */}
        {showAgentPanel && (
          <div className="reveal-on-scroll mb-6">
            <AgentPanel />
          </div>
        )}

        {/* AI response */}
        {aiQuery && (
          <div className="reveal-on-scroll mb-6 bg-teal-50 border border-teal-200 rounded-2xl p-4 lg:p-5 flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-teal-gradient flex items-center justify-center text-white text-lg flex-shrink-0">🤖</div>
            <div>
              <p className="font-display font-bold text-sm text-teal-800 mb-1">XAI found results for:</p>
              <p className="text-teal-700 text-sm font-body">&ldquo;{aiQuery}&rdquo;</p>
              <p className="text-xs text-teal-600 mt-1">Showing {displayListings.length} results · Ranked by relevance · AI confidence: 94%</p>
            </div>
          </div>
        )}

        {/* Category tabs */}
        <CategoryTabs activeCategory={activeCategory} onCategoryChange={setActiveCategory} />

        {/* Listings */}
        <div className="mt-6">
          <ListingGrid
            listings={displayListings}
            isLoading={isSearching}
            onConnect={handleConnect}
            connectedListings={connectedListings}
          />
        </div>
      </div>
    </div>
  );
}
