"use client";

import React from "react";
import { ShieldCheck, Lock, MapPin, User, Scale, MessageSquare, Database } from "lucide-react";

interface NavbarProps {
  activeTab: "customer" | "auditor" | "chat" | "security";
  setActiveTab: (tab: "customer" | "auditor" | "chat" | "security") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3.5 shadow-2xl">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Logo */}
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
            <span className="text-xl font-black text-white tracking-tighter">भा</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                BharatBanker AI
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                v1.0 Production
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Unified Decisioning Platform for Hyper-Personalization & Lending Ethics
            </p>
          </div>
        </div>

        {/* Compliance Guardrail Badges */}
        <div className="hidden lg:flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>RBI Digital Lending (3-Day Cooling Off)</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/25 text-indigo-400 text-xs font-medium">
            <Lock className="w-3.5 h-3.5 text-indigo-400" />
            <span>DPDP Act 2023 (Masked Aadhaar)</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-sky-500/10 border border-sky-500/25 text-sky-400 text-xs font-medium">
            <MapPin className="w-3.5 h-3.5 text-sky-400" />
            <span>AWS Mumbai (ap-south-1)</span>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <nav className="flex items-center p-1 bg-slate-900/90 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab("customer")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "customer"
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Customer 360</span>
          </button>

          <button
            onClick={() => setActiveTab("auditor")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "auditor"
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            <span>Judge Live Auditor</span>
          </button>

          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "chat"
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Vernacular Chat</span>
          </button>

          <button
            onClick={() => setActiveTab("security")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === "security"
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Security Vault</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
