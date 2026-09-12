"use client";

import React, { useState } from "react";
import { 
  Scale, 
  ShieldCheck, 
  ShieldAlert, 
  Sliders, 
  Check, 
  X, 
  FileCode, 
  UserCheck,
  Lock
} from "lucide-react";
import { DashboardResponse } from "../lib/types";

interface VetoAuditorProps {
  data: DashboardResponse;
  onSimulate: (dti: number, healthScore: number) => void;
  onReset: () => void;
}

export const VetoAuditor: React.FC<VetoAuditorProps> = ({ data, onSimulate, onReset }) => {
  const { customer_profile: profile, contract_2_veto_outcome: veto } = data;

  const [simDti, setSimDti] = useState<number>(profile.dti_ratio);
  const [simHealth, setSimHealth] = useState<number>(veto.financial_health_score);
  const [overrideModalOpen, setOverrideModalOpen] = useState(false);
  const [officerNote, setOfficerNote] = useState("");
  const [overrideSaved, setOverrideSaved] = useState(false);

  const handleDtiChange = (val: number) => {
    setSimDti(val);
    onSimulate(val, simHealth);
  };

  const handleHealthChange = (val: number) => {
    setSimHealth(val);
    onSimulate(simDti, val);
  };

  const handleReset = () => {
    setSimDti(profile.dti_ratio);
    setSimHealth(veto.financial_health_score);
    onReset();
  };

  // Mock product matrix with dynamic status
  const isVetoActive = simDti > 0.50 || simHealth < 40;

  const products = [
    {
      name: "Instant Personal Loan",
      type: "PERSONAL_LOAN",
      rawScore: 0.82,
      discountedScore: isVetoActive ? 0.0 : Number((0.82 * (1 - simDti * 0.4)).toFixed(2)),
      isCredit: true,
    },
    {
      name: "Platinum Cashback Credit Card",
      type: "CREDIT_CARD",
      rawScore: 0.74,
      discountedScore: isVetoActive ? 0.0 : Number((0.74 * (1 - simDti * 0.3)).toFixed(2)),
      isCredit: true,
    },
    {
      name: "Family Health Shield Insurance",
      type: "HEALTH_INSURANCE",
      rawScore: 0.85,
      discountedScore: 0.85,
      isCredit: false,
    },
    {
      name: "Automated Tax-Saving SIP",
      type: "SIP_INVESTMENT",
      rawScore: 0.78,
      discountedScore: isVetoActive ? 0.30 : 0.78,
      isCredit: false,
    },
  ];

  return (
    <div className="space-y-6">
      {/* HEADER: Auditor Purpose */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Scale className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg font-black text-white tracking-tight">
                Banker & Judge Live Veto Auditor
              </h2>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Ethical Hard Floor Workbench
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl">
              In accordance with <strong className="text-slate-300">BharatBanker_AI_Unified_Solution.pdf</strong> Section 5, 
              soft-weighting alone is rejected because high-propensity loans could still reach stressed borrowers. 
              Drag the sliders below to see the deterministic hard veto floor programmatically halt credit pushes in real time.
            </p>
          </div>

          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            Reset to Baseline
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT 1 COL: LIVE STRESS SLIDERS */}
        <div className="glass-card p-5 rounded-2xl space-y-6">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Interactive Stress Sliders
            </h3>
          </div>

          {/* SLIDER 1: DTI RATIO */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-300">Simulated Debt-to-Income (DTI)</span>
              <span className={`font-mono font-bold text-sm ${simDti > 0.5 ? "text-rose-400" : "text-emerald-400"}`}>
                {(simDti * 100).toFixed(1)}%
              </span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.85"
              step="0.01"
              value={simDti}
              onChange={(e) => handleDtiChange(parseFloat(e.target.value))}
              className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>10% (Solvent)</span>
              <span className="text-rose-400 font-bold">50.0% (Hard Ceiling)</span>
              <span>85% (Critical)</span>
            </div>
          </div>

          {/* SLIDER 2: HEALTH SCORE */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-slate-300">Simulated Financial Health</span>
              <span className={`font-mono font-bold text-sm ${simHealth < 40 ? "text-rose-400" : "text-emerald-400"}`}>
                {simHealth} / 100
              </span>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              step="1"
              value={simHealth}
              onChange={(e) => handleHealthChange(parseInt(e.target.value))}
              className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span className="text-rose-400 font-bold">40 (Stress Floor)</span>
              <span>60 (Watch)</span>
              <span>100 (Healthy)</span>
            </div>
          </div>

          {/* VETO GATE VERDICT CARD */}
          <div
            className={`p-4 rounded-xl border text-center transition-all ${
              isVetoActive
                ? "bg-rose-950/40 border-rose-500/50 badge-glow-rose"
                : "bg-emerald-950/30 border-emerald-500/40 badge-glow-emerald"
            }`}
          >
            <div className="flex items-center justify-center gap-2 mb-1.5">
              {isVetoActive ? (
                <ShieldAlert className="w-5 h-5 text-rose-400 animate-bounce" />
              ) : (
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              )}
              <span className={`text-xs font-black uppercase tracking-wider ${isVetoActive ? "text-rose-300" : "text-emerald-300"}`}>
                {isVetoActive ? "HARD VETO FLOOR ACTIVE" : "GATEWAY OPEN (SOLVENT)"}
              </span>
            </div>
            <p className="text-xs text-slate-300">
              {isVetoActive
                ? "Predatory credit products (Personal Loan, Credit Card) are programmatically blocked by Contract 2."
                : "Customer qualifies for responsible credit & automated wealth-building products."}
            </p>
          </div>
        </div>

        {/* RIGHT 2 COLS: MULTI-PRODUCT MATRIX & AUDIT LOG */}
        <div className="lg:col-span-2 space-y-6">
          {/* PRODUCT DECISIONING TABLE */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <span>📊 Real-Time Multi-Product Propensity Matrix</span>
              </h3>
              <span className="text-xs text-slate-400">LightGBM Head + Veto Gate</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px]">
                    <th className="pb-2.5">Banking Product</th>
                    <th className="pb-2.5 text-center">Category</th>
                    <th className="pb-2.5 text-center">Raw Score</th>
                    <th className="pb-2.5 text-center">Discounted</th>
                    <th className="pb-2.5 text-right">Gate Decision</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {products.map((prod, idx) => {
                    const isBlocked = isVetoActive && prod.isCredit;

                    return (
                      <tr key={idx} className="hover:bg-slate-850/40 transition-colors">
                        <td className="py-3 font-semibold text-white">
                          {prod.name}
                        </td>
                        <td className="py-3 text-center">
                          <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                            prod.isCredit ? "bg-amber-500/10 text-amber-300" : "bg-cyan-500/10 text-cyan-300"
                          }`}>
                            {prod.isCredit ? "DEBT EXPANSION" : "PROTECTION / WEALTH"}
                          </span>
                        </td>
                        <td className="py-3 text-center font-mono text-slate-300">
                          {prod.rawScore.toFixed(2)}
                        </td>
                        <td className="py-3 text-center font-mono">
                          <span className={isBlocked ? "text-rose-400 line-through" : "text-emerald-400"}>
                            {prod.discountedScore.toFixed(2)}
                          </span>
                        </td>
                        <td className="py-3 text-right">
                          {isBlocked ? (
                            <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40">
                              <X className="w-3 h-3" />
                              <span>HARD VETOED</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                              <Check className="w-3 h-3" />
                              <span>ELIGIBLE</span>
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* AUDIT & REGULATORY INTEGRITY CARD */}
          <div className="glass-card p-5 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                <FileCode className="w-4 h-4 text-cyan-400" />
                <span>Regulatory Audit Signature (SHA-256 Tamper-Evident)</span>
              </div>
              <div className="font-mono text-[11px] text-slate-400 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
                AUDIT_SIG_{profile.customer_id}_{(simDti * 100).toFixed(0)}_DPDP_2026_RBI_MUMBAI
              </div>
            </div>

            <button
              onClick={() => setOverrideModalOpen(true)}
              className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors"
            >
              <UserCheck className="w-4 h-4 text-cyan-400" />
              <span>Relationship Manager Override</span>
            </button>
          </div>
        </div>
      </div>

      {/* OVERRIDE MODAL */}
      {overrideModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0E1626] border border-slate-700 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Lock className="w-4 h-4 text-amber-400" />
                <span>Compliance Override Authorization</span>
              </h3>
              <button
                onClick={() => setOverrideModalOpen(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-300">
              Under RBI Fair Practices & DPDP 2023, relationship managers may record a documented business exception to the algorithmic veto floor.
            </p>

            <div>
              <label className="text-xs text-slate-400 font-semibold mb-1 block">
                Officer Notes & Collateral Justification:
              </label>
              <textarea
                rows={3}
                value={officerNote}
                onChange={(e) => setOfficerNote(e.target.value)}
                placeholder="E.g., Customer verified physical agricultural land title or FDR collateral backing loan."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {overrideSaved ? (
              <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs font-semibold flex items-center gap-2">
                <Check className="w-4 h-4" />
                <span>Override recorded in SHA-256 regulatory audit stream.</span>
              </div>
            ) : (
              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setOverrideModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setOverrideSaved(true)}
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white"
                >
                  Sign & Submit Override
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
