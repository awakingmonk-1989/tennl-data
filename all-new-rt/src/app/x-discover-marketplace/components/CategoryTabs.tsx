"use client";
import React from "react";
import { CategoryType } from "./listingsData";

interface CategoryTabsProps {
  activeCategory: CategoryType;
  onCategoryChange: (cat: CategoryType) => void;
}

const categories: { id: CategoryType; label: string; emoji: string; count: string }[] = [
  { id: "rentals", label: "Rentals", emoji: "🏠", count: "12.4K" },
  { id: "services", label: "Services", emoji: "🔧", count: "8.1K" },
  { id: "jobs", label: "Jobs", emoji: "💼", count: "5.6K" },
  { id: "freelancers", label: "Freelancers", emoji: "🧑‍💻", count: "3.2K" },
  { id: "buysell", label: "Buy & Sell", emoji: "🛍️", count: "22K" },
];

export default function CategoryTabs({
  activeCategory,
  onCategoryChange,
}: CategoryTabsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onCategoryChange(cat.id)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold font-display text-sm whitespace-nowrap transition-all flex-shrink-0 ${
            activeCategory === cat.id
              ? "bg-teal-gradient text-white shadow-sm"
              : "bg-white border border-border text-fg-muted hover:border-xdiscover hover:text-xdiscover"
          }`}
        >
          <span>{cat.emoji}</span>
          <span>{cat.label}</span>
          <span
            className={`text-xs font-medium ${
              activeCategory === cat.id ? "text-white/70" : "text-fg-subtle"
            }`}
          >
            {cat.count}
          </span>
        </button>
      ))}
    </div>
  );
}
