import React from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import HeroSection from "./components/HeroSection";
import FeaturesTrioSection from "./components/FeaturesTrioSection";
import XLifePreviewSection from "./components/XLifePreviewSection";
import XDiscoverPreviewSection from "./components/XDiscoverPreviewSection";
import XAISection from "./components/XAISection";
import MetricsCTASection from "./components/MetricsCTASection";

export default function Homepage() {
  return (
    <main className="bg-warm-gradient min-h-screen">
      <Header />
      <HeroSection />
      <FeaturesTrioSection />
      <XLifePreviewSection />
      <XDiscoverPreviewSection />
      <XAISection />
      <MetricsCTASection />
      <Footer />
    </main>
  );
}
