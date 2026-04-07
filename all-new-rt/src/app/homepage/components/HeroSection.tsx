"use client";
import React, { useEffect, useRef } from "react";
import Link from "next/link";
import AppImage from "@/components/ui/AppImage";

export default function HeroSection() {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!heroRef.current) return;
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      const x = (clientX / innerWidth - 0.5) * 20;
      const y = (clientY / innerHeight - 0.5) * 20;
      const blobs = heroRef.current.querySelectorAll<HTMLElement>(".parallax-blob");
      blobs.forEach((blob, i) => {
        const factor = (i + 1) * 0.4;
        blob.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
      });
    };
    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <section ref={heroRef} className="relative min-h-screen flex flex-col justify-center overflow-hidden pt-20">
      {/* Background blobs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div
          className="parallax-blob absolute -top-32 -right-32 w-[600px] h-[600px] rounded-full opacity-30 blob-animate"
          style={{ background: "radial-gradient(circle, #FFB347 0%, #FF6B35 50%, transparent 70%)" }} />
        
        <div
          className="parallax-blob absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full opacity-20 blob-animate-2"
          style={{ background: "radial-gradient(circle, #2DD4BF 0%, #06B6D4 50%, transparent 70%)" }} />
        
        <div
          className="parallax-blob absolute top-1/2 left-1/3 w-[300px] h-[300px] rounded-full opacity-15 blob-animate"
          style={{ background: "radial-gradient(circle, #A78BFA 0%, transparent 70%)", animationDelay: "3s" }} />
        
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        {/* Eyebrow */}
        <div className="flex items-center gap-3 mb-8">
          <div className="flex items-center gap-2 bg-primary-pale border border-border-warm rounded-full px-4 py-2">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="section-label text-primary">Powered by AI</span>
          </div>
        </div>

        {/* Massive headline */}
        <div className="mb-10">
          <h1 className="magazine-heading text-fg leading-none">
            <span className="block">Your world,</span>
            <span className="block gradient-text-primary">curated</span>
            <span className="block">by AI.</span>
          </h1>
        </div>

        {/* Subheadline + CTA row */}
        <div className="grid lg:grid-cols-2 gap-12 items-end">
          <div className="space-y-8">
            <p className="text-xl text-fg-muted leading-relaxed max-w-lg font-body">
              XPlatform brings together AI-curated content that refreshes your mind, an intelligent marketplace that finds what you need, and automation that handles the rest.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                href="/x-life-feed"
                className="inline-flex items-center gap-2 bg-coral-gradient text-white px-7 py-4 rounded-2xl font-bold font-display text-base hover:opacity-90 transition-all shadow-warm-md hover:shadow-warm-lg hover:-translate-y-1">
                
                <span>Explore XLife</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </Link>
              <Link
                href="/x-discover-marketplace"
                className="inline-flex items-center gap-2 bg-white border-2 border-border text-fg px-7 py-4 rounded-2xl font-bold font-display text-base hover:border-xdiscover hover:text-xdiscover transition-all shadow-card hover:-translate-y-0.5">
                
                <span>XDiscover</span>
              </Link>
            </div>
          </div>

          {/* Floating feature cards */}
          <div className="relative h-64 lg:h-80 hidden lg:block">
            {/* XLife card */}
            <div className="absolute top-0 left-0 bg-white rounded-2xl p-5 shadow-card border border-border-warm float-anim w-52">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-xl bg-primary-pale flex items-center justify-center">
                  <span className="text-lg">📖</span>
                </div>
                <span className="font-display font-bold text-sm text-xlife">XLife</span>
              </div>
              <div className="space-y-1.5">
                <div className="h-2 bg-primary-pale rounded-full w-full" />
                <div className="h-2 bg-primary-pale rounded-full w-4/5" />
                <div className="h-2 bg-primary-pale rounded-full w-3/5" />
              </div>
              <div className="mt-3 flex items-center gap-2">
                <div className="circle-timer">
                  <svg width="28" height="28" viewBox="0 0 28 28">
                    <circle className="circle-timer-track" cx="14" cy="14" r="11" />
                    <circle
                      className="circle-timer-progress"
                      cx="14" cy="14" r="11"
                      strokeDasharray="69.1"
                      strokeDashoffset="25"
                      style={{ transform: "rotate(-90deg)", transformOrigin: "50% 50%" }} />
                    
                  </svg>
                </div>
                <span className="text-xs text-fg-muted font-medium">60s read</span>
              </div>
            </div>

            {/* XDiscover card */}
            <div className="absolute top-6 right-0 bg-white rounded-2xl p-5 shadow-card border border-border float-anim-slow w-56" style={{ animationDelay: "1s" }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-xl bg-teal-100 flex items-center justify-center">
                  <span className="text-lg">🔍</span>
                </div>
                <span className="font-display font-bold text-sm text-xdiscover">XDiscover</span>
              </div>
              <div className="bg-gray-50 rounded-xl px-3 py-2 text-xs text-fg-muted font-body">
                2BHK near school, under ₹30k...
              </div>
              <div className="mt-3 flex gap-1.5">
                <span className="tag-pill bg-teal-50 text-teal-600 text-xs">12 matches</span>
                <span className="tag-pill bg-amber-50 text-amber-600 text-xs">AI sorted</span>
              </div>
            </div>

            {/* XAI card */}
            <div className="absolute bottom-0 left-16 bg-white rounded-2xl p-5 shadow-card border border-border float-anim w-48" style={{ animationDelay: "2s" }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-xl bg-purple-50 flex items-center justify-center">
                  <span className="text-lg">🤖</span>
                </div>
                <span className="font-display font-bold text-sm text-xai">XAI</span>
              </div>
              <p className="text-xs text-fg-muted leading-relaxed">Agent running 24/7...</p>
              <div className="mt-2 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-xs text-green-600 font-medium">Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="mt-16 flex items-center gap-3 text-fg-subtle">
          <div className="w-8 h-12 border-2 border-border rounded-full flex items-start justify-center pt-2">
            <div className="w-1.5 h-3 bg-primary rounded-full animate-bounce" />
          </div>
          <span className="text-xs font-medium tracking-widest uppercase">Scroll to explore</span>
        </div>
      </div>

      {/* Hero image strip */}
      <div className="relative z-10 mt-4 lg:mt-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-3 gap-3 lg:gap-4 h-32 lg:h-48 overflow-hidden rounded-3xl">
            <div className="relative overflow-hidden rounded-2xl">
              <AppImage
                src="https://images.unsplash.com/photo-1589550579127-e0cc740ccc95"
                alt="Bright morning landscape with warm golden light over rolling hills"
                fill
                className="object-cover"
                sizes="(max-width: 768px) 33vw, 250px" />
              
              <div className="absolute inset-0 bg-gradient-to-t from-primary/30 to-transparent" />
              <span className="absolute bottom-3 left-3 tag-pill bg-white/90 text-xlife text-xs">XLife</span>
            </div>
            <div className="relative overflow-hidden rounded-2xl">
              <AppImage
                src="https://img.rocket.new/generatedImages/rocket_gen_img_19f95dac5-1773093030027.png"
                alt="Bright modern apartment interior with large windows and natural light"
                fill
                className="object-cover"
                sizes="(max-width: 768px) 33vw, 250px" />
              
              <div className="absolute inset-0 bg-gradient-to-t from-xdiscover/40 to-transparent" />
              <span className="absolute bottom-3 left-3 tag-pill bg-white/90 text-xdiscover text-xs">XDiscover</span>
            </div>
            <div className="relative overflow-hidden rounded-2xl">
              <AppImage
                src="https://img.rocket.new/generatedImages/rocket_gen_img_15afdb008-1772093387845.png"
                alt="Futuristic AI visualization with glowing nodes on white background"
                fill
                className="object-cover"
                sizes="(max-width: 768px) 33vw, 250px" />
              
              <div className="absolute inset-0 bg-gradient-to-t from-xai/40 to-transparent" />
              <span className="absolute bottom-3 left-3 tag-pill bg-white/90 text-xai text-xs">XAI</span>
            </div>
          </div>
        </div>
      </div>
    </section>);

}
