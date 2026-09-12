"use client";

import React from "react";
import { Sparkles, AlertOctagon, Languages, CheckCircle2 } from "lucide-react";

interface ScenarioSelectorProps {
  selectedId: string;
  onSelect: (id: string) => void;
}

const SCENARIOS = [
  {
    id: "CUST_PRIYA",
    name: "Priya Sharma",
    subtitle: "Young Earner • Inflow Jump",
    badge: "Salary Jump +67%",
    badgeColor: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    outcome: "SIP Wealth Builder Recommended",
    icon: Sparkles,
  },
  {
    id: "CUST_AMIT",
    name: "Amit Patel",
    subtitle: "Financially Stressed • Medical Outflows",
    badge: "VETO TRIGGERED",
    badgeColor: "bg-rose-500/15 text-rose-400 border-rose-500/30 font-bold",
    outcome: "Credit Halted • Zero-Penalty Relief",
    icon: AlertOctagon,
  },
  {
    id: "CUST_SUNITA",
    name: "Sunita Devi",
    subtitle: "Artisan • Hindi Conversational",
    badge: "Verhoeff KYC Detour",
    badgeColor: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    outcome: "Micro-Credit • RBI Grounded RAG",
    icon: Languages,
  },
  {
    id: "CUST_RAMESH",
    name: "Ramesh Kumar",
    subtitle: "Stable Professional • 36m Vintage",
    badge: "DTI 38% Approved",
    badgeColor: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
    outcome: "Instant Digital Personal Loan",
    icon: CheckCircle2,
  },
];

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({ selectedId, onSelect }) => {
  return (
    <div className="w-full bg-[#0B111E]/90 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-md">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-2 mb-3">
        <div>
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <span>🎯 Canonical Judge Scenarios</span>
            <span className="text-[11px] text-slate-400 font-normal normal-case">
              (Click to immediately stress-test the decisioning engine)
            </span>
          </h2>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {SCENARIOS.map((sc) => {
          const Icon = sc.icon;
          const isSelected = selectedId === sc.id;

          return (
            <button
              key={sc.id}
              onClick={() => onSelect(sc.id)}
              className={`text-left p-3 rounded-xl border transition-all relative overflow-hidden ${
                isSelected
                  ? "bg-slate-800/90 border-cyan-500/60 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500/50"
                  : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-850"
              }`}
            >
              {isSelected && (
                <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500" />
              )}
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                      isSelected
                        ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-white leading-tight">{sc.name}</div>
                    <div className="text-[11px] text-slate-400">{sc.subtitle}</div>
                  </div>
                </div>
              </div>

              <div className="mt-2.5 flex items-center justify-between gap-2">
                <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-md border ${sc.badgeColor}`}>
                  {sc.badge}
                </span>
                <span className="text-[11px] font-medium text-slate-300 truncate">
                  {sc.outcome}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
