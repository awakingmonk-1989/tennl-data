"use client";
import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import AppImage from "@/components/ui/AppImage";

const previewListings = [
{
  id: 1,
  type: "Rental",
  title: "Spacious 2BHK with Garden View",
  location: "Koramangala, Bangalore",
  price: "₹28,000/mo",
  usp: "5 min walk to DPS School",
  tags: ["Parking", "Pet OK", "Furnished"],
  image: "https://images.unsplash.com/photo-1646607523833-d791a89b3f99",
  imageAlt: "Bright modern apartment living room with natural light and green plants",
  aiScore: 97
},
{
  id: 2,
  type: "Service",
  title: "Priya\'s Home Cleaning Co.",
  location: "HSR Layout, Bangalore",
  price: "₹799/session",
  usp: "4.9★ · 340 reviews · Same-day booking",
  tags: ["Verified", "Insured", "Eco"],
  image: "https://img.rocket.new/generatedImages/rocket_gen_img_129d8935b-1772185190403.png",
  imageAlt: "Clean bright modern kitchen after professional cleaning with sunlight",
  aiScore: 94
},
{
  id: 3,
  type: "Job",
  title: "Product Designer · Remote",
  location: "Fintech startup · Series B",
  price: "₹18–28 LPA",
  usp: "Hiring urgently · 3 rounds only",
  tags: ["Remote", "Equity", "Flexible"],
  image: "https://img.rocket.new/generatedImages/rocket_gen_img_1d54100e6-1773157828251.png",
  imageAlt: "Bright open-plan office with natural light and collaborative workspace",
  aiScore: 91
}];


export default function XDiscoverPreviewSection() {
  const [query, setQuery] = useState("2BHK near good school, parking, under ₹30k in Bangalore");
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(true);
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
    if (sectionRef?.current) observer?.observe(sectionRef?.current);
    return () => observer?.disconnect();
  }, []);

  const handleSearch = () => {
    if (!query?.trim()) return;
    setSearching(true);
    setShowResults(false);
    setTimeout(() => {
      setSearching(false);
      setShowResults(true);
    }, 1200);
  };

  return (
    <section ref={sectionRef} className="py-16 lg:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="reveal-on-scroll mb-10 lg:mb-14 flex flex-col sm:flex-row sm:items-end justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-8 h-1 rounded-full bg-xdiscover block" />
              <span className="section-label text-xdiscover">XDiscover</span>
            </div>
            <h2 className="font-display font-extrabold text-display-md text-fg leading-tight">
              Tell AI what you need.<br className="hidden sm:block" /> It finds. You choose.
            </h2>
          </div>
          <Link href="/x-discover-marketplace" className="inline-flex items-center gap-2 bg-teal-gradient text-white px-6 py-3 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all shadow-sm self-start sm:self-auto">
            Open XDiscover
          </Link>
        </div>

        {/* AI Search bar */}
        <div className="reveal-on-scroll mb-8">
          <div className="search-glow bg-white rounded-2xl border-2 border-border p-4 flex flex-col sm:flex-row gap-3 transition-all">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center flex-shrink-0">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2DD4BF" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
                </svg>
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e?.target?.value)}
                onKeyDown={(e) => e?.key === "Enter" && handleSearch()}
                className="flex-1 bg-transparent text-fg placeholder-fg-subtle font-body text-base focus:outline-none"
                placeholder="Describe what you're looking for in plain English..." />
              
            </div>
            <button
              onClick={handleSearch}
              className="bg-teal-gradient text-white px-6 py-3 rounded-xl font-bold font-display text-sm hover:opacity-90 transition-all whitespace-nowrap flex items-center gap-2">
              
              {searching ?
              <>
                  <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" opacity="0.3" />
                    <path d="M21 12a9 9 0 00-9-9" />
                  </svg>
                  Searching...
                </> :

              <>AI Search</>
              }
            </button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2 px-1">
            <span className="text-xs text-fg-muted font-medium">Try:</span>
            {["Interior designer under ₹50k", "Remote React developer", "Dog-friendly apartments"]?.map((s) =>
            <button key={s} onClick={() => setQuery(s)} className="text-xs text-xdiscover hover:underline font-medium">
                {s}
              </button>
            )}
          </div>
        </div>

        {/* Listing cards */}
        {showResults &&
        <div className="reveal-on-scroll stagger-children grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5">
            {previewListings?.map((listing) =>
          <div key={listing?.id} className="listing-card group">
                <div className="relative h-44 overflow-hidden">
                  <AppImage
                src={listing?.image}
                alt={listing?.imageAlt}
                fill
                className="object-cover transition-transform duration-500 group-hover:scale-105"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw" />
              
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                  <div className="absolute top-3 left-3 flex gap-2">
                    <span className="tag-pill bg-white/95 text-fg text-xs">{listing?.type}</span>
                    <span className="tag-pill bg-teal-500/90 text-white text-xs">AI {listing?.aiScore}%</span>
                  </div>
                </div>
                <div className="p-5">
                  <h3 className="font-display font-bold text-base text-fg mb-1">{listing?.title}</h3>
                  <p className="text-xs text-fg-muted mb-2">{listing?.location}</p>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-display font-extrabold text-lg text-fg">{listing?.price}</span>
                    <div className="flex gap-1.5">
                      {listing?.tags?.slice(0, 2)?.map((tag) =>
                  <span key={tag} className="tag-pill bg-gray-50 text-fg-muted text-xs">{tag}</span>
                  )}
                    </div>
                  </div>
                  <div className="bg-teal-50 rounded-xl px-3 py-2 mb-4">
                    <p className="text-xs text-teal-700 font-medium">✦ {listing?.usp}</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="flex-1 bg-teal-gradient text-white py-2.5 rounded-xl font-bold font-display text-xs hover:opacity-90 transition-all">
                      AI Connect
                    </button>
                    <button className="px-3 py-2.5 border-2 border-border rounded-xl text-fg-muted hover:border-xdiscover hover:text-xdiscover transition-all">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81a19.79 19.79 0 01-3.07-8.68A2 2 0 012 .9h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 8.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
          )}
          </div>
        }

        {searching &&
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5">
            {[1, 2, 3]?.map((i) =>
          <div key={i} className="rounded-2xl overflow-hidden border border-border">
                <div className="shimmer h-44 w-full" />
                <div className="p-5 space-y-3">
                  <div className="shimmer h-4 rounded-full w-3/4" />
                  <div className="shimmer h-3 rounded-full w-1/2" />
                  <div className="shimmer h-8 rounded-xl w-full mt-4" />
                </div>
              </div>
          )}
          </div>
        }
      </div>
    </section>);

}
