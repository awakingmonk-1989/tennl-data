"use client";
import React, { useRef, useEffect, useState } from "react";
import Link from "next/link";

const metrics = [
  { value: 2400000, label: "Content pieces served", suffix: "+", display: "2.4M+" },
  { value: 340000, label: "Active listings", suffix: "", display: "340K" },
  { value: 50, label: "Expert mentors", suffix: "+", display: "50+" },
  { value: 98, label: "AI accuracy", suffix: "%", display: "98%" },
];

const testimonials = [
  {
    quote: "XDiscover found me the perfect 2BHK near my daughter\'s school in 4 minutes. I\'d been searching for 3 weeks.",
    name: "Meera Krishnamurthy",
    role: "Teacher, Bangalore",
    avatar: "https://i.pravatar.cc/100?u=meera",
  },
  {
    quote: "The XLife feed is my morning ritual. Articles are always relevant, never overwhelming. The timer is genius.",
    name: "Arjun Patel",
    role: "Product Manager, Mumbai",
    avatar: "https://i.pravatar.cc/100?u=arjun",
  },
  {
    quote: "Set up a deal-hunting agent for my wishlist. Saved ₹12,000 last month without doing anything.",
    name: "Divya Shankar",
    role: "Freelance Designer, Pune",
    avatar: "https://i.pravatar.cc/100?u=divya",
  },
];

export default function MetricsCTASection() {
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % testimonials?.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

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

  const t = testimonials?.[activeTestimonial];

  return (
    <section ref={sectionRef} className="py-16 lg:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Testimonial */}
        <div className="reveal-on-scroll mb-16 bg-white rounded-3xl border border-border p-8 lg:p-12 shadow-card">
          <div className="max-w-3xl mx-auto text-center">
            <div className="text-4xl mb-6">❝</div>
            <p className="font-display font-medium text-xl lg:text-2xl text-fg leading-relaxed mb-8 transition-all duration-500">
              {t?.quote}
            </p>
            <div className="flex items-center justify-center gap-3">
              <img src={t?.avatar} alt={t?.name} className="w-12 h-12 rounded-full object-cover" />
              <div className="text-left">
                <p className="font-display font-bold text-sm text-fg">{t?.name}</p>
                <p className="text-xs text-fg-muted">{t?.role}</p>
              </div>
            </div>
            <div className="mt-6 flex justify-center gap-2">
              {testimonials?.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setActiveTestimonial(i)}
                  className={`transition-all duration-300 rounded-full ${i === activeTestimonial ? "w-8 h-2 bg-primary" : "w-2 h-2 bg-border"}`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="reveal-on-scroll bg-coral-gradient rounded-3xl p-10 lg:p-16 text-center text-white relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-white/10 blob-animate" />
          <div className="absolute -bottom-16 -left-16 w-48 h-48 rounded-full bg-white/10 blob-animate-2" />
          <div className="relative z-10">
            <span className="section-label text-white/70 mb-4 block">Start for free</span>
            <h2 className="font-display font-extrabold text-display-md text-white leading-tight mb-6">
              Your AI life starts today.
            </h2>
            <p className="text-white/80 text-lg max-w-xl mx-auto mb-10">
              Join 180,000+ people who use XPlatform to consume better content, discover smarter, and automate the boring stuff.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/x-life-feed" className="bg-white text-primary font-bold font-display text-base px-8 py-4 rounded-2xl hover:bg-primary-pale transition-all shadow-lg hover:-translate-y-1">
                Start with XLife
              </Link>
              <Link href="/x-discover-marketplace" className="border-2 border-white/50 text-white font-bold font-display text-base px-8 py-4 rounded-2xl hover:bg-white/10 transition-all">
                Explore XDiscover
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
