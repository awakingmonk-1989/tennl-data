'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

const stats = [
  { value: '2.4M+', label: 'Content pieces served', emoji: '📖' },
  { value: '180K+', label: 'Marketplace matches made', emoji: '🤝' },
  { value: '42K+', label: 'AI agents created', emoji: '🤖' },
  { value: '4.8★', label: 'Average user rating', emoji: '⭐' },
];

const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'Product Designer, Bengaluru',
    quote: 'XLife is my 8am ritual now. The jokes in Kannada are hilarious and the articles are actually worth reading.',
    avatar: '👩‍💻',
  },
  {
    name: 'Rohan Mehta',
    role: 'Startup Founder, Mumbai',
    quote: 'Found my office space through XDiscover in 3 days. I just typed what I needed and the AI handled the entire search.',
    avatar: '👨‍💼',
  },
  {
    name: 'Ananya Krishnan',
    role: 'Teacher, Chennai',
    quote: 'I set up an XAI agent to create bedtime stories for my kids every evening. They love it and it saves me so much time.',
    avatar: '👩‍🏫',
  },
];

export default function StatsSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) setVisible(true);
      },
      { threshold: 0.15 }
    );
    if (sectionRef?.current) observer?.observe(sectionRef?.current);
    return () => observer?.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="py-12 sm:py-16 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
          {stats?.map((stat, i) => (
            <div
              key={i}
              className={`card-warm p-5 text-center transition-all duration-500 ${visible ? 'reveal-animate' : 'opacity-100'}`}
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="text-2xl mb-2">{stat?.emoji}</div>
              <div className="font-display text-2xl sm:text-3xl font-semibold text-fg mb-1">{stat?.value}</div>
              <div className="text-xs text-fg-muted">{stat?.label}</div>
            </div>
          ))}
        </div>

        {/* Testimonials */}
        <div className="text-center mb-8">
          <h2 className="font-display text-2xl sm:text-3xl font-semibold text-fg mb-2">
            People who{' '}
            <span className="italic text-primary">love XPlatform</span>
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-14">
          {testimonials?.map((t, i) => (
            <div key={i} className="card-warm p-5">
              <p className="text-sm text-fg-secondary leading-relaxed mb-4 italic">&ldquo;{t?.quote}&rdquo;</p>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center text-lg">{t?.avatar}</div>
                <div>
                  <p className="text-sm font-semibold text-fg">{t?.name}</p>
                  <p className="text-xs text-fg-muted">{t?.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Final CTA */}
        <div className="text-center py-14 px-6 rounded-3xl bg-gradient-to-br from-primary-pale via-accent-pale to-xai-pale border border-border">
          <h2 className="font-display text-3xl sm:text-4xl font-semibold text-fg mb-3">
            Ready to feel the{' '}
            <span className="italic text-primary">difference?</span>
          </h2>
          <p className="text-base text-fg-secondary mb-7 max-w-lg mx-auto">
            Join thousands who start their day with XLife, find what they need on XDiscover, and let XAI handle the rest.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href="/x-life-feed" className="btn-primary px-8 py-3.5 text-base inline-flex items-center gap-2 pulse-glow">
              Start with XLife
            </Link>
            <Link href="/x-discover-marketplace" className="btn-secondary px-8 py-3.5 text-base inline-flex items-center gap-2">
              Browse XDiscover
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
