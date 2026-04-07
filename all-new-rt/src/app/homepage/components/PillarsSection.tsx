'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';

const pillars = [
  {
    id: 'xlife',
    name: 'XLife',
    tagline: 'Content that makes you feel something',
    description: 'AI-crafted articles and jokes delivered in a warm, timer-driven feed. Laugh. Learn. Be surprised.',
    gradient: 'xlife-gradient',
    bgPale: 'bg-primary-pale',
    textColor: 'text-xlife',
    borderColor: 'border-primary/20',
    href: '/x-life-feed',
    cta: 'Open XLife',
    emoji: '✨',
    stats: ['300–500 word articles', '30-sec jokes', 'Multi-language'],
    colSpan: 'md:col-span-2',
  },
  {
    id: 'xdiscover',
    name: 'XDiscover',
    tagline: 'A marketplace that understands you',
    description: 'Say what you need in plain language. AI matches, connects, and negotiates across properties, jobs, freelancers, and more.',
    gradient: 'xdiscover-gradient',
    bgPale: 'bg-xdiscover-pale',
    textColor: 'text-xdiscover',
    borderColor: 'border-xdiscover/20',
    href: '/x-discover-marketplace',
    cta: 'Explore Marketplace',
    emoji: '🔍',
    stats: ['Natural language search', 'AI match intent', 'Bulk outreach'],
    colSpan: 'md:col-span-2',
  },
  {
    id: 'xai',
    name: 'XAI',
    tagline: 'AI agents that work 24/7 for you',
    description: 'Create bedtime stories, track deals, monitor listings, handle messages — just describe the task, AI handles the rest.',
    gradient: 'xai-gradient',
    bgPale: 'bg-xai-pale',
    textColor: 'text-xai',
    borderColor: 'border-xai/20',
    href: '/homepage#xai',
    cta: 'Meet XAI',
    emoji: '🤖',
    stats: ['Background agents', 'WhatsApp integration', 'Push notifications'],
    colSpan: 'md:col-span-4',
  },
];

export default function PillarsSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const cards = entry.target.querySelectorAll('.pillar-card');
            cards.forEach((card, i) => {
              setTimeout(() => {
                card.classList.add('reveal-animate');
              }, i * 150);
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
    <section ref={sectionRef} className="py-16 sm:py-20 px-4 sm:px-6 max-w-6xl mx-auto" id="pillars">
      <div className="text-center mb-12">
        <h2 className="font-display text-3xl sm:text-4xl font-semibold text-fg mb-3">
          Three pillars,{' '}
          <span className="italic text-primary">one platform</span>
        </h2>
        <p className="text-base text-fg-secondary max-w-xl mx-auto">
          Each section is designed to bring joy, utility, and intelligence into your everyday moments.
        </p>
      </div>
      {/* Bento grid — 4-col */}
      {/* Row 1: XLife col-span-2 + XDiscover col-span-2 = 4/4 ✓ */}
      {/* Row 2: XAI col-span-4 = 4/4 ✓ */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {pillars?.map((pillar) => (
          <div
            key={pillar?.id}
            className={`pillar-card reveal ${pillar?.colSpan} card-warm group overflow-hidden`}
          >
            <div className={`p-6 sm:p-8 h-full flex flex-col ${pillar?.id === 'xai' ? 'sm:flex-row sm:items-center sm:gap-8' : ''}`}>
              <div className={pillar?.id === 'xai' ? 'flex-1' : ''}>
                <div className="flex items-center gap-3 mb-4">
                  <span className={`text-2xl`}>{pillar?.emoji}</span>
                  <span className={`font-display text-xl font-semibold ${pillar?.textColor}`}>{pillar?.name}</span>
                </div>
                <h3 className="text-lg font-semibold text-fg mb-2 leading-snug">{pillar?.tagline}</h3>
                <p className="text-sm text-fg-secondary leading-relaxed mb-5">{pillar?.description}</p>

                <div className="flex flex-wrap gap-2 mb-6">
                  {pillar?.stats?.map((stat) => (
                    <span key={stat} className={`pill ${pillar?.bgPale} ${pillar?.textColor} border ${pillar?.borderColor} text-xs`}>
                      {stat}
                    </span>
                  ))}
                </div>
              </div>

              <div className={pillar?.id === 'xai' ? 'sm:shrink-0' : ''}>
                <Link
                  href={pillar?.href}
                  className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold text-white ${pillar?.gradient} shadow-warm transition-all duration-200 hover:shadow-warm-lg hover:-translate-y-0.5`}
                >
                  {pillar?.cta}
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
