"use client";

import React, { useState } from "react";
import { 
  ShieldAlert, 
  CheckCircle2, 
  TrendingUp, 
  Wallet, 
  PieChart, 
  Percent, 
  Sparkles, 
  Languages, 
  ArrowRight,
  HelpCircle
} from "lucide-react";
import { DashboardResponse } from "../lib/types";

interface CustomerPortalProps {
  data: DashboardResponse;
  onOpenChat: () => void;
}

export const CustomerPortal: React.FC<CustomerPortalProps> = ({ data, onOpenChat }) => {
  const [showHindi, setShowHindi] = useState(true);
  const { customer_profile: profile, contract_2_veto_outcome: veto } = data;
  const action = veto.final_action;

  // Color mapping based on health category
  const isHealthy = veto.financial_health_score >= 80;
  const isWatch = veto.financial_health_score >= 60 && veto.financial_health_score < 80;
  const isStress = veto.financial_health_score < 40;

  const scoreColor = isHealthy
    ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
    : isWatch
    ? "text-amber-400 bg-amber-500/10 border-amber-500/30"
    : "text-rose-400 bg-rose-500/10 border-rose-500/30";

  return (
    <div className="space-y-6">
      {/* 1. EXECUTIVE STATUS BANNER (Instant Clarity on What is Happening) */}
      <div
        className={`p-4 rounded-2xl border backdrop-blur-md transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
          veto.veto_triggered
            ? "bg-rose-950/30 border-rose-500/40 badge-glow-rose"
            : "bg-emerald-950/20 border-emerald-500/30 badge-glow-emerald"
        }`}
      >
        <div className="flex items-center gap-3.5">
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
              veto.veto_triggered
                ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
            }`}
          >
            {veto.veto_triggered ? (
              <ShieldAlert className="w-6 h-6 text-rose-400 animate-pulse" />
            ) : (
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Lending Decision Engine Status
              </span>
              <span
                className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border uppercase ${
                  veto.veto_triggered
                    ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                    : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                }`}
              >
                {veto.veto_triggered ? "🛑 Hard Veto Active" : "🟢 Pre-Approved Clean"}
              </span>
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white mt-0.5">
              {veto.veto_triggered
                ? "Predatory Loan Blocked: Empathetic Restructuring Activated"
                : `Affinity Match Verified: Safe Headroom for ${profile.name}`}
            </h3>
            <p className="text-xs text-slate-300 mt-0.5 max-w-2xl">
              {veto.veto_reason
                ? veto.veto_reason
                : `Evaluated via Person 2 Ethical Veto Layer: DTI (${(profile.dti_ratio * 100).toFixed(1)}%) is strictly beneath the 50.0% regulatory ceiling.`}
            </p>
          </div>
        </div>

        {/* DPDP Consent Badge */}
        <div className="shrink-0 flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>DPDP Tier {profile.dpdp_consent_tier} Validated</span>
        </div>
      </div>

      {/* 2. EXECUTIVE METRIC KPI GRID (Clear Labels, No Text Bloat) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Salary */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="font-semibold uppercase tracking-wider">Monthly Salary</span>
            <Wallet className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-white">
            ₹{profile.monthly_salary.toLocaleString("en-IN")}
          </div>
          <div className="flex items-center gap-1 mt-2 text-[11px] text-slate-400">
            <span className="text-emerald-400 font-semibold">Verified CBS Flow</span>
            <span>• {profile.account_vintage_months}m vintage</span>
          </div>
        </div>

        {/* KPI 2: DTI Ratio */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="font-semibold uppercase tracking-wider">Debt-To-Income</span>
            <Percent className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white">
            {(profile.dti_ratio * 100).toFixed(1)}%
          </div>
          <div className="flex items-center gap-1 mt-2 text-[11px]">
            <span
              className={`font-semibold ${
                profile.dti_ratio > 0.5 ? "text-rose-400" : "text-emerald-400"
              }`}
            >
              {profile.dti_ratio > 0.5 ? "⚠️ Over 50% Cap" : "✓ Within 50% Cap"}
            </span>
            <span className="text-slate-400">• Max safe limit</span>
          </div>
        </div>

        {/* KPI 3: Health Score */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="font-semibold uppercase tracking-wider">Health Score</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-white">
              {veto.financial_health_score}
            </span>
            <span className="text-xs text-slate-400 font-bold">/ 100</span>
          </div>
          <div className="mt-2">
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${scoreColor}`}>
              {veto.health_category}
            </span>
          </div>
        </div>

        {/* KPI 4: Segment */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="font-semibold uppercase tracking-wider">ML Archetype</span>
            <PieChart className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-lg font-bold text-white truncate mt-0.5">
            {profile.cluster_name}
          </div>
          <div className="flex items-center gap-1 mt-2 text-[11px] text-slate-400">
            <span>Essential spend:</span>
            <span className="text-slate-200 font-semibold">
              {(profile.essential_spend_ratio * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* 3. SINGLE BEST ACTION CARD (The Hero of Sub-Problem 1 & 2) */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-700/60 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-lg bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 text-xs font-bold tracking-wider uppercase flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Proactive Single Best Action</span>
            </span>
            <span className="text-xs text-slate-400 hidden sm:inline">
              (Never multiple spam popups)
            </span>
          </div>

          <button
            onClick={() => setShowHindi(!showHindi)}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-cyan-400 transition-colors bg-slate-900/60 px-3 py-1 rounded-lg border border-slate-800"
          >
            <Languages className="w-3.5 h-3.5 text-cyan-400" />
            <span>{showHindi ? "Viewing: Hindi / Hinglish" : "Viewing: English"}</span>
          </button>
        </div>

        <div className="mt-5 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: The Product Proposition & Vernacular Pitch */}
          <div className="lg:col-span-2 space-y-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                {action.display_title}
              </h2>
              <p className="text-sm text-slate-300 mt-1">
                {action.message_en}
              </p>
            </div>

            {/* Vernacular Nudge Quote Box */}
            <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900/90 via-slate-850 to-slate-900 border border-slate-800 relative">
              <div className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 mb-1 flex items-center gap-1.5">
                <span>💬 Vernacular Touchpoint</span>
              </div>
              <p className="text-sm sm:text-base font-medium text-slate-100 leading-relaxed italic">
                "{showHindi ? action.vernacular_message_hi : action.message_en}"
              </p>
            </div>

            {/* Primary Action Button */}
            <div className="pt-2 flex flex-wrap items-center gap-3">
              <button
                onClick={onOpenChat}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
              >
                <span>{veto.veto_triggered ? "Request Zero-Penalty Relief" : "Apply with Vernacular Assistant"}</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="text-xs text-slate-400 flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                <span>Zero hidden fees • CIBIL standing preserved</span>
              </div>
            </div>
          </div>

          {/* Right Col: Explainability by Construction (SHAP Drivers) */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/90 flex flex-col justify-between">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center justify-between">
                <span>🧠 SHAP Decision Drivers</span>
                <span className="text-[10px] text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20">
                  Feature Weight
                </span>
              </div>

              <div className="space-y-2.5">
                {action.shap_reasons && action.shap_reasons.length > 0 ? (
                  action.shap_reasons.map((reason, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-slate-850/80 border border-slate-800 text-xs text-slate-200 flex items-start gap-2"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                      <span className="leading-snug">{reason}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-slate-400 italic">
                    Feature vector matches standard behavioral archetype.
                  </div>
                )}
              </div>
            </div>

            {/* Blocked Products notice if any */}
            {veto.blocked_products && veto.blocked_products.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-800">
                <div className="text-[10px] font-bold uppercase tracking-wider text-rose-400 mb-1">
                  🚫 Blocked Credit Products (Hard Veto Floor):
                </div>
                <div className="flex flex-wrap gap-1">
                  {veto.blocked_products.map((p, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 font-mono"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
