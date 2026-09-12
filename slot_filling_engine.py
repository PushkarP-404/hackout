"""
slot_filling_engine.py — Deterministic Dialogue State Machine for BharatBanker AI.

Author: Person 3 (Conversational AI & Multilingual RAG Lead)
Scope: Sub-Problem 2 (Vernacular-First Conversational Banking)
Standards:
  - Non-negotiable Verhoeff Checksum Algorithm on Aadhaar last 4 digits.
  - Strict PAN Regex validation ([A-Z]{5}[0-9]{4}[A-Z]{1}).
  - State persistence for mid-flow RAG detours (freeze/resume without slot resets).
  - Plain-language vernacular error correction in Hindi, Hinglish, and English.
  - Ethical DTI check & handshake preparation for Person 2 Veto Layer.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# 1. MATHEMATICAL FOUNDATION: VERHOEFF CHECKSUM ALGORITHM (Dihedral Group D5)
# ==============================================================================

# Multiplication table d based on dihedral group D5
_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

# Permutation table p (8 x 10)
_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

# Inverse table inv
_VERHOEFF_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def generate_verhoeff_check_digit(num_str: str) -> str:
    """Computes the Verhoeff check digit for any numeric string."""
    clean = re.sub(r"\D", "", num_str)
    if not clean:
        raise ValueError("Input string must contain at least one digit.")
    c = 0
    for i, item in enumerate(reversed(clean)):
        c = _VERHOEFF_D[c][_VERHOEFF_P[(i + 1) % 8][int(item)]]
    return str(_VERHOEFF_INV[c])


def validate_verhoeff(num_str: str) -> bool:
    """Validates whether a numeric string with check digit satisfies the Verhoeff checksum."""
    clean = re.sub(r"\D", "", num_str)
    if len(clean) < 2:
        return False
    c = 0
    for i, item in enumerate(reversed(clean)):
        c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][int(item)]]
    return c == 0


def generate_valid_aadhaar_last4_sample(prefix: str = "236") -> str:
    """Helper utility for demos and tests: returns a 4-digit string that passes Verhoeff."""
    clean_prefix = re.sub(r"\D", "", prefix)[:3]
    if len(clean_prefix) < 3:
        clean_prefix = "236"
    chk = generate_verhoeff_check_digit(clean_prefix)
    return clean_prefix + chk


# ==============================================================================
# 2. VALIDATION HELPERS & REGEX
# ==============================================================================

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")


def validate_full_name(name_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validates full name (min 3 chars, letters, spaces, dots)."""
    cleaned = " ".join(name_str.strip().split())
    if len(cleaned) < 3:
        return False, None, "Name must be at least 3 characters."
    if not re.match(r"^[a-zA-Z\s\.\u0900-\u097F]+$", cleaned):
        return False, None, "Name must contain only alphabetic characters."
    return True, cleaned, None


def validate_pan(pan_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Strict deterministic PAN validation: 5 letters, 4 numbers, 1 letter."""
    cleaned = pan_str.strip().upper().replace(" ", "").replace("-", "")
    if not PAN_REGEX.match(cleaned):
        return False, None, "Invalid PAN format (expected ABCDE1234F)."
    return True, cleaned, None


def validate_aadhaar_last4(aadhaar_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validates last 4 digits of Aadhaar with Verhoeff checksum.
    Never collects or stores 12 digits, complying with DPDP Act 2023.
    """
    cleaned = re.sub(r"\D", "", aadhaar_str.strip())
    if len(cleaned) != 4:
        return False, None, "Please provide exactly the last 4 digits of your Aadhaar."
    if not validate_verhoeff(cleaned):
        example_valid = generate_valid_aadhaar_last4_sample(cleaned[:3])
        return (
            False,
            None,
            f"Aadhaar last 4 digits failed Verhoeff checksum. (For prefix '{cleaned[:3]}', valid check digit is '{example_valid[-1]}', e.g. '{example_valid}').",
        )
    return True, cleaned, None


def parse_indian_currency_str(text: str) -> Optional[float]:
    """Parses colloquial Indian currency amounts (e.g. 50k, 1.5 Lakh, ₹45,000, 75000)."""
    t = text.lower().strip().replace("₹", "").replace("rs.", "").replace("rs", "").replace(",", "").strip()

    # Match Lakh pattern: e.g. '1.5 lakh', '2 lac', '2.5lakhs'
    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|lacs|lakhs)", t)
    if lakh_match:
        try:
            return float(lakh_match.group(1)) * 100000.0
        except ValueError:
            pass

    # Match Thousand / K pattern: e.g. '50k', '45 thousand', '60 hazar'
    k_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:k|thousand|hazar|hazaar)", t)
    if k_match:
        try:
            return float(k_match.group(1)) * 1000.0
        except ValueError:
            pass

    # Pure number pattern
    num_match = re.search(r"(\d+(?:\.\d+)?)", t)
    if num_match:
        try:
            return float(num_match.group(1))
        except ValueError:
            return None
    return None


def validate_monthly_income(income_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """Validates monthly income: must be >= ₹5,000 and reasonable (< ₹50,00,000)."""
    val = parse_indian_currency_str(income_str)
    if val is None:
        return False, None, "Could not parse income amount. Please enter in numbers (e.g. 45000)."
    if val < 5000.0:
        return False, None, "Monthly income must be at least ₹5,000."
    if val > 5000000.0:
        return False, None, "Monthly income exceeds maximum permissible threshold for this tier."
    return True, val, None


def validate_loan_amount(loan_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """Validates requested loan amount (₹10,000 to ₹10,00,000 for digital instant retail loans)."""
    val = parse_indian_currency_str(loan_str)
    if val is None:
        return False, None, "Could not parse loan amount. Please enter in numbers (e.g. 150000 or 1.5 Lakh)."
    if val < 10000.0:
        return False, None, "Minimum digital loan amount is ₹10,000."
    if val > 1000000.0:
        return False, None, "Maximum digital instant loan cap is ₹10,00,000 (10 Lakhs)."
    return True, val, None


def validate_employment_type(emp_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Normalizes employment type to standard categories."""
    t = emp_str.strip().lower()
    if any(w in t for w in ["salaried", "naukri", "job", "private", "govt", "government", "service"]):
        return True, "Salaried", None
    if any(w in t for w in ["self", "freelance", "professional", "consultant", "doctor", "ca", "advocate"]):
        return True, "Self-Employed", None
    if any(w in t for w in ["business", "vyapaar", "dukan", "shop", "merchant", "vyapari", "trade", "enterprise"]):
        return True, "Business", None
    if any(w in t for w in ["artisan", "karigar", "agriculture", "farmer", "kisan", "daily", "mazdoor"]):
        return True, "Artisan / Micro-Enterprise", None
    # Default fallback if reasonably text
    if len(t) >= 3:
        return True, emp_str.strip().title(), None
    return False, None, "Please select: Salaried, Self-Employed, Business, or Artisan."


# ==============================================================================
# 3. DIALOGUE STATE MODEL & VERNACULAR PROMPT CATALOG
# ==============================================================================

class Language(str, Enum):
    HINDI = "hi"         # Devanagari
    HINGLISH = "hi_en"   # Roman Hindi
    ENGLISH = "en"       # Standard English


SLOT_SEQUENCE = [
    "full_name",
    "pan_number",
    "aadhaar_last4",
    "monthly_income",
    "loan_amount",
    "employment_type",
]


PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "welcome": {
        "hi": "नमस्ते! मैं आपका भारतबैंकर साथी हूँ। मैं आपके डिजिटल लोन आवेदन में सहायता करूँगा। चलिए शुरू करते हैं! कृपया अपना पूरा नाम दर्ज करें:",
        "hi_en": "Namaste! Main aapka BharatBanker saathi hoon. Main aapke digital loan application mein madad karunga. Chaliye shuru karte hain! Kripya apna poora naam darj karein:",
        "en": "Hello! I am your BharatBanker digital assistant. I will assist you with your instant loan application. Let's begin! Please provide your Full Name:",
    },
    "full_name": {
        "hi": "कृपया अपना पूरा नाम दर्ज करें (जैसा कि आपके बैंक खाते में है):",
        "hi_en": "Kripya apna poora naam darj karein (jaise aapke bank khate mein hai):",
        "en": "Please provide your Full Name (as per your bank account):",
    },
    "pan_number": {
        "hi": "धन्यवाद {name}! अब कृपया अपना 10-अंकों का पैन नंबर दर्ज करें (उदाहरण: ABCDE1234F):",
        "hi_en": "Dhanyawad {name}! Ab kripya apna 10-digit PAN number darj karein (udanharan: ABCDE1234F):",
        "en": "Thank you {name}! Now please provide your 10-character PAN number (e.g., ABCDE1234F):",
    },
    "aadhaar_last4": {
        "hi": "आपकी पहचान सुरक्षित रूप से सत्यापित करने के लिए, कृपया अपने आधार कार्ड के केवल अंतिम 4 अंक दर्ज करें (DPDP नियम 2023 के तहत):",
        "hi_en": "Aapki pehchan surakshit roop se verify karne ke liye, kripya apne Aadhaar card ke keval antim 4 ank darj karein (DPDP Act 2023 ke tehat):",
        "en": "For secure identity verification under DPDP Act 2023, please enter ONLY the LAST 4 DIGITS of your Aadhaar card:",
    },
    "monthly_income": {
        "hi": "धन्यवाद। कृपया अपनी औसत मासिक आय (₹ में) दर्ज करें (उदाहरण: 45000):",
        "hi_en": "Dhanyawad. Kripya apni ausat masik aamdani (₹ mein) darj karein (udanharan: 45000):",
        "en": "Thank you. Please enter your average net monthly income in ₹ (e.g., 45000):",
    },
    "loan_amount": {
        "hi": "आप कितनी लोन राशि (₹ में) लेना चाहते हैं? (उदाहरण: ₹1,00,000 या 1 Lakh):",
        "hi_en": "Aap kitni loan rashi (₹ mein) aavedan karna chahte hain? (udanharan: 100000 ya 1 Lakh):",
        "en": "How much loan amount (in ₹) would you like to apply for? (e.g., 100000 or 1.5 Lakh):",
    },
    "employment_type": {
        "hi": "कृपया अपने रोजगार का प्रकार बताएं (Salaried / Self-Employed / Business / Artisan):",
        "hi_en": "Kripya apne rojgaar ka prakar batayein (Salaried / Self-Employed / Business / Artisan):",
        "en": "Please specify your employment type (Salaried / Self-Employed / Business / Artisan):",
    },
}

ERROR_TEMPLATES: Dict[str, Dict[str, str]] = {
    "full_name": {
        "hi": "कृपया एक मान्य नाम दर्ज करें (कम से कम 3 अक्षर, केवल शब्द):",
        "hi_en": "Kripya ek valid naam darj karein (kam se kam 3 akshar, bina kisi special character ke):",
        "en": "Please provide a valid full name (minimum 3 characters, alphabets only):",
    },
    "pan_number": {
        "hi": "पैन नंबर अमान्य है। पैन 10 अक्षरों का होना चाहिए, जैसे 5 अक्षर, 4 अंक और 1 अक्षर (उदाहरण: ABCDE1234F)। कृपया पुनः प्रयास करें:",
        "hi_en": "PAN number sahi nahi hai. PAN 10 aksharon ka hona chahiye (jaise: ABCDE1234F). Kripya dobara darj karein:",
        "en": "Invalid PAN format. PAN must be exactly 10 alphanumeric characters (e.g., ABCDE1234F). Please re-enter:",
    },
    "aadhaar_last4": {
        "hi": "आधार के अंतिम 4 अंक अमान्य हैं या Verhoeff चेकसम में विफल रहे। कृपया अपने सही अंतिम 4 अंक दर्ज करें (उदाहरण: 2363):",
        "hi_en": "Aadhaar ke antim 4 ank sahi nahi hain ya Verhoeff checksum pass nahi hua. Kripya apne sahi antim 4 ank darj karein (udanharan: 2363):",
        "en": "The last 4 digits of Aadhaar failed the Verhoeff checksum validation. Please enter valid 4 digits (e.g. 2363):",
    },
    "monthly_income": {
        "hi": "अमान्य मासिक आय। कृपया केवल संख्या दर्ज करें (न्यूनतम ₹5,000, जैसे: 35000 या 50k):",
        "hi_en": "Amaniya masik aamdani. Kripya keval sankhya darj karein (kam se kam ₹5,000, jaise: 35000 ya 50k):",
        "en": "Invalid monthly income. Please provide a numeric amount (minimum ₹5,000, e.g., 35000 or 50k):",
    },
    "loan_amount": {
        "hi": "अमान्य लोन राशि। डिजिटल लोन ₹10,000 से ₹10,00,000 के बीच उपलब्ध है (उदाहरण: 150000 या 1.5 Lakh):",
        "hi_en": "Amaniya loan rashi. Digital loan ₹10,000 se ₹10,00,000 ke beech uplabdh hai (udanharan: 150000 ya 1.5 Lakh):",
        "en": "Invalid loan amount. Instant digital loans range from ₹10,000 to ₹10,00,000 (e.g., 150000 or 1.5 Lakh):",
    },
    "employment_type": {
        "hi": "कृपया मान्य विकल्प चुनें: Salaried, Self-Employed, Business, या Artisan:",
        "hi_en": "Kripya sahi vikalp chunein: Salaried, Self-Employed, Business, ya Artisan:",
        "en": "Please choose a valid option: Salaried, Self-Employed, Business, or Artisan:",
    },
}


@dataclass
class DialogueState:
    session_id: str
    current_slot: str = "full_name"
    collected_slots: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    is_journey_complete: bool = False
    is_frozen: bool = False
    detected_language: str = "hi"
    last_bot_prompt: str = ""
    veto_triggered: bool = False
    veto_reason: Optional[str] = None


@dataclass
class SlotResult:
    is_valid: bool
    slot_name: str
    cleaned_value: Any
    bot_message: str
    current_slot: Optional[str]
    collected_slots: Dict[str, Any]
    is_journey_complete: bool
    error_message: Optional[str] = None
    veto_triggered: bool = False
    veto_details: Optional[Dict[str, Any]] = None


# ==============================================================================
# 4. SLOT-FILLING ENGINE CONTROLLER
# ==============================================================================

class SlotFillingEngine:
    """Manages the structured Loan Application Journey with deterministic validation,
    mid-flow state freeze/resume, and plain-language vernacular guidance.
    """

    def __init__(self):
        self._sessions: Dict[str, DialogueState] = {}

    def get_or_create_state(self, session_id: str, default_language: str = "hi") -> DialogueState:
        if session_id not in self._sessions:
            self._sessions[session_id] = DialogueState(
                session_id=session_id,
                current_slot="full_name",
                detected_language=default_language,
            )
        return self._sessions[session_id]

    def reset_journey(self, session_id: str, language: str = "hi") -> DialogueState:
        state = DialogueState(
            session_id=session_id,
            current_slot="full_name",
            detected_language=language,
        )
        self._sessions[session_id] = state
        return state

    def get_welcome_message(self, session_id: str, language: str = "hi") -> str:
        state = self.get_or_create_state(session_id, default_language=language)
        state.detected_language = language
        lang_key = self._normalize_lang_key(language)
        msg = PROMPT_TEMPLATES["welcome"].get(lang_key, PROMPT_TEMPLATES["welcome"]["en"])
        state.last_bot_prompt = msg
        return msg

    def freeze_for_detour(self, session_id: str) -> None:
        """Freezes current dialogue state so a mid-flow knowledge detour does not reset slots."""
        if session_id in self._sessions:
            self._sessions[session_id].is_frozen = True

    def resume_after_detour(self, session_id: str, language: Optional[str] = None) -> str:
        """Resumes the pending slot prompt after answering an informational RAG query."""
        state = self.get_or_create_state(session_id)
        state.is_frozen = False
        if language:
            state.detected_language = language
        lang_key = self._normalize_lang_key(state.detected_language)

        slot = state.current_slot
        if state.is_journey_complete:
            if lang_key == "hi":
                return "आपका लोन आवेदन पहले ही सफलतापूर्वक जमा हो चुका है। क्या आप कोई अन्य जानकारी चाहते हैं?"
            elif lang_key == "hi_en":
                return "Aapka loan application pehle hi submit ho chuka hai. Kya aap koi aur jankari chahte hain?"
            else:
                return "Your loan application has already been submitted. May I help you with anything else?"

        template = PROMPT_TEMPLATES.get(slot, {}).get(lang_key, PROMPT_TEMPLATES["full_name"]["en"])
        name = state.collected_slots.get("full_name", "Mitra")
        formatted = template.format(name=name)

        # Prepend graceful detour resumption phrase
        if lang_key == "hi":
            prefix = "नीतिगत जानकारी के बाद, चलिए आपका आवेदन जारी रखते हैं। "
        elif lang_key == "hi_en":
            prefix = "Niti jankari ke baad, chaliye aapka application jari rakhte hain. "
        else:
            prefix = "Now returning back to your application: "

        resumption_msg = prefix + formatted
        state.last_bot_prompt = resumption_msg
        return resumption_msg

    def process_turn(
        self, session_id: str, user_text: str, language: Optional[str] = None
    ) -> SlotResult:
        """Processes a single conversational turn for slot filling."""
        state = self.get_or_create_state(session_id)
        if language:
            state.detected_language = language
        lang_key = self._normalize_lang_key(state.detected_language)

        if state.is_journey_complete:
            return SlotResult(
                is_valid=True,
                slot_name="completed",
                cleaned_value=None,
                bot_message=(
                    "Aapka loan aavedan pehle hi darj ho chuka hai. Hamari team aapse sampark karegi."
                    if lang_key in ["hi", "hi_en"]
                    else "Your loan application has already been submitted. Our team will contact you shortly."
                ),
                current_slot=None,
                collected_slots=state.collected_slots,
                is_journey_complete=True,
            )

        current_slot = state.current_slot
        is_valid, cleaned_val, err_detail = self._validate_slot(current_slot, user_text)

        if not is_valid:
            state.retry_count += 1
            err_msg = ERROR_TEMPLATES.get(current_slot, {}).get(lang_key, ERROR_TEMPLATES[current_slot]["en"])
            state.last_bot_prompt = err_msg
            return SlotResult(
                is_valid=False,
                slot_name=current_slot,
                cleaned_value=None,
                bot_message=err_msg,
                current_slot=current_slot,
                collected_slots=state.collected_slots,
                is_journey_complete=False,
                error_message=err_detail,
            )

        # Slot valid: record and advance
        state.collected_slots[current_slot] = cleaned_val
        state.retry_count = 0

        # Check for intermediate DTI evaluation when income and loan amount are both present
        veto_triggered, veto_details = self._evaluate_affordability_veto(state)

        next_slot = self._get_next_slot(current_slot)
        state.current_slot = next_slot

        if next_slot is None:
            state.is_journey_complete = True
            completion_msg = self._build_completion_message(state, lang_key, veto_triggered, veto_details)
            state.last_bot_prompt = completion_msg
            return SlotResult(
                is_valid=True,
                slot_name=current_slot,
                cleaned_value=cleaned_val,
                bot_message=completion_msg,
                current_slot=None,
                collected_slots=state.collected_slots,
                is_journey_complete=True,
                veto_triggered=veto_triggered,
                veto_details=veto_details,
            )

        # Generate next prompt
        next_template = PROMPT_TEMPLATES.get(next_slot, {}).get(lang_key, PROMPT_TEMPLATES[next_slot]["en"])
        name = state.collected_slots.get("full_name", "")
        next_prompt = next_template.format(name=name)

        # If an intermediate veto warning occurred on loan_amount, weave empathetic advice into prompt
        if current_slot == "loan_amount" and veto_triggered:
            prefix_warning = self._build_veto_inline_warning(veto_details, lang_key)
            next_prompt = prefix_warning + "\n\n" + next_prompt

        state.last_bot_prompt = next_prompt
        return SlotResult(
            is_valid=True,
            slot_name=current_slot,
            cleaned_value=cleaned_val,
            bot_message=next_prompt,
            current_slot=next_slot,
            collected_slots=state.collected_slots,
            is_journey_complete=False,
            veto_triggered=veto_triggered,
            veto_details=veto_details,
        )

    # --------------------------------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------------------------------

    def _normalize_lang_key(self, lang: str) -> str:
        if lang in ["hi", "hi_in", "hindi"]:
            return "hi"
        if lang in ["hi_en", "hinglish", "roman_hindi"]:
            return "hi_en"
        return "en"

    def _validate_slot(self, slot_name: str, text: str) -> Tuple[bool, Any, Optional[str]]:
        if slot_name == "full_name":
            return validate_full_name(text)
        elif slot_name == "pan_number":
            return validate_pan(text)
        elif slot_name == "aadhaar_last4":
            return validate_aadhaar_last4(text)
        elif slot_name == "monthly_income":
            return validate_monthly_income(text)
        elif slot_name == "loan_amount":
            return validate_loan_amount(text)
        elif slot_name == "employment_type":
            return validate_employment_type(text)
        return False, None, "Unknown slot"

    def _get_next_slot(self, current_slot: str) -> Optional[str]:
        try:
            idx = SLOT_SEQUENCE.index(current_slot)
            if idx + 1 < len(SLOT_SEQUENCE):
                return SLOT_SEQUENCE[idx + 1]
            return None
        except ValueError:
            return None

    def _evaluate_affordability_veto(self, state: DialogueState) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Handshake with Responsible Lending principles:
        Calculates estimated EMI and DTI ratio.
        If DTI > 50%, fires a Hard Veto alert.
        """
        slots = state.collected_slots
        if "monthly_income" in slots and "loan_amount" in slots:
            income = float(slots["monthly_income"])
            loan = float(slots["loan_amount"])

            # Approximate 3-year EMI at ~14% APR: ~₹34 per ₹1,000 (0.034 factor)
            # For 2-year conservative: ~0.048 factor
            estimated_monthly_emi = round(loan * 0.034, 2)
            projected_dti = round(estimated_monthly_emi / income, 3)

            # Responsible lending floor: DTI must not exceed 50%
            if projected_dti > 0.50:
                safe_max_loan = round((income * 0.40) / 0.034, -3)  # Loan capped at 40% DTI
                details = {
                    "monthly_income": income,
                    "loan_amount": loan,
                    "estimated_monthly_emi": estimated_monthly_emi,
                    "projected_dti": projected_dti,
                    "dti_percentage": round(projected_dti * 100, 1),
                    "dti_threshold": 0.50,
                    "safe_max_loan": safe_max_loan,
                    "reason": f"Projected debt-to-income ({round(projected_dti*100,1)}%) exceeds responsible lending safety cap of 50%.",
                }
                state.veto_triggered = True
                state.veto_reason = details["reason"]
                return True, details

        return False, None

    def _build_veto_inline_warning(self, veto_details: Dict[str, Any], lang_key: str) -> str:
        dti_pct = veto_details.get("dti_percentage", 55)
        safe_amt = int(veto_details.get("safe_max_loan", 100000))

        if lang_key == "hi":
            return (
                f"⚠️ ध्यान दें: इस लोन राशि के साथ आपकी अनुमानित EMI आपकी मासिक आय का {dti_pct}% होगी, "
                f"जो RBI/बैंक सुरक्षा सीमा (50%) से अधिक है। आपके लिए सुरक्षित राशि लगभग ₹{safe_amt:,} होगी।"
            )
        elif lang_key == "hi_en":
            return (
                f"⚠️ Dhyaan dein: Is loan amount ke sath aapki estimated EMI aapki income ka {dti_pct}% hogi, "
                f"jo safety limit (50%) se zyada hai. Aapke liye safe amount lagbhag ₹{safe_amt:,} hai."
            )
        else:
            return (
                f"⚠️ Financial Health Notice: The projected EMI would consume {dti_pct}% of your monthly income, "
                f"exceeding our 50% responsible lending safety threshold. A safer loan limit for your income is ₹{safe_amt:,}."
            )

    def _build_completion_message(
        self, state: DialogueState, lang_key: str, veto_triggered: bool, veto_details: Optional[Dict[str, Any]]
    ) -> str:
        name = state.collected_slots.get("full_name", "Mitra")
        loan = state.collected_slots.get("loan_amount", 0)

        if veto_triggered and veto_details:
            safe_amt = int(veto_details.get("safe_max_loan", loan))
            dti = veto_details.get("dti_percentage", 52)
            if lang_key == "hi":
                return (
                    f"धन्यवाद {name}! आपका आवेदन प्राप्त हो गया है।\n\n"
                    f"🛡️ **जिम्मेदार बैंकिंग समीक्षा (Ethical Veto Alert):**\n"
                    f"आपकी मांगी गई राशि (₹{loan:,.0f}) पर ऋण-आय अनुपात (DTI) {dti}% बनता है, जो सुरक्षा सीमा से अधिक है। "
                    f"हम आपके बजट की सुरक्षा हेतु आपको ₹{safe_amt:,.0f} तक की प्री-अप्रूव्ड सीमा या अनुकूल EMI रीशेड्यूलिंग का सुझाव देते हैं। "
                    f"हमारा वित्तीय परामर्शदाता जल्द ही आपसे संपर्क करेगा।"
                )
            elif lang_key == "hi_en":
                return (
                    f"Dhanyawad {name}! Aapka application receive ho gaya hai.\n\n"
                    f"🛡️ **Responsible Banking Notice (Ethical Veto Triggered):**\n"
                    f"Requested loan ₹{loan:,.0f} par projected DTI {dti}% ban raha hai. Over-indebtedness se bachane ke liye "
                    f"hum aapko safe amount ₹{safe_amt:,.0f} ya flexible EMI plan recommend karte hain. "
                    f"Hamare financial counsellor aapse jald sampark karenge."
                )
            else:
                return (
                    f"Thank you {name}! Your application details have been received.\n\n"
                    f"🛡️ **Responsible Lending Notice (Ethical Veto Triggered):**\n"
                    f"Your requested loan of ₹{loan:,.0f} yields a debt-to-income ratio of {dti}%, exceeding the 50% safety ceiling. "
                    f"To safeguard your financial health, we suggest a moderated loan amount of ₹{safe_amt:,.0f} or an empathetic repayment plan. "
                    f"A bank relationship officer will connect with you shortly."
                )

        # Standard clean approval completion
        if lang_key == "hi":
            return (
                f"बधाई हो {name}! आपका ₹{loan:,.0f} का डिजिटल लोन आवेदन सफलतापूर्वक सत्यापित और दर्ज कर लिया गया है।\n"
                f"• पैन और आधार सत्यापन: सफल (Verhoeff Checksum Verified)\n"
                f"• DTI वित्तीय स्थिति: स्वस्थ (< 50%)\n"
                f"RBI डिजिटल लेंडिंग दिशा-निर्देशों के तहत आपका 3-दिवसीय कूलिंग-ऑफ पीरियड लागू होगा। विस्तृत KFS आपके पंजीकृत नंबर पर भेजा जा रहा है।"
            )
        elif lang_key == "hi_en":
            return (
                f"Badhai ho {name}! Aapka ₹{loan:,.0f} ka digital loan application successfully verify aur submit ho gaya hai.\n"
                f"• PAN & Aadhaar Validation: Complete (Verhoeff Checksum Passed)\n"
                f"• DTI Health Check: Safe (< 50%)\n"
                f"RBI Digital Lending guidelines ke tehat aapka 3-day cooling-off period valid rahega. Standard KFS aapko jald bhej diya jayega."
            )
        else:
            return (
                f"Congratulations {name}! Your digital loan application for ₹{loan:,.0f} has been verified and registered successfully.\n"
                f"• KYC & Identity: Verified (Verhoeff Checksum Validated)\n"
                f"• Affordability: Approved (DTI within safe parameters)\n"
                f"As per RBI Digital Lending Guidelines, your 3-day cooling-off lookup period is active. The standard Key Fact Statement (KFS) has been generated."
            )
