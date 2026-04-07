import React from "react";
import Link from "next/link";
import AppLogo from "@/components/ui/AppLogo";

export default function Footer() {
  return (
    <footer className="border-t border-border bg-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Pattern 3: Vercel Horizontal Flow */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          <Link href="/homepage" className="flex items-center gap-2.5">
            <AppLogo size={32} />
            <span className="font-display font-extrabold text-base tracking-tight text-fg">XPlatform</span>
          </Link>

          <nav className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            {[
              { label: "XLife", href: "/x-life-feed" },
              { label: "XDiscover", href: "/x-discover-marketplace" },
              { label: "XAI", href: "/homepage#xai" },
              { label: "About", href: "/homepage" },
            ]?.map((link) => (
              <Link
                key={link?.href}
                href={link?.href}
                className="text-sm font-medium text-fg-muted hover:text-fg transition-colors"
              >
                {link?.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            {/* Twitter/X */}
            <a href="#" aria-label="X (Twitter)" className="text-fg-subtle hover:text-fg transition-colors p-1">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.26 5.632zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
            {/* Instagram */}
            <a href="#" aria-label="Instagram" className="text-fg-subtle hover:text-fg transition-colors p-1">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <rect x="2" y="2" width="20" height="20" rx="5" />
                <circle cx="12" cy="12" r="4" />
                <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
              </svg>
            </a>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-fg-subtle">
          <p>© 2026 XPlatform Inc. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-fg-muted transition-colors">Privacy</a>
            <span>·</span>
            <a href="#" className="hover:text-fg-muted transition-colors">Terms</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
