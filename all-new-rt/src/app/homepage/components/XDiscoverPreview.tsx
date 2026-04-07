'use client';

import React, { useState } from 'react';
import Link from 'next/link';

const sampleQuery = '2BHK with parking under ₹30k near a good school in Koramangala';

const sampleResults = [
  { title: 'Spacious 2BHK with Covered Parking', location: 'Koramangala 5th Block', price: '₹27,500/mo', tags: ['Near DPS', 'Covered Parking', 'Gym'], match: 96 },
  { title: 'Modern 2BHK in Gated Society', location: 'HSR Layout Sector 2', price: '₹29,000/mo', tags: ['Near National Public School', 'Parking', 'Pool'], match: 91 },
];

export default function XDiscoverPreview() {
  const [step, setStep] = useState<'idle' | 'typing' | 'searching' | 'results'>('idle');
  const [progress, setProgress] = useState(0);

  const handleDemo = () => {
    setStep('typing');
    setTimeout(() => {
      setStep('searching');
      let p = 0;
      const interval = setInterval(() => {
        p += 8;
        setProgress(Math.min(p, 100));
        if (p >= 100) {
          clearInterval(interval);
          setStep('results');
        }
      }, 120);
    }, 1200);
  };

  const handleReset = () => {
    setStep('idle');
    setProgress(0);
  };

  return (
    <section className="py-12 sm:py-16 px-4 sm:px-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-10">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2.5 h-2.5 rounded-full bg-xdiscover" />
            <span className="text-sm font-semibold text-xdiscover uppercase tracking-wider">XDiscover</span>
          </div>
          <h2 className="font-display text-2xl sm:text-3xl font-semibold text-fg">
            Just say what you need.{' '}
            <span className="italic text-xdiscover">AI finds it.</span>
          </h2>
        </div>
        <Link href="/x-discover-marketplace" className="inline-flex items-center gap-1.5 text-sm font-semibold text-xdiscover hover:underline underline-offset-2 shrink-0">
          Open Marketplace
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </Link>
      </div>
      <div className="max-w-2xl mx-auto">
        {/* Search bar demo */}
        <div className="search-warm p-4 mb-4 flex items-center gap-3">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" className="text-xdiscover shrink-0">
            <circle cx="8" cy="8" r="5.5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M12.5 12.5L16 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <span className={`flex-1 text-sm ${step === 'idle' ? 'text-fg-muted' : 'text-fg'}`}>
            {step === 'idle' ? 'Try: "2BHK with parking under ₹30k near a good school..."' : sampleQuery}
            {step === 'typing' && <span className="cursor-blink ml-0.5 text-xdiscover">|</span>}
          </span>
          {step === 'idle' && (
            <button onClick={handleDemo} className="shrink-0 px-4 py-2 rounded-full text-xs font-semibold text-white bg-xdiscover hover:opacity-90 transition-opacity">
              Try Demo
            </button>
          )}
          {step !== 'idle' && step !== 'results' && (
            <div className="shrink-0 w-5 h-5 rounded-full border-2 border-xdiscover border-t-transparent animate-spin" />
          )}
        </div>

        {/* Searching state */}
        {step === 'searching' && (
          <div className="card-warm p-5 mb-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-lg">🤖</span>
              <span className="text-sm font-semibold text-fg">XAI is searching across listings...</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-xdiscover rounded-full transition-all duration-150"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-xs text-fg-muted">Scanning 2,400+ listings</span>
              <span className="text-xs font-medium text-xdiscover">{progress}%</span>
            </div>
          </div>
        )}

        {/* Results */}
        {step === 'results' && (
          <div className="space-y-3">
            <p className="text-xs font-medium text-fg-muted mb-2">✨ Top matches for your query</p>
            {sampleResults?.map((r, i) => (
              <div key={i} className="listing-card p-4 flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-fg">{r?.title}</span>
                    <span className="pill bg-xdiscover-pale text-xdiscover border border-xdiscover/20 text-xs">{r?.match}% match</span>
                  </div>
                  <p className="text-xs text-fg-muted mb-2">📍 {r?.location}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {r?.tags?.map((tag) => (
                      <span key={tag} className="pill bg-muted text-fg-secondary text-xs border border-border">{tag}</span>
                    ))}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2 shrink-0">
                  <span className="font-semibold text-fg">{r?.price}</span>
                  <button className="px-3 py-1.5 rounded-full text-xs font-semibold text-white bg-xdiscover hover:opacity-90 transition-opacity">
                    Connect via AI
                  </button>
                </div>
              </div>
            ))}
            <button onClick={handleReset} className="text-xs text-fg-muted hover:text-primary underline underline-offset-2 mt-2">
              Reset demo
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
