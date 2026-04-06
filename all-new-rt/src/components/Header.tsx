"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AppLogo from "@/components/ui/AppLogo";

const navLinks = [
  { label: "XLife", href: "/x-life-feed", color: "text-xlife" },
  { label: "XDiscover", href: "/x-discover-marketplace", color: "text-xdiscover" },
  { label: "XAI", href: "/homepage#xai", color: "text-xai" },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? "nav-glass shadow-sm" : "bg-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            {/* Logo */}
            <Link href="/homepage" className="flex items-center gap-2.5 group">
              <AppLogo size={36} />
              <span className="font-display font-800 text-lg tracking-tight text-fg hidden sm:block">
                XPlatform
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1">
              {navLinks?.map((link) => (
                <Link
                  key={link?.href}
                  href={link?.href}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold font-display transition-all duration-200 ${
                    pathname === link?.href
                      ? `${link?.color} bg-primary-pale`
                      : "text-fg-muted hover:text-fg hover:bg-gray-50"
                  }`}
                >
                  {link?.label}
                </Link>
              ))}
            </nav>

            {/* CTA */}
            <div className="hidden lg:flex items-center gap-3">
              <button className="text-sm font-semibold font-display text-fg-muted hover:text-fg transition-colors px-4 py-2">
                Sign in
              </button>
              <Link
                href="/homepage"
                className="bg-coral-gradient text-white px-5 py-2.5 rounded-xl text-sm font-bold font-display hover:opacity-90 transition-all shadow-warm-sm hover:shadow-warm-md hover:-translate-y-0.5"
              >
                Get Started
              </Link>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMenuOpen(true)}
              className="lg:hidden p-2 text-fg-muted hover:text-fg transition-colors rounded-lg"
              aria-label="Open menu"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>
          </div>
        </div>
      </header>
      {/* Mobile Menu */}
      {menuOpen && (
        <div className="fixed inset-0 z-[100] mobile-menu-overlay flex flex-col">
          <div className="flex items-center justify-between px-4 py-4 border-b border-border">
            <Link href="/homepage" className="flex items-center gap-2.5" onClick={() => setMenuOpen(false)}>
              <AppLogo size={36} />
              <span className="font-display font-extrabold text-lg tracking-tight text-fg">XPlatform</span>
            </Link>
            <button
              onClick={() => setMenuOpen(false)}
              className="p-2 text-fg-muted hover:text-fg rounded-lg transition-colors"
              aria-label="Close menu"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <nav className="flex flex-col gap-2 px-4 pt-8">
            {navLinks?.map((link) => (
              <Link
                key={link?.href}
                href={link?.href}
                onClick={() => setMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-4 rounded-2xl text-xl font-bold font-display transition-all ${
                  pathname === link?.href ? `${link?.color} bg-primary-pale` : "text-fg hover:bg-gray-50"
                }`}
              >
                {link?.label}
              </Link>
            ))}
          </nav>
          <div className="mt-auto px-4 pb-12 flex flex-col gap-3">
            <button className="w-full py-4 border-2 border-border rounded-2xl text-fg font-bold font-display text-base hover:border-primary transition-colors">
              Sign in
            </button>
            <Link
              href="/homepage"
              onClick={() => setMenuOpen(false)}
              className="w-full py-4 bg-coral-gradient text-white rounded-2xl font-bold font-display text-base text-center hover:opacity-90 transition-opacity shadow-warm-md"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      )}
    </>
  );
}
