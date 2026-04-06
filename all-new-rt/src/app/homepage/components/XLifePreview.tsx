'use client';

import React, { useState } from 'react';
import Link from 'next/link';

const previewItems = [
  {
    type: 'article',
    topic: 'Wellness',
    title: 'Why Doing Nothing Is the Most Productive Thing You Can Do',
    excerpt: 'In a culture obsessed with hustle, the science of rest reveals something counterintuitive: our brains consolidate learning, spark creativity, and process emotion during deliberate downtime...',
    readTime: '4 min read',
    timer: 60,
    emoji: '🧘',
  },
  {
    type: 'joke',
    topic: 'Tech Humour',
    content: 'Why did the developer go broke? \n\nBecause they used up all their cache! 😂',
    lang: 'English',
    timer: 30,
    emoji: '😄',
  },
  {
    type: 'article',
    topic: 'Science',
    title: 'The Hidden Language of Trees: How Forests Communicate',
    excerpt: 'Beneath every old-growth forest lies a web of fungal threads connecting trees in a network so sophisticated that scientists call it the "Wood Wide Web"...',
    readTime: '5 min read',
    timer: 60,
    emoji: '🌳',
  },
];

export default function XLifePreview() {
  const [current, setCurrent] = useState(0);

  return (
    <section className="py-12 sm:py-16 bg-surface-warm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2.5 h-2.5 rounded-full bg-xlife" />
              <span className="text-sm font-semibold text-xlife uppercase tracking-wider">XLife Feed</span>
            </div>
            <h2 className="font-display text-2xl sm:text-3xl font-semibold text-fg">
              Stories and laughs,{' '}
              <span className="italic text-primary">delivered fresh</span>
            </h2>
          </div>
          <Link href="/x-life-feed" className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline underline-offset-2 shrink-0">
            Open Full Feed
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </Link>
        </div>

        {/* Preview card */}
        <div className="relative max-w-2xl mx-auto">
          {previewItems?.map((item, i) => (
            <div
              key={i}
              className={`transition-all duration-500 ${i === current ? 'block' : 'hidden'}`}
            >
              {item?.type === 'article' ? (
                <div className="card-warm p-6 sm:p-8">
                  <div className="flex items-center justify-between mb-4">
                    <span className="pill bg-primary-pale text-primary border border-primary/20">{item?.topic}</span>
                    <div className="flex items-center gap-2">
                      {/* Mini circle timer */}
                      <svg width="36" height="36" viewBox="0 0 36 36" className="shrink-0">
                        <circle cx="18" cy="18" r="15" fill="none" stroke="#F0EBE3" strokeWidth="3"/>
                        <circle cx="18" cy="18" r="15" fill="none" stroke="#FF6B35" strokeWidth="3"
                          strokeDasharray="94.2"
                          strokeDashoffset="30"
                          strokeLinecap="round"
                          style={{ transform: 'rotate(-90deg)', transformOrigin: '18px 18px' }}
                        />
                        <text x="18" y="22" textAnchor="middle" fill="#FF6B35" fontSize="9" fontWeight="600">60s</text>
                      </svg>
                      <span className="text-xs text-fg-muted">{item?.readTime}</span>
                    </div>
                  </div>
                  <div className="text-3xl mb-3">{item?.emoji}</div>
                  <h3 className="font-display text-xl font-semibold text-fg mb-3 leading-snug">{item?.title}</h3>
                  <p className="text-sm text-fg-secondary leading-relaxed">{item?.excerpt}</p>
                  <div className="mt-5 flex items-center gap-3">
                    <button className="btn-primary px-5 py-2.5 text-sm inline-flex items-center gap-1.5">
                      ❤️ I&apos;m Interested
                    </button>
                    <button className="btn-secondary px-4 py-2.5 text-sm" onClick={() => setCurrent((current + 1) % previewItems?.length)}>
                      Skip →
                    </button>
                  </div>
                </div>
              ) : (
                <div className="joke-canvas p-8 sm:p-12 text-center">
                  <div className="text-4xl mb-4">{item?.emoji}</div>
                  <span className="pill bg-accent-pale text-amber-700 border border-accent/30 mb-6 inline-block">{item?.topic}</span>
                  <p className="font-display text-xl sm:text-2xl font-medium text-fg leading-relaxed whitespace-pre-line">{item?.content}</p>
                  <div className="mt-6 flex items-center justify-center gap-3">
                    <button className="btn-primary px-5 py-2.5 text-sm inline-flex items-center gap-1.5">
                      😂 That&apos;s Funny!
                    </button>
                    <button className="btn-secondary px-4 py-2.5 text-sm" onClick={() => setCurrent((current + 1) % previewItems?.length)}>
                      Next →
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Dots */}
          <div className="flex items-center justify-center gap-2 mt-5">
            {previewItems?.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrent(i)}
                className={`rounded-full transition-all duration-200 ${i === current ? 'w-6 h-2 bg-primary' : 'w-2 h-2 bg-border hover:bg-fg-muted'}`}
                aria-label={`Go to item ${i + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
