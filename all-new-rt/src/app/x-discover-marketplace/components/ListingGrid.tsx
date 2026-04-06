"use client";
import React from "react";
import AppImage from "@/components/ui/AppImage";
import { Listing } from "./listingsData";

interface ListingGridProps {
  listings: Listing[];
  isLoading: boolean;
  onConnect: (id: string) => void;
  connectedListings: Set<string>;
}

export default function ListingGrid({
  listings,
  isLoading,
  onConnect,
  connectedListings,
}: ListingGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="rounded-2xl overflow-hidden border border-border bg-white">
            <div className="shimmer h-44 w-full" />
            <div className="p-5 space-y-3">
              <div className="shimmer h-4 rounded-full w-3/4" />
              <div className="shimmer h-3 rounded-full w-1/2" />
              <div className="shimmer h-3 rounded-full w-2/3" />
              <div className="shimmer h-10 rounded-xl w-full mt-4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!listings.length) {
    return (
      <div className="text-center py-20">
        <div className="text-5xl mb-4">🔍</div>
        <p className="font-display font-bold text-xl text-fg mb-2">No results found</p>
        <p className="text-fg-muted text-sm">Try a different search or category</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-5">
      {listings.map((listing, idx) => {
        const isConnected = connectedListings.has(listing.id);
        return (
          <div
            key={listing.id}
            className="listing-card group reveal-on-scroll"
            style={{ transitionDelay: `${idx * 60}ms` }}
          >
            {/* Image */}
            <div className="relative h-44 overflow-hidden">
              <AppImage
                src={listing.image}
                alt={listing.imageAlt}
                fill
                className="object-cover transition-transform duration-500 group-hover:scale-105"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
              <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
                <span className="tag-pill bg-white/95 text-fg text-xs">{listing.type}</span>
                {listing.aiScore && (
                  <span className="tag-pill bg-teal-500/90 text-white text-xs">
                    AI {listing.aiScore}%
                  </span>
                )}
              </div>
              {listing.featured && (
                <span className="absolute top-3 right-3 tag-pill bg-amber-400 text-white text-xs">
                  ✦ Featured
                </span>
              )}
            </div>

            {/* Content */}
            <div className="p-5">
              <h3 className="font-display font-bold text-base text-fg mb-1 leading-tight">
                {listing.title}
              </h3>
              <p className="text-xs text-fg-muted mb-3 flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                {listing.location}
              </p>

              {/* Price + tags row */}
              <div className="flex items-center justify-between mb-3">
                <span className="font-display font-extrabold text-lg text-fg">
                  {listing.price}
                </span>
                <div className="flex gap-1">
                  {listing.tags.slice(0, 2).map((tag) => (
                    <span key={tag} className="tag-pill bg-gray-50 text-fg-muted text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* USP */}
              <div className="bg-teal-50 rounded-xl px-3 py-2 mb-4">
                <p className="text-xs text-teal-700 font-medium leading-snug">
                  ✦ {listing.usp}
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => onConnect(listing.id)}
                  className={`flex-1 py-2.5 rounded-xl font-bold font-display text-xs transition-all ${
                    isConnected
                      ? "bg-green-50 border-2 border-green-300 text-green-700" :"bg-teal-gradient text-white hover:opacity-90"
                  }`}
                >
                  {isConnected ? "✓ Connected" : "AI Connect"}
                </button>
                {/* Call */}
                <a
                  href={`tel:${listing.phone || "+919999999999"}`}
                  className="px-3 py-2.5 border-2 border-border rounded-xl text-fg-muted hover:border-xdiscover hover:text-xdiscover transition-all"
                  aria-label="Call"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81 19.79 19.79 0 01.4 1.18 2 2 0 012.38.9h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 8.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" />
                  </svg>
                </a>
                {/* WhatsApp */}
                <a
                  href={`https://wa.me/${listing.whatsapp || "919999999999"}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2.5 border-2 border-border rounded-xl text-fg-muted hover:border-green-400 hover:text-green-600 transition-all"
                  aria-label="WhatsApp"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
