import React from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import XDiscoverClient from "./components/XDiscoverClient";

export default function XDiscoverMarketplacePage() {
  return (
    <main className="min-h-screen bg-warm-gradient">
      <Header />
      <XDiscoverClient />
      <Footer />
    </main>
  );
}
