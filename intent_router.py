"""
intent_router.py — Per-Turn Intent Router & Language Detector for BharatBanker AI.

Author: Person 3 (Conversational AI & Multilingual RAG Lead)
Scope: Sub-Problem 2 (Vernacular-First Conversational Banking)
Standards:
  - Per-turn dispatching between TASK_SLOT_FILLING and KNOWLEDGE_RAG.
  - Seamless mid-KYC policy detours without resetting collected slot state.
  - Robust multilingual script and dialect identification (Devanagari, Hinglish, English).
"""

from enum import Enum
import re
from typing import Optional, Set, Tuple


class IntentCategory(str, Enum):
    TASK_SLOT_FILLING = "TASK_SLOT_FILLING"
    KNOWLEDGE_RAG = "KNOWLEDGE_RAG"
    RESET_FLOW = "RESET_FLOW"
    GREETING = "GREETING"
    HELP = "HELP"


# Common Hinglish conversational indicator words
HINGLISH_WORDS: Set[str] = {
    "kya", "kyu", "kyun", "kaise", "kab", "kisko", "kaha", "kahan", "kitna", "kitni",
    "hai", "hain", "hoon", "tha", "thi", "the", "mera", "meri", "mere", "aap", "aapka",
    "aapki", "aapke", "tum", "tumhara", "hum", "humne", "mujhe", "chahiye", "nahi", "matlab",
    "karo", "karein", "batao", "batayein", "bataiye", "hoga", "hogi", "dena", "le", "lo",
    "namaste", "pranam", "dhanyawad", "shukriya", "bhai", "sir", "madam", "paise", "rupaye",
    "khata", "bima", "byaj", "karz", "chukana", "chahiye", "sahayata", "madad"
}

# Question / Inquiry indicators indicating knowledge intent
QUESTION_WORDS: Set[str] = {
    "what", "why", "how", "when", "where", "who", "which", "whose", "can i", "is it",
    "kya", "kyun", "kyu", "kaise", "kab", "kahan", "kitna", "matlab", "arth", "samjhao",
    "explain", "meaning", "rule", "rules", "policy", "guideline", "guidelines", "reason",
    "cooling-off", "cooling off", "look-up", "lookup", "penalty", "charge", "charges",
    "foreclosure", "prepayment", "apr", "kfs", "aadhaar", "pan", "mandate", "harassment",
    "recovery", "agent", "ombudsman", "dti", "overdraft", "od", "insurance", "beema", "bima"
}

# Reset keywords
RESET_KEYWORDS: Set[str] = {
    "reset", "restart", "start over", "cancel", "shuru se", "naye sire se",
    "dobara shuru", "cancel application", "radd karo"
}

# Greeting keywords
GREETING_KEYWORDS: Set[str] = {
    "hi", "hello", "hey", "namaste", "pranam", "vanakkam", "sat sri akal",
    "good morning", "good afternoon", "good evening"
}


class IntentRouter:
    """Per-turn dispatcher that categorizes user utterances and enables
    state-preserving knowledge detours.
    """

    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        """Detects whether text is Devanagari Hindi ('hi'), Hinglish ('hi_en'), or English ('en')."""
        clean = text.strip()
        if not clean:
            return "en"

        # Check for Devanagari Unicode block (\u0900 to \u097F)
        devanagari_chars = len(re.findall(r"[\u0900-\u097F]", clean))
        total_alpha = len(re.findall(r"[a-zA-Z\u0900-\u097F]", clean))

        if total_alpha > 0 and (devanagari_chars / total_alpha) > 0.30:
            return "hi"

        # Check for Romanized Hindi / Hinglish tokens
        words = re.findall(r"\b[a-zA-Z]+\b", clean.lower())
        if words:
            hinglish_match_count = sum(1 for w in words if w in HINGLISH_WORDS)
            if (hinglish_match_count / len(words)) >= 0.20 or any(w in ["kya", "kyun", "matlab", "chahiye"] for w in words):
                return "hi_en"

        return "en"

    def route_turn(
        self,
        text: str,
        current_slot: Optional[str] = None,
        is_journey_active: bool = False
    ) -> Tuple[IntentCategory, str]:
        """Classifies the inbound message per-turn into an IntentCategory and detected language.

        Decision Rules:
        1. Explicit reset requests -> RESET_FLOW
        2. If active journey and input matches slot pattern -> TASK_SLOT_FILLING
        3. If input has question tokens / RAG indicators -> KNOWLEDGE_RAG
        4. If greeting / standalone hello -> GREETING
        5. Default to TASK_SLOT_FILLING if journey active, else KNOWLEDGE_RAG.
        """
        detected_lang = self.detect_language(text)
        t_clean = text.strip().lower()

        # 1. Reset check
        if any(kw in t_clean for kw in RESET_KEYWORDS):
            return IntentCategory.RESET_FLOW, detected_lang

        # 2. Greeting check (only when journey is not yet active or user just said hello)
        if not is_journey_active and t_clean in GREETING_KEYWORDS:
            return IntentCategory.GREETING, detected_lang

        # 3. Knowledge / RAG query detection
        is_question = (
            "?" in text
            or any(re.search(r"\b" + re.escape(w) + r"\b", t_clean) for w in QUESTION_WORDS)
        )

        # Check if the text is clearly an answer for the active slot
        is_slot_answer = False
        if is_journey_active and current_slot:
            is_slot_answer = self._is_likely_slot_value(current_slot, text)

        # Disambiguation:
        # If user explicitly asked a question (e.g. "Yeh cooling-off kya hai?" or "Why do you need my PAN?")
        # Even if in active journey, route to KNOWLEDGE_RAG!
        if is_question and not (is_slot_answer and len(t_clean.split()) <= 2):
            return IntentCategory.KNOWLEDGE_RAG, detected_lang

        # If in active journey, prefer TASK_SLOT_FILLING
        if is_journey_active and current_slot:
            return IntentCategory.TASK_SLOT_FILLING, detected_lang

        # If not in journey and question was asked
        if is_question:
            return IntentCategory.KNOWLEDGE_RAG, detected_lang

        # Fallback to Task Slot Filling if journey is active, else Knowledge RAG
        if is_journey_active:
            return IntentCategory.TASK_SLOT_FILLING, detected_lang
        else:
            return IntentCategory.KNOWLEDGE_RAG, detected_lang

    def _is_likely_slot_value(self, slot_name: str, text: str) -> bool:
        """Heuristic check to identify direct slot inputs (e.g. numeric income, PAN)."""
        t = text.strip()
        words = t.split()

        if slot_name == "pan_number":
            # PAN is exactly 10 alphanumeric chars
            cleaned = t.upper().replace(" ", "")
            return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", cleaned))

        elif slot_name == "aadhaar_last4":
            # Exactly 4 digits
            digits = re.sub(r"\D", "", t)
            return len(digits) == 4 and len(words) <= 2

        elif slot_name in ["monthly_income", "loan_amount"]:
            # Contains numbers or Lakh / k
            has_digits = bool(re.search(r"\d", t))
            is_short = len(words) <= 3
            return has_digits and is_short

        elif slot_name == "full_name":
            # 1 to 4 words, purely letters
            return 1 <= len(words) <= 4 and bool(re.match(r"^[a-zA-Z\s\.\u0900-\u097F]+$", t))

        elif slot_name == "employment_type":
            common_types = ["salaried", "self", "business", "artisan", "naukri", "job", "dukan"]
            return any(w in t.lower() for w in common_types)

        return False
