"use client";
import React from "react";
import AppImage from "@/components/ui/AppImage";
import { FeedItem } from "./feedData";

interface ContentCardProps {
  item: FeedItem;
  isActive?: boolean;
  onInterested?: () => void;
  isInterested?: boolean;
}

export default function ContentCard({ item, isActive, onInterested, isInterested }: ContentCardProps) {
  if (item.type === "joke") {
    return (
      <div className={`joke-canvas p-8 lg:p-12 transition-all duration-500 ${isActive ? "shadow-warm-md" : ""}`}>
        <div className="max-w-2xl mx-auto text-center">
          <div className="text-6xl lg:text-7xl mb-8">{item.emoji || "😄"}</div>
          <span className="tag-pill bg-primary-pale text-primary text-xs mb-6 inline-block">{item.category}</span>
          <h2 className="font-display font-extrabold text-2xl lg:text-4xl text-fg leading-tight mb-6">
            {item.title}
          </h2>
          {item.content && (
            <p className="text-lg lg:text-2xl text-fg-muted leading-relaxed font-body">
              {item.content}
            </p>
          )}
          {item.punchline && (
            <div className="mt-6 bg-white rounded-2xl px-6 py-4 border border-border-warm">
              <p className="text-xl lg:text-2xl font-bold text-primary font-display">{item.punchline}</p>
            </div>
          )}
          <div className="mt-8 flex items-center justify-center gap-4">
            <button className="flex items-center gap-2 bg-white border-2 border-border rounded-2xl px-5 py-3 text-sm font-bold font-display text-fg-muted hover:border-primary hover:text-primary transition-all">
              😂 Hilarious
            </button>
            <button className="flex items-center gap-2 bg-white border-2 border-border rounded-2xl px-5 py-3 text-sm font-bold font-display text-fg-muted hover:border-border hover:text-fg transition-all">
              🤔 Meh
            </button>
            <button className="flex items-center gap-2 bg-white border-2 border-border rounded-2xl px-5 py-3 text-sm font-bold font-display text-fg-muted hover:border-amber-300 hover:text-amber-600 transition-all">
              🔁 Share
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Article card
  return (
    <div className={`article-card bg-white transition-all duration-500 ${isActive ? "shadow-warm-md border-border-warm" : ""}`}>
      {item.image && (
        <div className="relative h-56 lg:h-72 overflow-hidden">
          <AppImage
            src={item.image}
            alt={item.imageAlt || item.title}
            fill
            className="object-cover transition-transform duration-700 hover:scale-105"
            sizes="(max-width: 1024px) 100vw, 800px"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
          <div className="absolute top-4 left-4 flex gap-2">
            <span className="tag-pill bg-white/95 text-fg text-xs">{item.category}</span>
            {item.readTime && (
              <span className="tag-pill bg-primary/90 text-white text-xs">{item.readTime}</span>
            )}
          </div>
        </div>
      )}
      <div className="p-6 lg:p-8">
        <h2 className="font-display font-extrabold text-2xl lg:text-3xl text-fg leading-tight mb-4">
          {item.title}
        </h2>
        {item.content && (
          <div className="prose-sm text-fg-muted leading-relaxed space-y-4 font-body">
            {item.content.split("\n\n").map((para, i) => (
              <p key={i} className="text-base leading-relaxed">{para}</p>
            ))}
          </div>
        )}
        <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary-pale flex items-center justify-center text-sm">🤖</div>
            <div>
              <p className="text-xs font-bold text-fg font-display">XAI Writer</p>
              <p className="text-xs text-fg-subtle">Just now · AI-generated</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2.5 rounded-xl border border-border text-fg-muted hover:text-primary hover:border-border-warm transition-all" aria-label="Like">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
              </svg>
            </button>
            <button className="p-2.5 rounded-xl border border-border text-fg-muted hover:text-fg hover:border-border-warm transition-all" aria-label="Share">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
              </svg>
            </button>
            {!isInterested && onInterested && (
              <button
                onClick={onInterested}
                className="flex items-center gap-1.5 bg-primary-pale border border-border-warm text-primary px-4 py-2.5 rounded-xl font-bold font-display text-sm hover:bg-primary hover:text-white transition-all"
              >
                💛 I&apos;m Interested
              </button>
            )}
            {isInterested && (
              <span className="flex items-center gap-1.5 bg-primary text-white px-4 py-2.5 rounded-xl font-bold font-display text-sm">
                💛 Saved
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
