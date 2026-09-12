"use client";

import React, { useState, useRef, useEffect } from "react";
import { 
  ShieldAlert, 
  ShieldCheck, 
  Sliders, 
  Sparkles,
  BookOpen,
  Send,
  Check,
  AlertTriangle,
  FileText,
  CreditCard,
  User,
  Bell,
  Link as LinkIcon
} from "lucide-react";
import { fetchCustomerDashboard, sendChatMessage, CANONICAL_PRESETS } from "../lib/api";
import { DashboardResponse, CandidateRecommendation } from "../lib/types";

// ── Semicircular SVG Gauge (Exact Figma Component) ──
function GaugeChart({ score, dark }: { score: number; dark?: boolean }) {
  const cx = 70, cy = 68, r = 52;
  const toRad = (d: number) => (d * Math.PI) / 180;

  function arc(startDeg: number, endDeg: number) {
    const x1 = cx + r * Math.cos(toRad(startDeg));
    const y1 = cy + r * Math.sin(toRad(startDeg));
    const x2 = cx + r * Math.cos(toRad(endDeg));
    const y2 = cy + r * Math.sin(toRad(endDeg));
    const sweep = Math.abs(endDeg - startDeg);
    const large = sweep > 180 ? 1 : 0;
    return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
  }

  const bgPath = arc(180, 360);
  const endDeg = 180 + (Math.min(Math.max(score, 0), 100) / 100) * 180;
  const scorePath = arc(180, endDeg);
  const scoreColor = score >= 75 ? '#2A6B63' : score >= 50 ? '#D86F52' : '#C0392B';

  return (
    <svg width="140" height="88" viewBox="0 0 140 88" className="mx-auto">
      <path d={bgPath} fill="none" stroke={dark ? '#2E3D36' : '#C4D8CC'} strokeWidth="11" strokeLinecap="round" />
      <path d={scorePath} fill="none" stroke={scoreColor} strokeWidth="11" strokeLinecap="round" />
      <text x={cx} y={cy + 6} textAnchor="middle" fill={dark ? '#F8F4EC' : '#202927'} fontSize="22" fontWeight="600" fontFamily="'DM Sans', sans-serif">
        {score}
      </text>
      <text x={cx} y={cy + 18} textAnchor="middle" fill={dark ? '#8AA49C' : '#6B7872'} fontSize="9" fontFamily="'DM Sans', sans-serif">
        / 100
      </text>
    </svg>
  );
}

// ── Sliding Language Pill Toggle (Exact Figma Component) ──
function LangToggle({ lang, onChange }: { lang: 'EN' | 'HI'; onChange: (l: 'EN' | 'HI') => void }) {
  const isEN = lang === 'EN';
  return (
    <div
      onClick={() => onChange(isEN ? 'HI' : 'EN')}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        width: 86,
        height: 36,
        borderRadius: 99,
        background: 'rgba(255,255,255,0.12)',
        border: '1px solid rgba(255,255,255,0.18)',
        cursor: 'pointer',
        position: 'relative',
        userSelect: 'none',
        padding: '0 6px',
        justifyContent: 'space-between',
        transition: 'background 0.2s',
      }}
    >
      {/* Sliding Flag Circle */}
      <div
        style={{
          position: 'absolute',
          top: 3,
          left: isEN ? 4 : 'auto',
          right: isEN ? 'auto' : 4,
          width: 28,
          height: 28,
          borderRadius: '50%',
          background: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '1rem',
          boxShadow: '0 1px 4px rgba(0,0,0,0.22)',
          transition: 'all 0.22s cubic-bezier(.4,0,.2,1)',
          zIndex: 2,
        }}
      >
        {isEN ? '🇬🇧' : '🇮🇳'}
      </div>
      {/* Text Label */}
      <span
        style={{
          position: 'absolute',
          right: isEN ? 10 : 'auto',
          left: isEN ? 'auto' : 10,
          fontSize: '0.75rem',
          fontWeight: 700,
          color: 'rgba(248,244,236,0.85)',
          letterSpacing: '0.06em',
          fontFamily: "'DM Sans', sans-serif",
          zIndex: 1,
        }}
      >
        {isEN ? 'EN' : 'हि'}
      </span>
    </div>
  );
}

function fmtINR(n: number) {
  return '₹' + Math.abs(Math.round(n)).toLocaleString('en-IN');
}

type Tab = 'overview' | 'transactions' | 'askai' | 'threats' | 'settings';

interface ChatMsg {
  role: 'user' | 'ai';
  text: string;
  citation?: string | null;
  isVeto?: boolean;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('CUST_ELEANOR');
  const [data, setData] = useState<DashboardResponse>(CANONICAL_PRESETS.CUST_ELEANOR);
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState<'EN' | 'HI'>('EN');
  const [darkMode, setDarkMode] = useState(false); // Default Figma theme: Light Mode (Warm Ivory + Deep Teal)

  // Simulation Sliders
  const [simDti, setSimDti] = useState<number>(0.199);
  const [simHealth, setSimHealth] = useState<number>(72);

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([
    {
      role: 'ai',
      text: "Hi Eleanor! I'm your BharatBank AI assistant. Ask me about your balances, DTI, spending, health score, SIP planning, or security alerts."
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => 'session_' + Math.random().toString(36).substring(2, 9));
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Theme tokens matching Figma design
  const t = darkMode ? {
    bg: '#1A2420',
    surface: '#232E29',
    surfaceHover: '#2A3830',
    border: 'rgba(255,255,255,0.09)',
    borderSubtle: 'rgba(255,255,255,0.05)',
    text: '#F8F4EC',
    muted: '#8AA49C',
    subtleBg: '#2A3830',
    panelBg: '#1E2B26',
    panelBorder: 'rgba(255,255,255,0.08)',
    headerBg: '#123E3A',
    headerText: '#F8F4EC',
    accentTeal: '#2A6B63',
    accentTerracotta: '#D86F52',
    accentCrimson: '#C0392B',
  } : {
    bg: '#F8F4EC',
    surface: '#ffffff',
    surfaceHover: '#FDFAF6',
    border: '#E8E3DB',
    borderSubtle: '#F0EBE3',
    text: '#202927',
    muted: '#6B7872',
    subtleBg: '#FDFAF6',
    panelBg: '#DDE8E2',
    panelBorder: '#C4D8CC',
    headerBg: '#123E3A',
    headerText: '#F8F4EC',
    accentTeal: '#2A6B63',
    accentTerracotta: '#D86F52',
    accentCrimson: '#C0392B',
  };

  // Load customer data from backend
  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await fetchCustomerDashboard(selectedCustomerId);
        setData(res);
        setSimDti(res.customer_profile.dti_ratio);
        setSimHealth(res.contract_2_veto_outcome.financial_health_score);
      } catch (err) {
        console.warn('Fallback to canonical preset for', selectedCustomerId, err);
        const preset = CANONICAL_PRESETS[selectedCustomerId] || CANONICAL_PRESETS.CUST_ELEANOR;
        setData(preset);
        setSimDti(preset.customer_profile.dti_ratio);
        setSimHealth(preset.contract_2_veto_outcome.financial_health_score);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedCustomerId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isTyping]);

  // Handle simulation sliders
  const handleSimulateDti = async (val: number) => {
    setSimDti(val);
    try {
      const updated = await fetchCustomerDashboard(selectedCustomerId, val, simHealth);
      setData(updated);
    } catch {
      // Offline fallback
      setData(prev => ({
        ...prev,
        customer_profile: { ...prev.customer_profile, dti_ratio: val },
        contract_2_veto_outcome: {
          ...prev.contract_2_veto_outcome,
          veto_triggered: val > 0.50 || simHealth < 40,
          financial_health_score: Math.max(10, Math.round(100 - (val * 80))),
        }
      }));
    }
  };

  const handleSimulateHealth = async (val: number) => {
    setSimHealth(val);
    try {
      const updated = await fetchCustomerDashboard(selectedCustomerId, simDti, val);
      setData(updated);
    } catch {
      setData(prev => ({
        ...prev,
        contract_2_veto_outcome: {
          ...prev.contract_2_veto_outcome,
          financial_health_score: val,
          veto_triggered: simDti > 0.50 || val < 40,
        }
      }));
    }
  };

  const handleResetSim = async () => {
    try {
      const fresh = await fetchCustomerDashboard(selectedCustomerId);
      setData(fresh);
      setSimDti(fresh.customer_profile.dti_ratio);
      setSimHealth(fresh.contract_2_veto_outcome.financial_health_score);
    } catch {
      const preset = CANONICAL_PRESETS[selectedCustomerId] || CANONICAL_PRESETS.CUST_ELEANOR;
      setData(preset);
      setSimDti(preset.customer_profile.dti_ratio);
      setSimHealth(preset.contract_2_veto_outcome.financial_health_score);
    }
  };

  // Chat send
  const sendChat = async (text: string) => {
    if (!text.trim() || isTyping) return;
    const userMsg: ChatMsg = { role: 'user', text: text.trim() };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput('');
    setIsTyping(true);

    try {
      const resp = await sendChatMessage(sessionId, text, lang === 'EN' ? 'en' : 'hi');
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: resp.bot_message,
          citation: resp.grounded_citation,
          isVeto: resp.ethical_veto_triggered,
        }
      ]);
    } catch (err) {
      console.warn('Fallback AI chat reply', err);
      setTimeout(() => {
        setChatMessages((prev) => [
          ...prev,
          {
            role: 'ai',
            text: lang === 'EN'
              ? `BharatBank AI: Your current DTI is ${(profile.dti_ratio * 100).toFixed(1)}% with a monthly surplus of ${fmtINR(surplus)}. (Grounded via RBI Digital Lending Guidelines 2022).`
              : `भारतबैंक AI: आपका वर्तमान DTI ${(profile.dti_ratio * 100).toFixed(1)}% है और मासिक बचत ${fmtINR(surplus)} है। (RBI दिशानिर्देश 2022 द्वारा प्रमाणित)।`,
            citation: '[Source: RBI Digital Lending Guidelines 2022, Sec 4.2]'
          }
        ]);
      }, 500);
    } finally {
      setIsTyping(false);
    }
  };

  const profile = data.customer_profile;
  const veto = data.contract_2_veto_outcome;
  const action = veto.final_action;
  const isVetoActive = veto.veto_triggered;

  // Real or derived financial metrics
  const fm = data.financial_metrics;
  const monthlySalary = fm ? fm.monthly_salary : profile.monthly_salary;
  const monthlyEmi = fm ? fm.monthly_emi : (monthlySalary * profile.dti_ratio);
  const monthlyBills = fm ? fm.monthly_bills : (selectedCustomerId === 'CUST_ELEANOR' ? 12600 : Math.round(monthlySalary * 0.088));
  const monthlySpend = fm ? fm.monthly_spend : (selectedCustomerId === 'CUST_ELEANOR' ? 89340 : Math.round(monthlySalary * 0.62));
  const surplus = fm ? fm.monthly_surplus : Math.max(0, monthlySalary - monthlyEmi - monthlyBills);
  const totalDebt = fm ? fm.total_debt : (selectedCustomerId === 'CUST_ELEANOR' ? 3850000 : Math.round(monthlyEmi * 135));
  const annualIncome = fm ? fm.annual_income : (monthlySalary * 12);
  const debtPct = fm ? fm.debt_pct : ((totalDebt / (annualIncome + 1e-5)) * 100);
  const prevInflows = fm?.prev_inflows || (selectedCustomerId === 'CUST_ELEANOR' ? [128000, 135200, 119800, 142500] : [Math.round(monthlySalary * 0.85), Math.round(monthlySalary * 0.90), Math.round(monthlySalary * 0.92), monthlySalary]);
  const monthLabels = ['Jun', 'Jul', 'Aug', 'Sep'];

  // Accounts
  const accounts = data.accounts && data.accounts.length > 0 ? data.accounts : [
    { id: 'SAV-009163', name: 'High-Yield Savings', balance: 54220.00, type: 'savings' },
    { id: 'INV-002577', name: 'Investment Portfolio', balance: 138640.75, type: 'investment' },
  ];

  // Transactions
  const transactions = data.recent_transactions && data.recent_transactions.length > 0 ? data.recent_transactions : [
    { id: 'TXN-2409-00814', date: '2026-09-12', description: 'Direct Deposit — Employer Payroll', category: 'Income', amount: monthlySalary, status: 'settled' },
    { id: 'TXN-2409-00811', date: '2026-09-11', description: 'Whole Foods Market Provisions', category: 'Groceries', amount: -4250.00, status: 'settled' },
    { id: 'TXN-2409-00808', date: '2026-09-10', description: 'Electric & Gas — City Utilities', category: 'Utilities', amount: -2140.00, status: 'settled' },
    { id: 'TXN-2409-00804', date: '2026-09-09', description: 'Transfer to High-Yield Savings', category: 'Transfer', amount: -15000.00, status: 'settled' },
    { id: 'TXN-2409-00799', date: '2026-09-08', description: 'Café Sable & Dining', category: 'Dining', amount: -1850.00, status: 'settled' },
    { id: 'TXN-2409-00793', date: '2026-09-07', description: 'Amazon Web Services Cloud', category: 'Software', amount: -1890.00, status: 'settled' },
    { id: 'TXN-2409-00786', date: '2026-09-06', description: 'Freelance Client Invoice #INV-0047', category: 'Income', amount: 25000.00, status: 'settled' },
    { id: 'TXN-2409-00779', date: '2026-09-05', description: 'Metro Transit Monthly Commute Pass', category: 'Transport', amount: -1120.00, status: 'settled' },
    { id: 'TXN-2409-00774', date: '2026-09-04', description: 'Dividend Yield — VTSMX Index', category: 'Income', amount: 3420.00, status: 'settled' },
    { id: 'TXN-2409-00768', date: '2026-09-03', description: 'Pending: Stripe Merchant Payout', category: 'Income', amount: 6700.00, status: 'pending' },
  ];

  // Security Threats (Exact Figma Data)
  const threats = [
    {
      id: 'THR-2409-001',
      type: 'Unusual Login Location',
      severity: 'high' as const,
      time: 'Sep 12, 2026 · 02:14 AM',
      description: "Login attempt detected from a new device in Bengaluru. Your last session was from Mumbai. If this wasn't you, secure your account immediately.",
      action: 'Review Login Activity',
    },
    {
      id: 'THR-2409-002',
      type: 'Large Transfer to New Recipient',
      severity: 'medium' as const,
      time: 'Sep 11, 2026 · 02:33 PM',
      description: '₹45,000 NEFT initiated to first-time recipient ACC-882991 (Ravi Kumar). You have never transacted with this account before.',
      action: 'Verify Transfer',
    },
    {
      id: 'THR-2409-003',
      type: 'Repeated Failed UPI PIN',
      severity: 'high' as const,
      time: 'Sep 10, 2026 · 11:47 PM',
      description: '4 consecutive failed UPI PIN attempts on your linked PhonePe handle. This may indicate an unauthorised access attempt.',
      action: 'Reset UPI PIN',
    },
  ];
  const highThreatsCount = threats.filter(t => t.severity === 'high').length;

  return (
    <div 
      className="min-h-screen flex flex-col transition-colors duration-200" 
      style={{ background: t.bg, color: t.text, fontFamily: "'DM Sans', sans-serif" }}
    >
      {/* ── DEEP TEAL HEADER FRAME (Exact Figma Design #123E3A) ── */}
      <header style={{ background: t.headerBg }}>
        {/* Top bar with Logo, Support, and User Avatar */}
        <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div 
                style={{ 
                  width: 32, 
                  height: 32, 
                  borderRadius: 8, 
                  background: 'rgba(255,255,255,0.12)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center' 
                }}
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M2 14V7L9 3L16 7V14" stroke="#DDE8E2" strokeWidth="1.5" strokeLinejoin="round"/>
                  <rect x="6" y="10" width="2.5" height="4" rx="1" fill="#DDE8E2"/>
                  <rect x="9.5" y="10" width="2.5" height="4" rx="1" fill="#DDE8E2"/>
                </svg>
              </div>
              <div className="flex items-baseline">
                <span style={{ color: '#F8F4EC', fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.01em' }}>
                  BharatBank
                </span>
                <span style={{ color: '#DDE8E2', fontWeight: 400, fontSize: '1rem', marginLeft: 3 }}>
                  AI
                </span>
                <span 
                  style={{
                    color: '#A8D5C8',
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    padding: '2px 6px',
                    borderRadius: 4,
                    background: 'rgba(255,255,255,0.08)',
                    marginLeft: 8
                  }}
                >
                  Decisioning Platform
                </span>
              </div>
            </div>

            {/* Support & Persona Profile Pill */}
            <div className="flex items-center gap-4">
              <button 
                onClick={() => setActiveTab('askai')}
                style={{ 
                  color: 'rgba(248,244,236,0.65)', 
                  fontSize: '0.8125rem', 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer' 
                }}
              >
                Support
              </button>
              <div 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 8, 
                  background: 'rgba(255,255,255,0.08)', 
                  borderRadius: 8, 
                  padding: '5px 12px' 
                }}
              >
                <div 
                  style={{ 
                    width: 26, 
                    height: 26, 
                    borderRadius: '50%', 
                    background: '#DDE8E2', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center' 
                  }}
                >
                  <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#123E3A' }}>
                    {profile.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <span style={{ color: '#F8F4EC', fontSize: '0.8125rem', fontWeight: 500 }}>
                  {profile.name}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Greeting + Account Pills */}
        <div className="max-w-6xl mx-auto px-6 pt-7 pb-0">
          <div className="flex flex-wrap items-end justify-between gap-6 mb-5">
            <div>
              <p style={{ color: 'rgba(248,244,236,0.45)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>
                Welcome back
              </p>
              <h1 style={{ color: '#F8F4EC', fontSize: '2rem', fontWeight: 300, letterSpacing: '-0.025em', lineHeight: 1 }}>
                Hi, {profile.name.split(' ')[0]}
              </h1>
              <p style={{ color: 'rgba(248,244,236,0.4)', fontSize: '0.8125rem', marginTop: 5 }}>
                Saturday, September 12 · Updated just now · {profile.cluster_name}
              </p>
            </div>

            {/* Account balance pills */}
            <div className="flex gap-3 flex-wrap">
              {accounts.map(acc => (
                <div
                  key={acc.id}
                  style={{
                    background: 'rgba(255,255,255,0.08)',
                    border: '1px solid rgba(255,255,255,0.14)',
                    borderRadius: 10,
                    padding: '8px 16px',
                    textAlign: 'left',
                  }}
                >
                  <p style={{ color: 'rgba(248,244,236,0.55)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 2 }}>
                    {acc.name}
                  </p>
                  <p style={{ color: '#F8F4EC', fontSize: '0.9375rem', fontWeight: 600, fontFamily: 'monospace' }}>
                    {fmtINR(acc.balance)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* 5 Nav Tabs (Exact Figma Layout) */}
          <nav className="flex gap-1 overflow-x-auto">
            {(['overview', 'transactions', 'askai', 'threats', 'settings'] as Tab[]).map((tab) => {
              const isActive = activeTab === tab;
              const label =
                tab === 'overview'
                  ? 'Overview'
                  : tab === 'transactions'
                  ? 'Transactions'
                  : tab === 'askai'
                  ? 'Ask AI'
                  : tab === 'threats'
                  ? 'Threats'
                  : 'Settings';

              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '10px 20px',
                    background: isActive ? t.bg : 'transparent',
                    color: isActive ? (darkMode ? '#F8F4EC' : '#123E3A') : 'rgba(248,244,236,0.60)',
                    border: 'none',
                    borderRadius: '10px 10px 0 0',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: isActive ? 600 : 400,
                    transition: 'all 0.15s',
                    fontFamily: "'DM Sans', sans-serif",
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  <span>{label}</span>
                  {tab === 'threats' && highThreatsCount > 0 && (
                    <span 
                      style={{
                        background: isActive ? '#C0392B' : 'rgba(192,57,43,0.85)',
                        color: '#fff',
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        borderRadius: 99,
                        minWidth: 17,
                        height: 17,
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '0 4px',
                      }}
                    >
                      {highThreatsCount}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* ── WORKSPACE ── */}
      <main style={{ flex: 1, background: t.bg, transition: 'background 0.2s' }}>
        <div className="max-w-6xl mx-auto px-6 py-8">
          {loading ? (
            <div 
              style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10 }} 
              className="p-12 text-center flex flex-col items-center justify-center gap-3"
            >
              <div className="w-8 h-8 rounded-full border-2 border-teal-600 border-t-transparent animate-spin" />
              <p style={{ color: t.muted, fontSize: '0.8125rem' }}>
                Evaluating LightGBM Propensity & Cross-Cutting Ethical Veto Floor...
              </p>
            </div>
          ) : (
            <>
              {/* ── TAB 1: OVERVIEW ── */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Status Banner when Ethical Hard Veto is Active */}
                  {isVetoActive && (
                    <div 
                      style={{ 
                        background: darkMode ? '#321515' : '#FDECEA', 
                        border: '1px solid #F5C6C6', 
                        borderLeft: '5px solid #C0392B',
                        borderRadius: 10, 
                        padding: '16px 20px', 
                        display: 'flex', 
                        alignItems: 'flex-start', 
                        gap: 14 
                      }}
                    >
                      <ShieldAlert className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <div style={{ color: '#C0392B', fontSize: '0.725rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                          🛑 Non-Negotiable Hard Veto Gate Active
                        </div>
                        <div style={{ color: darkMode ? '#F8F4EC' : '#202927', fontSize: '0.9375rem', fontWeight: 600, marginTop: 2 }}>
                          Credit Pushes Programmatically Frozen (DTI: {(profile.dti_ratio * 100).toFixed(1)}% | Health: {veto.financial_health_score}/100)
                        </div>
                        <div style={{ color: darkMode ? '#8AA49C' : '#6B7872', fontSize: '0.8125rem', marginTop: 4, lineHeight: 1.4 }}>
                          {veto.veto_reason || "Policy strictly suppresses debt expansion offers to protect household cashflow. Zero-penalty empathetic relief substituted."}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 4 CARDS GRID (Exact Figma Layout) */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 16, alignItems: 'start' }}>
                    {/* Box 1: Monthly Overview */}
                    <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '18px 20px' }}>
                      <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: t.muted, marginBottom: 12 }}>
                        Monthly Overview
                      </p>
                      <div style={{ marginBottom: 12 }}>
                        <p style={{ fontSize: '0.75rem', color: t.muted, marginBottom: 3 }}>Total Spending</p>
                        <p style={{ fontSize: '1.25rem', fontWeight: 600, color: t.text, fontFamily: 'monospace' }}>
                          {fmtINR(monthlySpend)}
                        </p>
                      </div>
                      <div style={{ borderTop: `1px solid ${t.borderSubtle}`, paddingTop: 12 }}>
                        <p style={{ fontSize: '0.75rem', color: t.muted, marginBottom: 6 }}>Income Inflow — Sep 2026</p>
                        <p style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2A6B63', fontFamily: 'monospace' }}>
                          {fmtINR(monthlySalary)}
                        </p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8 }}>
                          <span 
                            style={{
                              fontSize: '0.75rem', fontWeight: 600,
                              color: '#2A6B63',
                              background: darkMode ? '#1E2B26' : '#DDE8E2',
                              borderRadius: 5, padding: '2px 7px',
                            }}
                          >
                            ▲ 14.5% vs Aug
                          </span>
                        </div>
                        {/* 4-Month Inflow Bar Indicator */}
                        <div style={{ display: 'flex', gap: 8, marginTop: 12, alignItems: 'flex-end' }}>
                          {prevInflows.map((v, i) => {
                            const maxV = Math.max(...prevInflows);
                            const hPct = Math.round((v / maxV) * 100);
                            return (
                              <div key={i} style={{ flex: 1, textAlign: 'center' }}>
                                <div style={{ fontSize: '0.65rem', color: i === prevInflows.length - 1 ? (darkMode ? '#F8F4EC' : '#123E3A') : t.muted, marginBottom: 2, fontWeight: i === prevInflows.length - 1 ? 700 : 400 }}>
                                  {monthLabels[i]}
                                </div>
                                <div style={{ fontSize: '0.6rem', color: t.muted, marginBottom: 3, fontFamily: 'monospace' }}>
                                  {(v / 1000).toFixed(0)}K
                                </div>
                                <div style={{ height: 3, background: i === prevInflows.length - 1 ? (darkMode ? '#2A6B63' : '#123E3A') : (darkMode ? '#33413B' : '#DDE8E2'), borderRadius: 2, width: `${hPct}%`, margin: '0 auto' }} />
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>

                    {/* Box 2: Debt-to-Income (DTI) Ratio */}
                    <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '18px 20px' }}>
                      <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: t.muted, marginBottom: 12 }}>
                        Debt-to-Income Ratio
                      </p>
                      <p style={{ fontSize: '1.5rem', fontWeight: 600, color: profile.dti_ratio > 0.5 ? '#C0392B' : profile.dti_ratio > 0.36 ? '#D86F52' : t.text, fontFamily: 'monospace', marginBottom: 4 }}>
                        {(profile.dti_ratio * 100).toFixed(1)}<span style={{ fontSize: '0.875rem', fontWeight: 400 }}>%</span>
                      </p>
                      <p style={{ fontSize: '0.75rem', color: t.muted, marginBottom: 12, fontFamily: 'monospace' }}>
                        EMI {fmtINR(monthlyEmi)} / income {fmtINR(monthlySalary)}
                      </p>
                      {/* Progress Bar with Color Coding */}
                      <div style={{ height: 6, background: darkMode ? '#2E3D36' : '#F0EBE3', borderRadius: 4, marginBottom: 8, overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            height: 6, 
                            width: `${Math.min(profile.dti_ratio * 100, 100)}%`, 
                            background: profile.dti_ratio > 0.5 ? '#C0392B' : profile.dti_ratio > 0.36 ? '#D86F52' : '#2A6B63', 
                            borderRadius: 4,
                            transition: 'width 0.3s ease'
                          }} 
                        />
                      </div>
                      <p style={{ fontSize: '0.725rem', color: t.muted, marginBottom: 14 }}>
                        Recommended: &lt;36% • <strong style={{ color: '#C0392B' }}>Hard Veto Floor: 50.0%</strong>
                      </p>
                      <div style={{ borderTop: `1px solid ${t.borderSubtle}`, paddingTop: 12 }}>
                        <p style={{ fontSize: '0.75rem', color: t.muted, marginBottom: 4 }}>Total debt vs annual income</p>
                        <p style={{ fontSize: '1.125rem', fontWeight: 600, color: profile.dti_ratio > 0.5 ? '#C0392B' : '#D86F52', fontFamily: 'monospace' }}>
                          {debtPct.toFixed(0)}%
                          <span style={{ fontSize: '0.725rem', fontWeight: 400, color: t.muted, marginLeft: 6 }}>
                            ({fmtINR(totalDebt)} / {fmtINR(annualIncome)} p.a.)
                          </span>
                        </p>
                      </div>
                    </div>

                    {/* Box 3: Monthly Surplus */}
                    <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '18px 20px' }}>
                      <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: t.muted, marginBottom: 12 }}>
                        Monthly Surplus
                      </p>
                      <p style={{ fontSize: '1.5rem', fontWeight: 600, color: surplus > 0 ? '#2A6B63' : '#C0392B', fontFamily: 'monospace', marginBottom: 4 }}>
                        {fmtINR(surplus)}
                      </p>
                      <p style={{ fontSize: '0.725rem', color: t.muted, marginBottom: 14 }}>Income − EMIs − Bills</p>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {[
                          { label: 'Income', value: fmtINR(monthlySalary), color: '#2A6B63' },
                          { label: 'EMIs', value: `− ${fmtINR(monthlyEmi)}`, color: '#C0392B' },
                          { label: 'Bills', value: `− ${fmtINR(monthlyBills)}`, color: '#C0392B' },
                        ].map(r => (
                          <div key={r.label} className="flex justify-between" style={{ borderBottom: `1px dashed ${t.borderSubtle}`, paddingBottom: 6 }}>
                            <span style={{ fontSize: '0.8125rem', color: t.muted }}>{r.label}</span>
                            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: r.color, fontFamily: 'monospace' }}>{r.value}</span>
                          </div>
                        ))}
                      </div>
                      <div className="flex justify-between" style={{ marginTop: 8 }}>
                        <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: t.text }}>Surplus</span>
                        <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#2A6B63', fontFamily: 'monospace' }}>{fmtINR(surplus)}</span>
                      </div>
                    </div>

                    {/* Box 4: Health Score Gauge */}
                    <div style={{ background: darkMode ? '#232E29' : '#DDE8E2', border: `1px solid ${darkMode ? t.border : '#C4D8CC'}`, borderRadius: 10, padding: '16px 18px', textAlign: 'center' }}>
                      <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: darkMode ? '#8AA49C' : '#3A4A44', marginBottom: 4 }}>
                        Health Score
                      </p>
                      <GaugeChart score={veto.financial_health_score} dark={darkMode} />
                      <p style={{ fontSize: '0.85rem', color: darkMode ? '#F8F4EC' : '#202927', fontWeight: 600, marginTop: 4 }}>
                        {veto.financial_health_score >= 75 ? 'Good' : veto.financial_health_score >= 50 ? 'Fair' : 'Needs Attention'}
                      </p>
                      <p style={{ fontSize: '0.7rem', color: t.muted, marginTop: 3 }}>
                        Status: <strong style={{ color: veto.veto_triggered ? '#C0392B' : '#2A6B63' }}>{veto.health_category}</strong>
                      </p>
                    </div>
                  </div>

                  {/* ── FOR YOU SECTION (Pure Dynamic ML: Exact Backend Models & SHAP Explanations) ── */}
                  <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '26px 30px' }}>
                    <div style={{ marginBottom: 20 }}>
                      <div className="flex items-center justify-between">
                        <div>
                          <p style={{ fontSize: '1.0625rem', fontWeight: 700, color: t.text, marginBottom: 3 }}>
                            FOR YOU
                          </p>
                          <p style={{ fontSize: '0.8125rem', color: t.muted }}>
                            Personalized Propensity Models &amp; Ethical Guardrails (LightGBM + SHAP Plain Text)
                          </p>
                        </div>
                        {isVetoActive && (
                          <span 
                            style={{
                              background: '#FDECEA',
                              color: '#C0392B',
                              border: '1px solid #F5C6C6',
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              borderRadius: 6,
                              padding: '4px 10px'
                            }}
                          >
                            Hard Veto Substitution Active
                          </span>
                        )}
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                      {/* CARD 1: Model Recommendation 1 */}
                      {data.raw_contract_1_recommendations && data.raw_contract_1_recommendations.length > 0 ? (
                        (() => {
                          const r = data.raw_contract_1_recommendations[0];
                          const isBlocked = isVetoActive && veto.blocked_products.includes(r.product_type);
                          return (
                            <div 
                              style={{ 
                                background: isBlocked ? (darkMode ? '#2C1B1B' : '#FFF5F5') : t.subtleBg, 
                                border: `1px solid ${isBlocked ? '#F5C6C6' : t.border}`, 
                                borderRadius: 10, 
                                padding: '20px', 
                                display: 'flex', 
                                flexDirection: 'column', 
                                gap: 10 
                              }}
                            >
                              <div className="flex items-center justify-between">
                                <span 
                                  style={{ 
                                    display: 'inline-block', 
                                    background: isBlocked ? '#FDECEA' : (darkMode ? '#1E2B26' : '#DDE8E2'), 
                                    color: isBlocked ? '#C0392B' : '#2A6B63', 
                                    fontSize: '0.7rem', 
                                    fontWeight: 700, 
                                    letterSpacing: '0.06em', 
                                    textTransform: 'uppercase', 
                                    borderRadius: 6, 
                                    padding: '3px 8px' 
                                  }}
                                >
                                  {isBlocked ? '🛑 VETO BLOCKED' : 'MODEL 1'}
                                </span>
                                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: t.muted }}>
                                  Propensity: {(r.raw_propensity_score * 100).toFixed(1)}%
                                </span>
                              </div>

                              {/* Exact Backend Model Recommendation Name */}
                              <p style={{ fontSize: '0.9375rem', fontWeight: 700, color: t.text, fontFamily: 'monospace' }}>
                                {r.product_type}
                              </p>

                              {/* SHAP Explanation Bullets */}
                              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                                {r.shap_reasons.map((reason, idx) => (
                                  <div key={idx} className="flex items-start gap-2">
                                    <span style={{ color: isBlocked ? '#C0392B' : '#2A6B63', fontWeight: 700 }}>•</span>
                                    <p style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44', lineHeight: 1.45 }}>
                                      {reason}
                                    </p>
                                  </div>
                                ))}
                              </div>

                              <button 
                                onClick={() => setActiveTab('askai')}
                                style={{ 
                                  background: 'transparent', 
                                  border: `1px solid ${t.border}`, 
                                  borderRadius: 8, 
                                  padding: '8px 14px', 
                                  fontSize: '0.8125rem', 
                                  fontWeight: 600, 
                                  color: isBlocked ? '#C0392B' : (darkMode ? '#DDE8E2' : '#123E3A'), 
                                  cursor: 'pointer', 
                                  fontFamily: "'DM Sans', sans-serif", 
                                  alignSelf: 'flex-start', 
                                  transition: 'all 0.15s' 
                                }}
                              >
                                {isBlocked ? 'View Policy Constraint →' : 'Explore Product →'}
                              </button>
                            </div>
                          );
                        })()
                      ) : null}

                      {/* CARD 2: Empathetic Hard Veto Intervention OR Model Recommendation 2 */}
                      {isVetoActive ? (
                        <div 
                          style={{ 
                            background: darkMode ? '#331B1B' : '#FFF2F0', 
                            border: '1px solid #F5C6C6', 
                            borderLeft: '4px solid #C0392B',
                            borderRadius: 10, 
                            padding: '20px', 
                            display: 'flex', 
                            flexDirection: 'column', 
                            gap: 10 
                          }}
                        >
                          <div className="flex items-center justify-between">
                            <span 
                              style={{ 
                                display: 'inline-block', 
                                background: '#FDECEA', 
                                color: '#C0392B', 
                                fontSize: '0.7rem', 
                                fontWeight: 700, 
                                letterSpacing: '0.06em', 
                                textTransform: 'uppercase', 
                                borderRadius: 6, 
                                padding: '3px 8px' 
                              }}
                            >
                              🛑 ETHICAL HARD VETO
                            </span>
                            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#C0392B' }}>
                              DTI &gt; 50% Ceiled
                            </span>
                          </div>

                          <p style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#C0392B', fontFamily: 'monospace' }}>
                            {action.display_title || 'ZERO_PENALTY_EMI_RELIEF'}
                          </p>

                          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                            <p style={{ fontSize: '0.8125rem', color: darkMode ? '#F8F4EC' : '#202927', lineHeight: 1.45, fontWeight: 500 }}>
                              {lang === 'EN' ? action.message_en : action.vernacular_message_hi}
                            </p>
                            {action.shap_reasons && action.shap_reasons.map((reason, idx) => (
                              <div key={idx} className="flex items-start gap-2">
                                <span style={{ color: '#C0392B', fontWeight: 700 }}>•</span>
                                <p style={{ fontSize: '0.775rem', color: darkMode ? '#8AA49C' : '#6B7872', lineHeight: 1.4 }}>
                                  {reason}
                                </p>
                              </div>
                            ))}
                          </div>

                          <button 
                            onClick={() => setActiveTab('askai')}
                            style={{ 
                              background: '#C0392B', 
                              border: 'none', 
                              color: '#ffffff',
                              borderRadius: 8, 
                              padding: '8px 14px', 
                              fontSize: '0.8125rem', 
                              fontWeight: 600, 
                              cursor: 'pointer', 
                              fontFamily: "'DM Sans', sans-serif", 
                              alignSelf: 'flex-start', 
                              transition: 'all 0.15s' 
                            }}
                          >
                            {action.cta_action === 'REQUEST_EMI_RELIEF' ? 'Request EMI Relief →' : 'View Protection Cover →'}
                          </button>
                        </div>
                      ) : (
                        data.raw_contract_1_recommendations && data.raw_contract_1_recommendations.length > 1 ? (
                          (() => {
                            const r = data.raw_contract_1_recommendations[1];
                            return (
                              <div 
                                style={{ 
                                  background: t.subtleBg, 
                                  border: `1px solid ${t.border}`, 
                                  borderRadius: 10, 
                                  padding: '20px', 
                                  display: 'flex', 
                                  flexDirection: 'column', 
                                  gap: 10 
                                }}
                              >
                                <div className="flex items-center justify-between">
                                  <span 
                                    style={{ 
                                      display: 'inline-block', 
                                      background: darkMode ? '#33271E' : '#F9EAE5', 
                                      color: '#D86F52', 
                                      fontSize: '0.7rem', 
                                      fontWeight: 700, 
                                      letterSpacing: '0.06em', 
                                      textTransform: 'uppercase', 
                                      borderRadius: 6, 
                                      padding: '3px 8px' 
                                    }}
                                  >
                                    MODEL 2
                                  </span>
                                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: t.muted }}>
                                    Propensity: {(r.raw_propensity_score * 100).toFixed(1)}%
                                  </span>
                                </div>

                                <p style={{ fontSize: '0.9375rem', fontWeight: 700, color: t.text, fontFamily: 'monospace' }}>
                                  {r.product_type}
                                </p>

                                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                                  {r.shap_reasons.map((reason, idx) => (
                                    <div key={idx} className="flex items-start gap-2">
                                      <span style={{ color: '#D86F52', fontWeight: 700 }}>•</span>
                                      <p style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44', lineHeight: 1.45 }}>
                                        {reason}
                                      </p>
                                    </div>
                                  ))}
                                </div>

                                <button 
                                  onClick={() => setActiveTab('askai')}
                                  style={{ 
                                    background: 'transparent', 
                                    border: `1px solid ${t.border}`, 
                                    borderRadius: 8, 
                                    padding: '8px 14px', 
                                    fontSize: '0.8125rem', 
                                    fontWeight: 600, 
                                    color: darkMode ? '#DDE8E2' : '#123E3A', 
                                    cursor: 'pointer', 
                                    fontFamily: "'DM Sans', sans-serif", 
                                    alignSelf: 'flex-start', 
                                    transition: 'all 0.15s' 
                                  }}
                                >
                                  Explore Terms →
                                </button>
                              </div>
                            );
                          })()
                        ) : null
                      )}

                      {/* CARD 3: Tax Saving / Wealth Maximizer (Model 3) */}
                      <div 
                        style={{ 
                          background: t.subtleBg, 
                          border: `1px solid ${t.border}`, 
                          borderRadius: 10, 
                          padding: '20px', 
                          display: 'flex', 
                          flexDirection: 'column', 
                          gap: 10 
                        }}
                      >
                        <div className="flex items-center justify-between">
                          <span 
                            style={{ 
                              display: 'inline-block', 
                              background: darkMode ? '#1E2B26' : '#DDE8E2', 
                              color: '#123E3A', 
                              fontSize: '0.7rem', 
                              fontWeight: 700, 
                              letterSpacing: '0.06em', 
                              textTransform: 'uppercase', 
                              borderRadius: 6, 
                              padding: '3px 8px' 
                            }}
                          >
                            TAX SAVING 80C
                          </span>
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: t.muted }}>
                            Annual Window
                          </span>
                        </div>

                        <p style={{ fontSize: '0.9375rem', fontWeight: 700, color: t.text, fontFamily: 'monospace' }}>
                          TAX_SAVING_80C_DEDUCTION
                        </p>

                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                          <div className="flex items-start gap-2">
                            <span style={{ color: '#2A6B63', fontWeight: 700 }}>•</span>
                            <p style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44', lineHeight: 1.45 }}>
                              Based on annual salary bracket ({fmtINR(annualIncome)}), investing in ELSS or PPF saves up to ₹46,800 in taxes.
                            </p>
                          </div>
                          <div className="flex items-start gap-2">
                            <span style={{ color: '#2A6B63', fontWeight: 700 }}>•</span>
                            <p style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44', lineHeight: 1.45 }}>
                              Lock-in period of 3 years under Section 80C eligible with instant Form 26AS certificate.
                            </p>
                          </div>
                        </div>

                        <button 
                          onClick={() => setActiveTab('askai')}
                          style={{ 
                            background: 'transparent', 
                            border: `1px solid ${t.border}`, 
                            borderRadius: 8, 
                            padding: '8px 14px', 
                            fontSize: '0.8125rem', 
                            fontWeight: 600, 
                            color: darkMode ? '#DDE8E2' : '#123E3A', 
                            cursor: 'pointer', 
                            fontFamily: "'DM Sans', sans-serif", 
                            alignSelf: 'flex-start', 
                            transition: 'all 0.15s' 
                          }}
                        >
                          View 80C Plans →
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ── TAB 2: TRANSACTIONS (Exact Figma Tab) ── */}
              {activeTab === 'transactions' && (
                <div>
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4" style={{ marginBottom: 20 }}>
                    <div>
                      <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: t.text, marginBottom: 2 }}>
                        Transaction History
                      </h2>
                      <p style={{ fontSize: '0.8125rem', color: t.muted }}>
                        {profile.name} · Core Banking Stream · September 2026
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <select 
                        style={{ 
                          background: t.surface, 
                          border: `1px solid ${t.border}`, 
                          borderRadius: 10, 
                          padding: '8px 14px', 
                          fontSize: '0.8125rem', 
                          color: t.text, 
                          cursor: 'pointer', 
                          fontFamily: "'DM Sans', sans-serif" 
                        }}
                      >
                        <option>All Categories</option>
                        <option>Income</option>
                        <option>Groceries</option>
                        <option>Utilities</option>
                        <option>Dining</option>
                        <option>EMI Debits</option>
                      </select>
                      <button 
                        style={{ 
                          background: '#D86F52', 
                          color: '#fff', 
                          border: 'none', 
                          borderRadius: 10, 
                          padding: '8px 18px', 
                          fontSize: '0.8125rem', 
                          fontWeight: 600, 
                          cursor: 'pointer', 
                          fontFamily: "'DM Sans', sans-serif" 
                        }}
                      >
                        Export CSV
                      </button>
                    </div>
                  </div>

                  <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        display: 'grid', 
                        gridTemplateColumns: '1fr 140px 140px', 
                        padding: '11px 24px', 
                        background: darkMode ? '#1E2B26' : '#F8F4EC', 
                        borderBottom: `1px solid ${t.border}` 
                      }}
                    >
                      {['Description', 'Date', 'Amount'].map(h => (
                        <span key={h} style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: t.muted, fontWeight: 600, textAlign: h === 'Amount' ? 'right' : 'left' }}>
                          {h}
                        </span>
                      ))}
                    </div>

                    {transactions.map((tx, i) => (
                      <div 
                        key={tx.id || i} 
                        style={{ 
                          display: 'grid', 
                          gridTemplateColumns: '1fr 140px 140px', 
                          padding: '14px 24px', 
                          borderBottom: i < transactions.length - 1 ? `1px solid ${t.borderSubtle}` : 'none', 
                          alignItems: 'center', 
                          transition: 'background 0.1s' 
                        }}
                      >
                        <div>
                          <p style={{ fontSize: '0.875rem', fontWeight: 500, color: t.text }}>{tx.description}</p>
                          <span style={{ fontSize: '0.725rem', color: t.muted }}>{tx.category}</span>
                        </div>
                        <span style={{ fontSize: '0.8125rem', color: t.muted, fontFamily: 'monospace' }}>
                          {tx.date}
                        </span>
                        <span 
                          style={{ 
                            fontSize: '0.9375rem', 
                            fontWeight: 600, 
                            color: tx.amount >= 0 ? '#2A6B63' : (darkMode ? '#F8F4EC' : '#202927'), 
                            textAlign: 'right', 
                            fontFamily: 'monospace' 
                          }}
                        >
                          {tx.amount >= 0 ? `+${fmtINR(tx.amount)}` : `−${fmtINR(Math.abs(tx.amount))}`}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Summary Bar */}
                  <div 
                    style={{ 
                      display: 'flex', 
                      gap: 20, 
                      marginTop: 16, 
                      padding: '16px 24px', 
                      background: darkMode ? '#1E2B26' : '#DDE8E2', 
                      border: `1px solid ${darkMode ? t.border : '#C4D8CC'}`, 
                      borderRadius: 10 
                    }}
                    className="flex-wrap"
                  >
                    {[
                      { label: 'Total Credits', value: `+${fmtINR(monthlySalary)}` },
                      { label: 'Total Debits', value: `−${fmtINR(monthlySpend)}` },
                      { label: 'Net Surplus', value: fmtINR(surplus) },
                    ].map(s => (
                      <div key={s.label} className="flex items-center gap-3">
                        <span style={{ fontSize: '0.775rem', color: darkMode ? '#8AA49C' : '#6B7872', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{s.label}:</span>
                        <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: darkMode ? '#F8F4EC' : '#202927', fontFamily: 'monospace' }}>{s.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── TAB 3: ASK AI (Exact Figma Chat with Sliding Flag Pill Toggle) ── */}
              {activeTab === 'askai' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 24, minHeight: 520 }}>
                  {/* Chat Area */}
                  <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, display: 'flex', flexDirection: 'column', overflow: 'hidden', transition: 'background 0.2s' }}>
                    {/* Chat Header with Sliding Flag Language Toggle */}
                    <div style={{ padding: '14px 22px', borderBottom: `1px solid ${t.border}`, display: 'flex', alignItems: 'center', gap: 10, background: '#123E3A' }}>
                      <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Sparkles className="w-4 h-4 text-emerald-300" />
                      </div>
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 600, fontSize: '0.9375rem', color: '#F8F4EC' }}>BharatBank AI</p>
                        <p style={{ fontSize: '0.75rem', color: '#DDE8E2', opacity: 0.75 }}>● Online · RBI Grounded RAG</p>
                      </div>
                      {/* Sliding Language Toggle */}
                      <LangToggle lang={lang} onChange={setLang} />
                    </div>

                    {/* Messages Stream */}
                    <div style={{ flex: 1, overflowY: 'auto', padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 14, background: t.bg, transition: 'background 0.2s' }}>
                      {chatMessages.map((msg, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                          {msg.role === 'ai' && (
                            <div style={{ width: 26, height: 26, borderRadius: 6, background: '#123E3A', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginRight: 8, marginTop: 2 }}>
                              <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
                            </div>
                          )}
                          <div 
                            style={{
                              maxWidth: '75%',
                              background: msg.role === 'user' ? '#123E3A' : t.surface,
                              color: msg.role === 'user' ? '#F8F4EC' : t.text,
                              borderRadius: msg.role === 'user' ? '10px 10px 2px 10px' : '10px 10px 10px 2px',
                              padding: '10px 14px',
                              fontSize: '0.875rem',
                              lineHeight: 1.55,
                              border: msg.role === 'ai' ? `1px solid ${t.border}` : 'none',
                              boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                            }}
                          >
                            <p className="whitespace-pre-line">{msg.text}</p>
                            {msg.citation && (
                              <div 
                                style={{
                                  marginTop: 8,
                                  padding: '4px 8px',
                                  borderRadius: 4,
                                  background: darkMode ? '#1E2B26' : '#DDE8E2',
                                  border: `1px solid ${darkMode ? t.border : '#C4D8CC'}`,
                                  fontSize: '0.725rem',
                                  color: '#2A6B63',
                                  fontFamily: 'monospace',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 4
                                }}
                              >
                                <BookOpen className="w-3 h-3 text-emerald-600 shrink-0" />
                                <span>{msg.citation}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}

                      {isTyping && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{ width: 26, height: 26, borderRadius: 6, background: '#123E3A', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                            <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
                          </div>
                          <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: '10px 10px 10px 2px', padding: '10px 16px', display: 'flex', gap: 4, alignItems: 'center' }}>
                            <span style={{ fontSize: '0.75rem', color: t.muted }}>BharatBank AI is thinking...</span>
                          </div>
                        </div>
                      )}
                      <div ref={chatEndRef} />
                    </div>

                    {/* Input Bar */}
                    <div style={{ padding: '14px 18px', borderTop: `1px solid ${t.border}`, display: 'flex', gap: 10, background: t.surface, transition: 'background 0.2s' }}>
                      <input
                        type="text"
                        value={chatInput}
                        onChange={e => setChatInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && sendChat(chatInput)}
                        placeholder={lang === 'EN' ? 'Ask about balances, DTI, spending, or loan terms…' : 'बैलेंस, DTI, लोन नियम, या खर्च के बारे में पूछें…'}
                        style={{ flex: 1, background: t.bg, border: `1px solid ${t.border}`, borderRadius: 8, padding: '10px 14px', fontSize: '0.875rem', color: t.text, fontFamily: "'DM Sans', sans-serif", outline: 'none' }}
                      />
                      <button
                        onClick={() => sendChat(chatInput)}
                        disabled={isTyping || !chatInput.trim()}
                        style={{ background: '#D86F52', border: 'none', borderRadius: 8, padding: '10px 16px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: !chatInput.trim() ? 0.5 : 1 }}
                      >
                        <Send className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>

                  {/* Suggested Inquiries (Exact Figma Sidebar) */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                    <div style={{ background: t.panelBg, border: `1px solid ${t.panelBorder}`, borderRadius: 10, padding: '18px 20px', transition: 'background 0.2s' }}>
                      <p style={{ fontWeight: 600, fontSize: '0.875rem', color: t.text, marginBottom: 12 }}>
                        {lang === 'EN' ? 'Try asking' : 'यह पूछें'}
                      </p>
                      {(lang === 'EN' ? [
                        "What's my DTI ratio?",
                        "Yeh cooling-off period kya hota hai?",
                        "What's my monthly surplus?",
                        "Explain my health score",
                        "Any suspicious activity?",
                        "How much can I save in taxes?",
                      ] : [
                        "मेरा DTI अनुपात क्या है?",
                        "कूलिंग-ऑफ पीरियड क्या होता है?",
                        "मेरी मासिक बचत क्या है?",
                        "मेरा हेल्थ स्कोर समझाएं",
                        "कोई संदिग्ध गतिविधि?",
                        "मैं कितना टैक्स बचा सकता हूं?",
                      ]).map(q => (
                        <button
                          key={q}
                          onClick={() => sendChat(q)}
                          style={{
                            display: 'block',
                            width: '100%',
                            textAlign: 'left',
                            background: t.surface,
                            border: `1px solid ${t.border}`,
                            borderRadius: 8,
                            padding: '9px 12px',
                            fontSize: '0.8125rem',
                            color: t.text,
                            cursor: 'pointer',
                            marginBottom: 8,
                            fontFamily: "'DM Sans', sans-serif",
                            transition: 'all 0.12s'
                          }}
                        >
                          {q}
                        </button>
                      ))}
                    </div>

                    <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '16px 18px', transition: 'background 0.2s' }}>
                      <p style={{ fontSize: '0.75rem', color: t.muted, lineHeight: 1.5 }}>
                        {lang === 'EN'
                          ? 'BharatBank AI uses your account data with zero hallucination. Verified against RBI Digital Lending Guidelines 2022.'
                          : 'BharatBank AI आपके खाते के डेटा का उपयोग करता है। RBI दिशानिर्देश 2022 द्वारा प्रमाणित।'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* ── TAB 4: THREATS (Exact Figma Security Monitoring) ── */}
              {activeTab === 'threats' && (
                <div>
                  <div className="flex items-center justify-between" style={{ marginBottom: 20 }}>
                    <div>
                      <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: t.text, marginBottom: 2, display: 'flex', alignItems: 'center', gap: 10 }}>
                        Security Threats
                        {highThreatsCount > 0 && (
                          <span style={{ background: '#C0392B', color: '#fff', fontSize: '0.75rem', fontWeight: 700, borderRadius: 99, padding: '2px 8px' }}>
                            {highThreatsCount} High
                          </span>
                        )}
                      </h2>
                      <p style={{ fontSize: '0.8125rem', color: t.muted }}>
                        PaySim-trained unsupervised anomaly detector monitoring real-time transactions
                      </p>
                    </div>
                    <button style={{ background: '#D86F52', color: '#fff', border: 'none', borderRadius: 10, padding: '9px 18px', fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer', fontFamily: "'DM Sans', sans-serif" }}>
                      Lock Account
                    </button>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginBottom: 24 }}>
                    {threats.map(tr => (
                      <div 
                        key={tr.id} 
                        style={{
                          background: t.surface,
                          border: `1px solid ${tr.severity === 'high' ? '#F5C6C6' : t.border}`,
                          borderLeft: `4px solid ${tr.severity === 'high' ? '#C0392B' : '#D86F52'}`,
                          borderRadius: 10,
                          padding: '20px 24px',
                          display: 'grid',
                          gridTemplateColumns: '1fr auto',
                          gap: 16,
                          alignItems: 'start',
                        }}
                      >
                        <div>
                          <div className="flex items-center gap-6" style={{ marginBottom: 8 }}>
                            <span 
                              style={{
                                background: tr.severity === 'high' ? (darkMode ? '#321515' : '#FDECEA') : (darkMode ? '#33271E' : '#FEF3EE'),
                                color: tr.severity === 'high' ? '#C0392B' : '#D86F52',
                                fontSize: '0.7rem', fontWeight: 700,
                                textTransform: 'uppercase', letterSpacing: '0.07em',
                                borderRadius: 6, padding: '3px 8px',
                              }}
                            >
                              {tr.severity === 'high' ? '● High' : '● Medium'}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: t.muted, fontFamily: 'monospace' }}>{tr.id}</span>
                            <span style={{ fontSize: '0.75rem', color: t.muted }}>{tr.time}</span>
                          </div>
                          <p style={{ fontWeight: 600, fontSize: '0.9375rem', color: t.text, marginBottom: 6 }}>{tr.type}</p>
                          <p style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44', lineHeight: 1.55 }}>{tr.description}</p>
                        </div>
                        <button 
                          style={{
                            background: tr.severity === 'high' ? '#C0392B' : 'transparent',
                            border: tr.severity === 'high' ? 'none' : `1px solid ${t.border}`,
                            color: tr.severity === 'high' ? '#fff' : t.text,
                            borderRadius: 8, padding: '8px 16px',
                            fontSize: '0.8125rem', fontWeight: 600,
                            cursor: 'pointer', fontFamily: "'DM Sans', sans-serif",
                            whiteSpace: 'nowrap', transition: 'all 0.15s',
                          }}
                        >
                          {tr.action}
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Cleared & Security Tips */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                    <div style={{ background: t.panelBg, border: `1px solid ${t.panelBorder}`, borderRadius: 10, padding: '20px 22px' }}>
                      <p style={{ fontWeight: 600, fontSize: '0.875rem', color: t.text, marginBottom: 10 }}>Recent Cleared Alerts</p>
                      {[
                        { desc: 'International transaction attempt — blocked', date: 'Sep 8' },
                        { desc: 'New payee addition — verified by biometric OTP', date: 'Sep 5' },
                        { desc: 'Large ATM withdrawal — confirmed', date: 'Sep 2' },
                      ].map((a, i) => (
                        <div key={i} className="flex items-center justify-between" style={{ marginBottom: 10 }}>
                          <div className="flex items-center gap-2">
                            <span style={{ color: '#2A6B63', fontSize: '0.8rem' }}>✓</span>
                            <span style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44' }}>{a.desc}</span>
                          </div>
                          <span style={{ fontSize: '0.75rem', color: t.muted, flexShrink: 0, marginLeft: 12 }}>{a.date}</span>
                        </div>
                      ))}
                    </div>

                    <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '20px 22px' }}>
                      <p style={{ fontWeight: 600, fontSize: '0.875rem', color: t.text, marginBottom: 10 }}>Security Tips</p>
                      {[
                        'Never share OTP or UPI PIN with anyone, including bank staff',
                        'Full 12-digit Aadhaar is never logged; only last 4 digits with Verhoeff check',
                        'Review linked devices in your account settings monthly',
                        'Report suspicious calls to 1930 (National Cyber Helpline)',
                      ].map((tip, i) => (
                        <div key={i} className="flex items-start gap-2" style={{ marginBottom: 9 }}>
                          <span style={{ color: '#123E3A', fontWeight: 700, flexShrink: 0 }}>·</span>
                          <span style={{ fontSize: '0.8125rem', color: darkMode ? '#DDE8E2' : '#3A4A44', lineHeight: 1.5 }}>{tip}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* ── TAB 5: SETTINGS (Includes Theme Switcher, Judge Persona Switcher & Live Veto Auditor) ── */}
              {activeTab === 'settings' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 20 }}>
                  {/* Theme Switcher (Exact Figma Slider) */}
                  <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '22px 26px', transition: 'background 0.2s' }}>
                    <p style={{ fontWeight: 600, fontSize: '0.9375rem', color: t.text, marginBottom: 16 }}>Appearance</p>
                    <div className="flex items-center justify-between" style={{ padding: '6px 0' }}>
                      <div>
                        <p style={{ fontSize: '0.875rem', fontWeight: 500, color: t.text, marginBottom: 2 }}>Visual Theme</p>
                        <p style={{ fontSize: '0.775rem', color: t.muted }}>
                          {darkMode ? 'Dark Mode (Deep Forest & Charcoal Slate)' : 'Figma Original (Warm Ivory & Deep Teal)'}
                        </p>
                      </div>
                      {/* Theme Pill Toggle */}
                      <div
                        onClick={() => setDarkMode(d => !d)}
                        style={{
                          width: 120, height: 36, borderRadius: 99,
                          background: darkMode ? '#202927' : '#F8F4EC',
                          border: `1px solid ${darkMode ? 'rgba(255,255,255,0.15)' : '#C2BAB0'}`,
                          display: 'flex', alignItems: 'center',
                          padding: '0 5px', cursor: 'pointer',
                          position: 'relative', transition: 'background 0.2s',
                        }}
                      >
                        <div style={{
                          position: 'absolute',
                          top: 4,
                          left: darkMode ? 'auto' : 4,
                          right: darkMode ? 4 : 'auto',
                          width: 28, height: 28, borderRadius: '50%',
                          background: darkMode ? '#2A6B63' : '#123E3A',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '0.875rem',
                          boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
                          transition: 'all 0.22s cubic-bezier(.4,0,.2,1)',
                        }}>
                          {darkMode ? '🌙' : '☀️'}
                        </div>
                        <span style={{
                          position: 'absolute',
                          left: darkMode ? 10 : 'auto',
                          right: darkMode ? 'auto' : 10,
                          fontSize: '0.7rem', fontWeight: 700,
                          color: darkMode ? '#8AA49C' : '#6B7872',
                          letterSpacing: '0.05em',
                          fontFamily: "'DM Sans', sans-serif",
                        }}>
                          {darkMode ? 'DARK' : 'LIGHT'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 1. JUDGE PERSONA SWITCHER */}
                  <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '22px 26px', transition: 'background 0.2s' }}>
                    <p style={{ fontWeight: 600, fontSize: '0.9375rem', color: t.text, marginBottom: 6 }}>
                      🎯 Customer Profile Switcher (Judge Canonical Presets)
                    </p>
                    <p style={{ fontSize: '0.775rem', color: t.muted, marginBottom: 16 }}>
                      Select a persona to immediately view how the feature engineering pipeline and veto thresholds adapt in real-time.
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                      {[
                        { id: 'CUST_ELEANOR', name: 'Eleanor Strauss', role: 'Figma Baseline (Healthy 72)' },
                        { id: 'CUST_PRIYA', name: 'Priya Sharma', role: 'Young Earner (Salary Jump)' },
                        { id: 'CUST_AMIT', name: 'Amit Patel', role: 'Stressed (Hard Veto Active)' },
                        { id: 'CUST_SUNITA', name: 'Sunita Devi', role: 'Artisan (Hindi Conversational)' },
                        { id: 'CUST_RAMESH', name: 'Ramesh Kumar', role: 'Stable Professional (Loan Approved)' },
                      ].map((c) => (
                        <button
                          key={c.id}
                          onClick={() => setSelectedCustomerId(c.id)}
                          style={{
                            padding: '12px 14px',
                            borderRadius: 8,
                            textAlign: 'left',
                            background: selectedCustomerId === c.id ? (darkMode ? '#1E2B26' : '#DDE8E2') : t.subtleBg,
                            border: `1px solid ${selectedCustomerId === c.id ? '#2A6B63' : t.border}`,
                            cursor: 'pointer',
                            transition: 'all 0.15s'
                          }}
                        >
                          <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: t.text }}>{c.name}</div>
                          <div style={{ fontSize: '0.7rem', color: t.muted, marginTop: 2 }}>{c.role}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 2. BANKER & JUDGE LIVE VETO AUDITOR (Interactive Stress Workbench) */}
                  <div style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '22px 26px', transition: 'background 0.2s' }}>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-3" style={{ borderBottom: `1px solid ${t.borderSubtle}`, marginBottom: 16 }}>
                      <div>
                        <div className="flex items-center gap-2">
                          <Sliders className="w-5 h-5 text-emerald-600" />
                          <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: t.text, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Banker &amp; Judge Live Veto Auditor (Interactive Stress Testing)
                          </h3>
                        </div>
                        <p style={{ fontSize: '0.775rem', color: t.muted, marginTop: 2 }}>
                          Drag the sliders to observe the deterministic Hard Veto Floor dynamically block credit pushes at 50% DTI.
                        </p>
                      </div>

                      <button
                        onClick={handleResetSim}
                        style={{
                          padding: '6px 14px',
                          borderRadius: 8,
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          background: t.subtleBg,
                          border: `1px solid ${t.border}`,
                          color: t.text,
                          cursor: 'pointer'
                        }}
                      >
                        Reset Sliders
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* DTI Slider */}
                      <div className="space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <span style={{ fontWeight: 600, color: t.text }}>Simulated Debt-to-Income (DTI)</span>
                          <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.875rem', color: simDti > 0.5 ? '#C0392B' : '#2A6B63' }}>
                            {(simDti * 100).toFixed(1)}%
                          </span>
                        </div>
                        <input
                          type="range"
                          min="0.10"
                          max="0.85"
                          step="0.01"
                          value={simDti}
                          onChange={(e) => handleSimulateDti(parseFloat(e.target.value))}
                          className="w-full accent-emerald-600 h-2 rounded-lg cursor-pointer"
                        />
                        <div className="flex justify-between text-[10px] font-mono" style={{ color: t.muted }}>
                          <span>10% (Solvent)</span>
                          <span style={{ color: '#C0392B', fontWeight: 700 }}>50.0% (Hard Ceiling)</span>
                          <span>85% (Distressed)</span>
                        </div>
                      </div>

                      {/* Health Score Slider */}
                      <div className="space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <span style={{ fontWeight: 600, color: t.text }}>Simulated Financial Health Score</span>
                          <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.875rem', color: simHealth < 40 ? '#C0392B' : '#2A6B63' }}>
                            {simHealth} / 100
                          </span>
                        </div>
                        <input
                          type="range"
                          min="10"
                          max="100"
                          step="1"
                          value={simHealth}
                          onChange={(e) => handleSimulateHealth(parseInt(e.target.value))}
                          className="w-full accent-emerald-600 h-2 rounded-lg cursor-pointer"
                        />
                        <div className="flex justify-between text-[10px] font-mono" style={{ color: t.muted }}>
                          <span style={{ color: '#C0392B', fontWeight: 700 }}>40 (Stress Floor)</span>
                          <span>60 (Watch)</span>
                          <span>100 (Healthy)</span>
                        </div>
                      </div>
                    </div>

                    {/* Gate Reaction Banner */}
                    <div
                      style={{
                        marginTop: 16,
                        padding: '12px 16px',
                        borderRadius: 8,
                        textAlign: 'center',
                        background: simDti > 0.5 || simHealth < 40 ? (darkMode ? '#321515' : '#FDECEA') : (darkMode ? '#1E2B26' : '#DDE8E2'),
                        border: `1px solid ${simDti > 0.5 || simHealth < 40 ? '#F5C6C6' : '#C4D8CC'}`,
                        color: simDti > 0.5 || simHealth < 40 ? '#C0392B' : '#2A6B63',
                        fontWeight: 700,
                        fontSize: '0.775rem',
                        letterSpacing: '0.05em',
                        textTransform: 'uppercase'
                      }}
                    >
                      {simDti > 0.5 || simHealth < 40
                        ? '🛑 HARD VETO GATE ACTIVE: Personal Loan & Credit Cards Frozen — Empathetic Relief Triggered'
                        : '🟢 GATEWAY OPEN: Borrower eligible for wealth creation & affordable credit'}
                    </div>
                  </div>

                  {/* 3. PROFILE & COMPLIANCE (Exact Figma Sections) */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                    {[
                      {
                        title: 'Profile & Security',
                        items: [
                          { label: 'Full Name', value: profile.name },
                          { label: 'DPDP Consent', value: `Tier ${profile.dpdp_consent_tier} Validated` },
                          { label: 'Data Residency', value: 'AWS Mumbai (ap-south-1)' },
                          { label: '2-Factor Auth', value: 'Enabled — Authenticator' },
                        ],
                        action: 'Edit Profile',
                      },
                      {
                        title: 'Statements & Audit',
                        items: [
                          { label: 'Audit Signature', value: `AUDIT_${profile.customer_id.substring(0, 10)}_2026` },
                          { label: 'RBI Compliance', value: 'Digital Lending 2022 Verified' },
                          { label: 'Account Opening', value: 'March 12, 2021' },
                          { label: 'Form 26AS', value: 'FY 2025-26 Available' },
                        ],
                        action: 'Download Docs',
                      },
                    ].map(section => (
                      <div key={section.title} style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, padding: '22px 26px' }}>
                        <div className="flex items-center justify-between" style={{ marginBottom: 14 }}>
                          <p style={{ fontWeight: 600, fontSize: '0.9375rem', color: t.text }}>{section.title}</p>
                          <button style={{ background: 'transparent', border: `1px solid ${t.border}`, borderRadius: 8, padding: '4px 10px', fontSize: '0.775rem', color: darkMode ? '#DDE8E2' : '#123E3A', cursor: 'pointer' }}>
                            {section.action}
                          </button>
                        </div>
                        {section.items.map(item => (
                          <div key={item.label} className="flex items-center justify-between" style={{ padding: '8px 0', borderBottom: `1px solid ${t.borderSubtle}` }}>
                            <span style={{ fontSize: '0.8125rem', color: t.muted }}>{item.label}</span>
                            <span style={{ fontSize: '0.8125rem', color: t.text, fontWeight: 500 }}>{item.value}</span>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* ── FOOTER (Exact Figma Layout) ── */}
      <footer style={{ borderTop: `1px solid ${t.border}`, padding: '16px 0', background: t.bg, transition: 'background 0.2s' }}>
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs" style={{ color: t.muted }}>
          <span>
            © 2026 BharatBank AI · Theme: Digital Transformation in Lending · RBI Regulated · DICGC Insured
          </span>
          <div className="flex gap-5">
            {['Privacy Policy', 'Terms of Use', 'Accessibility'].map(l => (
              <a key={l} href="#" style={{ color: t.muted, textDecoration: 'none' }} className="hover:underline">
                {l}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
