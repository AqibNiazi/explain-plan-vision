import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

export default function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col relative">
      {/* Atmospheric background */}
      <div className="grid-bg" />
      <div className="scanlines" />
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      <Navbar />

      <main className="relative z-10 flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}
