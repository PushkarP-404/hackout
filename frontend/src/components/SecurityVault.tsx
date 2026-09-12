"use client";

import React, { useState } from "react";
import { 
  ShieldCheck, 
  Lock, 
  MapPin, 
  KeyRound, 
  Database, 
  EyeOff, 
  Check, 
  Layers,
  Server,
  Fingerprint
} from "lucide-react";

export const SecurityVault: React.FC = () => {
  const [consentTier, setConsentTier] = useState<number>(2);
  const [testAadhaar, setTestAadhaar] = useState("");
  const [testPan, setTestPan] = useState("");

  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <Lock className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-black text-white tracking-tight">
            DPDP Act 2023 & RBI Security Architecture Vault
          </h2>
          <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
            5 Defense-in-Depth Layers
          </span>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          Compliant with mandatory security requirements in <strong className="text-slate-300">Security portion of the program.docx</strong>. 
          Handles Insecure Direct Object Reference (IDOR) prevention, Verhoeff Aadhaar data minimization, SlowAPI rate limiting, and RBI Mumbai data residency.
        </p>
      </div>

      {/* 5 SECURITY LAYERS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Layer 1 */}
        <div className="glass-card p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Layer 1 • Network
            </span>
            <Server className="w-4 h-4 text-cyan-400" />
          </div>
          <h3 className="text-sm font-bold text-white">VPC & RBI Data Residency</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            All database and model endpoints reside strictly within <strong className="text-cyan-300">AWS ap-south-1 (Mumbai)</strong>. 
            Direct internet access is blocked via private subnets and Cloudflare WAF rate-limiting.
          </p>
          <div className="text-[11px] font-mono text-emerald-400 bg-slate-900/80 p-2 rounded border border-slate-800 flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5" />
            <span>Residency: IN-MUMBAI-ZONE-1</span>
          </div>
        </div>

        {/* Layer 2 */}
        <div className="glass-card p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Layer 2 • Encryption
            </span>
            <KeyRound className="w-4 h-4 text-indigo-400" />
          </div>
          <h3 className="text-sm font-bold text-white">TLS 1.3 & SHA-256 Audit Trail</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            All transaction streams and candidate scores are hashed with SHA-256 digital signatures to generate tamper-evident logs for RBI regulatory inspectors.
          </p>
          <div className="text-[11px] font-mono text-indigo-300 bg-slate-900/80 p-2 rounded border border-slate-800 flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5" />
            <span>Cipher: AES-256-GCM / SHA-256</span>
          </div>
        </div>

        {/* Layer 3 */}
        <div className="glass-card p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Layer 3 • Zero Trust
            </span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <h3 className="text-sm font-bold text-white">IDOR Prevention Middleware</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Every object-level customer dashboard request programmatically verifies tenant ownership (<code className="text-emerald-300">auth_user == target_customer</code>), completely preventing horizontal privilege escalation.
          </p>
          <div className="text-[11px] font-mono text-emerald-400 bg-slate-900/80 p-2 rounded border border-slate-800 flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5" />
            <span>IDOR Barrier: ACTIVE (HTTP 403)</span>
          </div>
        </div>

        {/* Layer 4 */}
        <div className="glass-card p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
              Layer 4 • Minimization
            </span>
            <EyeOff className="w-4 h-4 text-rose-400" />
          </div>
          <h3 className="text-sm font-bold text-white">Verhoeff Aadhaar Masking</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Full 12-digit Aadhaar numbers are rejected by regex. Only the last 4 digits are accepted and mathematically verified using the <strong className="text-rose-300">Dihedral Group D5</strong> Verhoeff checksum.
          </p>
          <div className="text-[11px] font-mono text-rose-300 bg-slate-900/80 p-2 rounded border border-slate-800 flex items-center gap-1.5">
            <Check className="w-3.5 h-3.5" />
            <span>Storage: Masked XXXX-XXXX-Last4</span>
          </div>
        </div>

        {/* Layer 5 */}
        <div className="glass-card p-5 rounded-xl space-y-3 md:col-span-2 lg:col-span-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Layer 5 • Governance
            </span>
            <Layers className="w-4 h-4 text-amber-400" />
          </div>
          <h3 className="text-sm font-bold text-white">DPDP Act 2023 Tiered Consent Manager</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            To prevent proxy discrimination and adhere to the DPDP Act purpose-limitation doctrine, data is strictly segmented into 3 explicit consent tiers:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
            <button
              onClick={() => setConsentTier(0)}
              className={`p-3 rounded-lg border text-left transition-all ${
                consentTier === 0
                  ? "bg-cyan-950/40 border-cyan-500/60 ring-1 ring-cyan-500/40"
                  : "bg-slate-900/50 border-slate-800"
              }`}
            >
              <div className="text-xs font-bold text-white">Tier 0: Implicit</div>
              <div className="text-[11px] text-slate-400 mt-1">Salary credits & account vintage. Required for core banking.</div>
            </button>

            <button
              onClick={() => setConsentTier(1)}
              className={`p-3 rounded-lg border text-left transition-all ${
                consentTier === 1
                  ? "bg-cyan-950/40 border-cyan-500/60 ring-1 ring-cyan-500/40"
                  : "bg-slate-900/50 border-slate-800"
              }`}
            >
              <div className="text-xs font-bold text-white">Tier 1: Behavioral</div>
              <div className="text-[11px] text-slate-400 mt-1">Spend mix & savings velocity. Used for K-Means clustering.</div>
            </button>

            <button
              onClick={() => setConsentTier(2)}
              className={`p-3 rounded-lg border text-left transition-all ${
                consentTier === 2
                  ? "bg-cyan-950/40 border-cyan-500/60 ring-1 ring-cyan-500/40"
                  : "bg-slate-900/50 border-slate-800"
              }`}
            >
              <div className="text-xs font-bold text-white">Tier 2: Explicit</div>
              <div className="text-[11px] text-slate-400 mt-1">Life-stage events (marriage, home). Investment & insurance only.</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
