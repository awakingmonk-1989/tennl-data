import React from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import XLifeFeedClient from "./components/XLifeFeedClient";

export default function XLifeFeedPage() {
  return (
    <main className="min-h-screen bg-warm-gradient">
      <Header />
      <XLifeFeedClient />
      <Footer />
    </main>
  );
}
