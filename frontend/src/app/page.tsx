"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { ScenarioSelector } from "../components/ScenarioSelector";
import { CustomerPortal } from "../components/CustomerPortal";
import { VetoAuditor } from "../components/VetoAuditor";
import { VernacularChat } from "../components/VernacularChat";
import { SecurityVault } from "../components/SecurityVault";
import { fetchCustomerDashboard, CANONICAL_PRESETS } from "../lib/api";
import { DashboardResponse } from "../lib/types";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"customer" | "auditor" | "chat" | "security">("customer");
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>("CUST_PRIYA");
  const [dashboardData, setDashboardData] = useState<DashboardResponse>(CANONICAL_PRESETS.CUST_PRIYA);
  const [loading, setLoading] = useState<boolean>(false);

  // Load customer data whenever selected customer changes
  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchCustomerDashboard(selectedCustomerId);
        setDashboardData(data);
      } catch (err) {
        console.warn("Using preset data for", selectedCustomerId, err);
        setDashboardData(CANONICAL_PRESETS[selectedCustomerId] || CANONICAL_PRESETS.CUST_PRIYA);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedCustomerId]);

  const handleSimulate = async (dti: number, healthScore: number) => {
    const simulated = await fetchCustomerDashboard(selectedCustomerId, dti, healthScore);
    setDashboardData(simulated);
  };

  const handleReset = async () => {
    const fresh = await fetchCustomerDashboard(selectedCustomerId);
    setDashboardData(fresh);
  };

  return (
    <main className="min-h-screen bg-[#070B14] flex flex-col selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        {/* Canonical Scenarios Selector (Always accessible at the top) */}
        <ScenarioSelector
          selectedId={selectedCustomerId}
          onSelect={(id) => setSelectedCustomerId(id)}
        />

        {/* Tab Views */}
        {loading ? (
          <div className="p-12 text-center text-slate-400 glass-card rounded-2xl flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
            <span className="text-xs font-semibold tracking-wider uppercase text-cyan-400">
              Evaluating Feature Pipeline & Ethical Veto Floor...
            </span>
          </div>
        ) : (
          <>
            {activeTab === "customer" && (
              <CustomerPortal
                data={dashboardData}
                onOpenChat={() => setActiveTab("chat")}
              />
            )}

            {activeTab === "auditor" && (
              <VetoAuditor
                data={dashboardData}
                onSimulate={handleSimulate}
                onReset={handleReset}
              />
            )}

            {activeTab === "chat" && <VernacularChat />}

            {activeTab === "security" && <SecurityVault />}
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#05080E] py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            BharatBanker AI • Theme: Digital Transformation in Lending • Hackathon Submission 2026
          </span>
          <div className="flex items-center gap-4 text-[11px]">
            <span className="text-emerald-400">RBI Guidelines 2022 Compliant</span>
            <span className="text-indigo-400">DPDP Act 2023 Audited</span>
            <span className="text-cyan-400">Zero-Hallucination RAG</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
