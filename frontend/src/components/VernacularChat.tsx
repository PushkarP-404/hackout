"use client";

import React, { useState, useRef, useEffect } from "react";
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  Languages, 
  CheckCircle2, 
  AlertCircle, 
  FileCheck, 
  BookOpen, 
  ShieldCheck,
  RotateCcw
} from "lucide-react";
import { sendChatMessage } from "../lib/api";

interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  citation?: string | null;
  intentType?: string;
  isVeto?: boolean;
  time: string;
}

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: "m-0",
    sender: "bot",
    text: "नमस्ते! मैं BharatBanker का डिजिटल सहायक हूँ। मैं आपकी भाषा में सुरक्षित लोन आवेदन और बैंकिंग नियमों में सहायता कर सकता हूँ।\n\nआप लोन आवेदन शुरू करने के लिए अपना नाम बता सकते हैं, या कोई भी नीति सम्बन्धी सवाल पूछ सकते हैं।",
    time: "Just now",
  },
];

const SUGGESTIONS = [
  "Yeh cooling-off period kya hota hai?",
  "Why do you need my PAN card?",
  "What is the 50% DTI rule?",
  "Can I prepay my loan without penalty?",
];

const KYC_SLOTS = [
  { key: "name", label: "Full Name" },
  { key: "pan_number", label: "PAN (ABCDE1234F)" },
  { key: "aadhaar_last4", label: "Aadhaar Last 4 (Verhoeff)" },
  { key: "monthly_income", label: "Monthly Income" },
  { key: "loan_amount", label: "Loan Amount" },
  { key: "employment_type", label: "Employment" },
];

export const VernacularChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("hi");
  const [completedSlots, setCompletedSlots] = useState<string[]>([]);
  const [currentSlot, setCurrentSlot] = useState<string>("name");
  const [sessionId] = useState(() => "session_" + Math.random().toString(36).substring(2, 9));
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: "u-" + Date.now(),
      sender: "user",
      text: query,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const resp = await sendChatMessage(sessionId, query, selectedLanguage);

      const botMsg: ChatMessage = {
        id: "b-" + Date.now(),
        sender: "bot",
        text: resp.bot_message,
        citation: resp.grounded_citation,
        intentType: resp.intent_type,
        isVeto: resp.ethical_veto_triggered,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, botMsg]);

      // Update slot progression
      if (resp.collected_slots) {
        setCompletedSlots(Object.keys(resp.collected_slots));
      }
      if (resp.current_slot) {
        setCurrentSlot(resp.current_slot);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setMessages(INITIAL_MESSAGES);
    setCompletedSlots([]);
    setCurrentSlot("name");
  };

  return (
    <div className="space-y-6">
      {/* HEADER & SLOT STEPPER */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg font-black text-white tracking-tight">
                Vernacular Conversational AI Studio
              </h2>
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Slot-Filling + Grounded RAG
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Supports mid-KYC policy detours without dialogue state loss. Citations grounded in verified RBI & PMJDY directives.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500"
            >
              <option value="hi">हिंदी (Hindi / Hinglish)</option>
              <option value="en">English (Official)</option>
              <option value="ta">தமிழ் (Tamil)</option>
              <option value="te">తెలుగు (Telugu)</option>
            </select>

            <button
              onClick={handleReset}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
              title="Reset Conversation"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* VISUAL KYC SLOT PROGRESS BAR */}
        <div className="pt-2 border-t border-slate-800/80">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-semibold mb-2">
            <span>KYC & LOAN JOURNEY PROGRESS</span>
            <span className="text-cyan-400">
              {completedSlots.length} of {KYC_SLOTS.length} Verified
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
            {KYC_SLOTS.map((slot, idx) => {
              const isDone = completedSlots.includes(slot.key);
              const isCurrent = currentSlot === slot.key && !isDone;

              return (
                <div
                  key={idx}
                  className={`p-2 rounded-lg border text-center transition-all ${
                    isDone
                      ? "bg-emerald-950/30 border-emerald-500/40 text-emerald-300"
                      : isCurrent
                      ? "bg-cyan-950/40 border-cyan-500/60 text-cyan-200 ring-1 ring-cyan-500/40"
                      : "bg-slate-900/40 border-slate-800 text-slate-500"
                  }`}
                >
                  <div className="flex items-center justify-center gap-1 mb-0.5">
                    {isDone ? (
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    ) : (
                      <span className="w-3 h-3 rounded-full border border-slate-600 text-[9px] flex items-center justify-center font-mono">
                        {idx + 1}
                      </span>
                    )}
                    <span className="text-[10px] font-bold uppercase truncate">
                      {slot.key.replace("_", " ")}
                    </span>
                  </div>
                  <div className="text-[9px] text-slate-400 truncate">
                    {slot.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CHAT CONTAINER */}
      <div className="glass-card rounded-2xl border border-slate-800 flex flex-col h-[520px] overflow-hidden shadow-2xl">
        {/* MESSAGE STREAM */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${
                msg.sender === "user" ? "items-end" : "items-start"
              }`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 shadow-lg ${
                  msg.sender === "user"
                    ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-br-none"
                    : "bg-slate-900/90 border border-slate-850 text-slate-100 rounded-bl-none"
                }`}
              >
                {/* Intent & Type Badge */}
                {msg.intentType && msg.sender === "bot" && (
                  <div className="flex items-center gap-2 mb-2 pb-1.5 border-b border-slate-800">
                    <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1">
                      <Sparkles className="w-2.5 h-2.5" />
                      <span>{msg.intentType.replace("_", " ")}</span>
                    </span>
                    {msg.isVeto && (
                      <span className="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/30">
                        Ethical Veto Intercept
                      </span>
                    )}
                  </div>
                )}

                {/* Message Content */}
                <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-line font-normal">
                  {msg.text}
                </p>

                {/* Grounded Citation Box */}
                {msg.citation && (
                  <div className="mt-3 p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 flex items-start gap-2 text-emerald-300 text-xs">
                    <BookOpen className="w-3.5 h-3.5 mt-0.5 shrink-0 text-emerald-400" />
                    <div>
                      <div className="font-bold text-[10px] uppercase tracking-wider text-emerald-400">
                        Official Regulatory Citation
                      </div>
                      <div className="font-mono text-[11px]">{msg.citation}</div>
                    </div>
                  </div>
                )}

                <div
                  className={`text-[10px] mt-2 ${
                    msg.sender === "user" ? "text-cyan-200" : "text-slate-400"
                  } text-right`}
                >
                  {msg.time}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-slate-400 p-3 bg-slate-900/60 rounded-xl max-w-xs border border-slate-800">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>Verifying slots & querying multilingual vector index...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* QUICK DETOUR CHIPS */}
        <div className="p-3 bg-slate-900/60 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 shrink-0 flex items-center gap-1">
            <BookOpen className="w-3 h-3" />
            <span>Detour Qs:</span>
          </span>
          {SUGGESTIONS.map((sug, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(sug)}
              className="text-xs shrink-0 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-cyan-300 border border-slate-700 transition-colors"
            >
              {sug}
            </button>
          ))}
        </div>

        {/* INPUT FORM */}
        <div className="p-3.5 bg-slate-950 border-t border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message in Hindi, Hinglish, or English (e.g. 'Sunita Devi', 'ABCDE1234F', or ask a question)..."
              className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-md shadow-cyan-500/20 disabled:opacity-40 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
