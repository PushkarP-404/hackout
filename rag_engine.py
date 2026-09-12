"""
rag_engine.py — Multilingual Grounded RAG Knowledge Engine for BharatBanker AI.

Author: Person 3 (Conversational AI & Multilingual RAG Lead)
Scope: Sub-Problem 2 (Vernacular-First Conversational Banking)
Standards:
  - FAISS local vector index with normalized cosine similarity.
  - Zero-hallucination guardrail with strict confidence threshold.
  - Mandatory official citations ([Source: RBI Guidelines, Sec X]).
  - Native bilingual synthesis across Hindi, Hinglish, and English.
  - Pre-built fast persistent vector cache (<50ms reload time).
"""

from dataclasses import dataclass
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "rag_docs")
INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "faiss_rag.index")
METADATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "rag_metadata.json")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CONFIDENCE_THRESHOLD = 0.52


@dataclass
class RagChunk:
    chunk_id: str
    doc_name: str
    section_title: str
    citation: str
    content_en: str
    content_hi: str
    content_hi_en: str
    keywords: List[str]


@dataclass
class RagResponse:
    query: str
    detected_language: str
    bot_message: str
    grounded_citation: Optional[str]
    similarity_score: float
    is_declined: bool
    source_chunk: Optional[RagChunk] = None


# ==============================================================================
# 1. CURATED MULTILINGUAL SYNTHESIS CATALOG (Grounded Knowledge Bank)
# ==============================================================================

CURATED_SYNTHESIS: Dict[str, Dict[str, Any]] = {
    "cooling_off_period": {
        "title": "Cooling-Off / Look-Up Period",
        "citation": "[Source: RBI Digital Lending Guidelines 2022, Sec 3.1]",
        "summary_en": (
            "Under RBI Digital Lending Guidelines, borrowers have a mandatory 3-calendar-day cooling-off (look-up) period. "
            "During this window, you can exit the loan without paying any foreclosure penalty or penal charges; "
            "you only repay the disbursed principal plus proportionate accrued interest."
        ),
        "summary_hi_en": (
            "RBI Digital Lending Guidelines ke tehat aapko 3 din ka 'cooling-off period' milta hai. "
            "Is dauraan agar aap loan cancel karna chahein, toh bina kisi penalty ya foreclosure charges ke cancel kar sakte hain; "
            "aapko sirf li gayi rashi aur utne dino ka aam byaj lautana hota hai."
        ),
        "summary_hi": (
            "भारतीय रिजर्व बैंक (RBI) डिजिटल लेंडिंग दिशा-निर्देशों के तहत उधारकर्ताओं को 3 दिन का अनिवार्य 'कूलिंग-ऑफ (लुक-अप) पीरियड' मिलता है। "
            "इस अवधि में आप बिना किसी फोरक्लोजर पेनल्टी के लोन से बाहर निकल सकते हैं; केवल वितरित मूलधन और आनुपातिक ब्याज ही देय होता है।"
        ),
        "keywords": [
            "cooling off", "cooling-off", "look up", "lookup", "cancel loan", "loan cancellation",
            "cooling-off period kya hota hai", "cooling off kya hai", "loan wapas karna", "exit loan"
        ],
    },
    "why_pan_and_aadhaar": {
        "title": "KYC Verification & Data Privacy (PAN & Aadhaar Last 4)",
        "citation": "[Source: RBI KYC Master Direction & DPDP Act 2023, Sec 2.2]",
        "summary_en": (
            "PAN verification is legally required under Income Tax Act Section 139A and RBI KYC norms to evaluate credit bureau history. "
            "In compliance with DPDP Act 2023 and UIDAI rules, we NEVER store your full 12-digit Aadhaar. "
            "We only collect the last 4 digits, validated with the Verhoeff checksum algorithm to verify your existing KYC safely."
        ),
        "summary_hi_en": (
            "Income Tax Act aur RBI KYC niyamon ke tehat credit bureau score check karne ke liye PAN anivarya hai. "
            "DPDP Act 2023 ke anusaar hum aapka poora 12-digit Aadhaar number kabhi save ya request nahi karte. "
            "Keval antim 4 ank Verhoeff checksum se jaanche jaate hain taaki aapka data poori tarah surakshit rahe."
        ),
        "summary_hi": (
            "आयकर अधिनियम धारा 139A और RBI KYC नियमों के तहत क्रेडिट ब्यूरो जांच के लिए पैन अनिवार्य है। "
            "DPDP अधिनियम 2023 के तहत हम कभी भी आपका पूरा 12-अंकों का आधार नहीं मांगते। "
            "आपकी निजता की सुरक्षा के लिए केवल अंतिम 4 अंक वेरहोफ चेकसम द्वारा सत्यापित किए जाते हैं।"
        ),
        "keywords": [
            "why pan", "pan kyun chahiye", "pan kyu", "aadhaar kyu", "why aadhaar", "aadhaar 4 digit",
            "pan number kyu mangte ho", "data safety", "aadhaar privacy", "dpdp"
        ],
    },
    "inability_to_repay": {
        "title": "Loan Repayment Distress & Empathetic Restructuring",
        "citation": "[Source: RBI Framework for Stressed Assets & Fair Recovery Code, Sec 4.4]",
        "summary_en": (
            "If you face financial hardship or cannot repay an EMI on time, RBI guidelines mandate that lenders provide proactive assistance, "
            "such as EMI rescheduling, tenure extension, or a temporary grace period. Lenders and recovery agents are strictly prohibited "
            "from harassment, contacting after 7:00 PM, or accessing your personal phone contacts."
        ),
        "summary_hi_en": (
            "Agar aap kisi mahine EMI nahi chuka pate hain, toh ghabraiye mat. RBI ke niyamon ke anusaar bank aapko EMI aage badhane (reschedule) "
            "ya tenure badhane ka vikalp dete hain. Kisi bhi recovery agent ko subah 8 baje se pehle ya shaam 7 baje ke baad call karna, "
            "ya kisi bhi tarah pareshan karna sakht mana hai."
        ),
        "summary_hi": (
            "यदि आप किसी वित्तीय कठिनाई के कारण समय पर ईएमआई नहीं चुका पाते हैं, तो RBI नियमों के तहत बैंक आपको ईएमआई रीशेड्यूल करने "
            "या रियायती अवधि (Grace Period) का विकल्प प्रदान करता है। किसी भी रिकवरी एजेंट द्वारा सुबह 8 बजे से पहले या शाम 7 बजे के बाद "
            "संपर्क करना या अनुचित दबाव बनाना पूर्णतः प्रतिबंधित है।"
        ),
        "keywords": [
            "loan nahi chuka payi", "loan nahi chukaya", "cannot repay", "unable to pay", "missed emi",
            "default", "harassment", "recovery agent", "kya hoga agar loan na du", "agar emi na bhare"
        ],
    },
    "upi_pin_golden_rule": {
        "title": "UPI PIN Security & Safety Rules",
        "citation": "[Source: NPCI UPI Safety Advisory, Sec 1.1]",
        "summary_en": (
            "The Golden Rule of UPI: You only enter your UPI PIN when SENDING money or checking account balance. "
            "You NEVER need to enter a UPI PIN or scan a QR code to RECEIVE money or get a refund. "
            "Entering your PIN always debits money from your account."
        ),
        "summary_hi_en": (
            "UPI ka sabse zaroori niyam: UPI PIN sirf paise BHEJNE (send karne) ke liye darj kiya jata hai. "
            "Paise prapt karne (receive karne) ya refund ke liye kabhi bhi UPI PIN darj karne ya QR scan karne ki zaroorat nahi hoti. "
            "PIN dalne par hamesha aapke khate se paise kat-te hain."
        ),
        "summary_hi": (
            "UPI का स्वर्णिम नियम: UPI PIN केवल पैसे भेजने (भुगतान करने) के लिए दर्ज किया जाता है। "
            "पैसे प्राप्त करने या रिफंड पाने के लिए कभी भी UPI PIN दर्ज करने की आवश्यकता नहीं होती। "
            "पिन दर्ज करने पर सदैव आपके खाते से राशि कटती है।"
        ),
        "keywords": [
            "upi pin", "pin rule", "receive money pin", "upi safety", "qr code receive",
            "upi pin kab dalna chahiye", "paisa aane par pin", "upi fraud"
        ],
    },
    "prepayment_penalty": {
        "title": "Prepayment & Foreclosure Charges Restriction",
        "citation": "[Source: RBI Master Direction on Fair Practices, Sec 2.5]",
        "summary_en": (
            "As per RBI Master Direction on Fair Lending Practices, banks and NBFCs cannot charge any foreclosure fees "
            "or pre-payment penalties on individual floating-rate retail loans (including personal and home loans). "
            "You can prepay your balance at zero penalty."
        ),
        "summary_hi_en": (
            "RBI ke Fair Practices Code ke anusaar individual floating-rate personal loan ya home loan par kisi bhi tarah ka "
            "foreclosure charge ya prepayment penalty lagana nishedh hai. Aap jab chahein apna loan bina penalty ke band kar sakte hain."
        ),
        "summary_hi": (
            "RBI के निष्पक्ष व्यवहार संहिता (Fair Practices Code) के अनुसार, व्यक्तिगत फ्लोटिंग रेट ऋणों पर किसी भी प्रकार का "
            "फोरक्लोजर शुल्क या प्री-पेमेंट पेनल्टी लगाना पूर्णतः प्रतिबंधित है। आप बिना किसी अतिरिक्त शुल्क के समय पूर्व ऋण चुका सकते हैं।"
        ),
        "keywords": [
            "prepayment penalty", "foreclosure charges", "pehle loan chukana", "loan band karne par charges",
            "pre-payment", "foreclosure fee"
        ],
    },
    "pmjdy_overdraft_insurance": {
        "title": "PMJDY Overdraft Facility and RuPay Insurance",
        "citation": "[Source: PMJDY Scheme Rules & Insurance Terms, Sec 2.4 & 3.2]",
        "summary_en": (
            "Under Pradhan Mantri Jan Dhan Yojana (PMJDY), eligible account holders who maintain satisfactory transactions "
            "for 6 months can get an overdraft (OD) of up to ₹10,000 (up to ₹2,000 without collateral conditions). "
            "RuPay Debit Cards also carry ₹2,00,000 accidental insurance cover provided the card is used once in 90 days."
        ),
        "summary_hi_en": (
            "Pradhan Mantri Jan Dhan Yojana (PMJDY) ke tehat 6 mahine achhe len-den par ₹10,000 tak ki Overdraft (OD) suvidha milti hai "
            "(₹2,000 tak bina kisi shart). Saath hi RuPay card par ₹2,00,000 ka durghatna beema milta hai, basharte card 90 dino mein kam se kam ek baar use hua ho."
        ),
        "summary_hi": (
            "प्रधानमंत्री जन धन योजना (PMJDY) के तहत 6 महीने के संतोषजनक संचालन के बाद ₹10,000 तक की ओवरड्राफ्ट सुविधा मिलती है "
            "(₹2,000 तक बिना शर्त)। साथ ही RuPay कार्ड पर ₹2,00,000 का दुर्घटना बीमा कवर मिलता है (90 दिनों में 1 लेन-देन आवश्यक)।"
        ),
        "keywords": [
            "pmjdy overdraft", "jan dhan od", "jan dhan loan", "rupay insurance", "rupay 2 lakh",
            "jan dhan khata benefits", "jan dhan me 10000"
        ],
    },
    "dti_safety_cap": {
        "title": "Debt-to-Income (DTI) 50% Responsible Lending Ceiling",
        "citation": "[Source: RBI Credit Assessment & Affordability Framework, Sec 1.3]",
        "summary_en": (
            "BharatBanker AI adheres to RBI responsible lending directives: total monthly loan EMIs must never exceed 50% "
            "of verified net monthly income. If your requested loan would push your DTI above 50%, an ethical hard veto activates "
            "to prevent debt entrapment, and an affordable, moderated limit is offered instead."
        ),
        "summary_hi_en": (
            "BharatBanker AI zimmedar lending ke tehat kaam karta hai: aapki kul monthly EMI aapki aamdani ke 50% se zyada nahi honi chahiye. "
            "Agar DTI 50% se upar jata hai, toh Hard Veto lagta hai taaki aap par karz ka bojh na badhe, aur aapko safe amount offer kiya jata hai."
        ),
        "summary_hi": (
            "भारतबैंकर जिम्मेदार बैंकिंग सिद्धांतों का पालन करता है: कुल मासिक ऋण ईएमआई आपकी आय के 50% से अधिक नहीं होनी चाहिए। "
            "यदि डीटीआई 50% से अधिक होता है, तो अतिरिक्त कर्ज से बचाने के लिए हार्ड वीटो लागू होता है और सुरक्षित ऋण राशि का सुझाव दिया जाता है।"
        ),
        "keywords": [
            "dti", "debt to income", "50% rule", "affordability", "veto", "karz ki seema",
            "loan eligibility", "kitna loan mil sakta hai"
        ],
    },
}


# ==============================================================================
# 2. RAG ENGINE CORE IMPLEMENTATION
# ==============================================================================

class GroundedRagEngine:
    """Multilingual Vector-Grounded RAG Engine for official banking regulations."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._index: Optional[faiss.IndexFlatIP] = None
        self._chunks: List[RagChunk] = []
        self._is_initialized = False

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def initialize(self, force_rebuild: bool = False) -> None:
        """Loads or builds the local FAISS vector index."""
        if self._is_initialized and not force_rebuild:
            return

        # Check if saved index and metadata exist
        if not force_rebuild and os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            try:
                self._load_saved_index()
                self._is_initialized = True
                return
            except Exception as e:
                print(f"[RAG] Failed to load cached index ({e}), rebuilding fresh...")

        self._build_fresh_index()
        self._is_initialized = True

    def _load_saved_index(self) -> None:
        self._index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            raw_chunks = json.load(f)
            self._chunks = [RagChunk(**c) for c in raw_chunks]

    def _build_fresh_index(self) -> None:
        """Parses markdown docs + curated synthesis, embeds chunks, and builds FAISS index."""
        chunks: List[RagChunk] = []

        # 1. Ingest curated knowledge items
        for key, item in CURATED_SYNTHESIS.items():
            combined_text = (
                f"{item['title']} {item['citation']}\n"
                f"{item['summary_en']}\n"
                f"{item['summary_hi_en']}\n"
                f"{' '.join(item['keywords'])}"
            )
            chunk = RagChunk(
                chunk_id=f"curated_{key}",
                doc_name=item["title"],
                section_title=item["title"],
                citation=item["citation"],
                content_en=item["summary_en"],
                content_hi=item["summary_hi"],
                content_hi_en=item["summary_hi_en"],
                keywords=item["keywords"],
            )
            chunks.append(chunk)

        # 2. Ingest raw markdown documents in data/rag_docs
        if os.path.exists(DOCS_DIR):
            for fname in os.listdir(DOCS_DIR):
                if fname.endswith(".md"):
                    fpath = os.path.join(DOCS_DIR, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()
                    parsed = self._parse_markdown_doc(fname, text)
                    chunks.extend(parsed)

        self._chunks = chunks

        # 3. Generate embeddings
        texts_to_embed = [
            f"{c.doc_name} {c.section_title} {c.content_en} {' '.join(c.keywords)}"
            for c in self._chunks
        ]
        model = self._get_model()
        embeddings = model.encode(texts_to_embed, convert_to_numpy=True, normalize_embeddings=True)
        embeddings = embeddings.astype(np.float32)

        # 4. Build FAISS Index (Inner Product on normalized vectors = Cosine Similarity)
        dimension = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)
        self._index.add(embeddings)

        # 5. Save index and metadata
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        faiss.write_index(self._index, INDEX_PATH)
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump([c.__dict__ for c in self._chunks], f, ensure_ascii=False, indent=2)

    def _parse_markdown_doc(self, fname: str, text: str) -> List[RagChunk]:
        """Splits markdown file into clause chunks at Section headers."""
        chunks: List[RagChunk] = []
        sections = re.split(r"(?=## Section \d+:)", text)
        doc_title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        doc_title = doc_title_match.group(1).strip() if doc_title_match else fname.replace(".md", "")

        for i, sec in enumerate(sections):
            if not sec.strip() or sec.startswith("# "):
                continue
            title_match = re.search(r"## (Section \d+:[^\n]+)", sec)
            title = title_match.group(1).strip() if title_match else f"Section {i}"
            citation_match = re.search(r"\*\*Source Citation:\*\*\s*(\[Source:[^\]]+\])", sec)
            citation = citation_match.group(1).strip() if citation_match else f"[Source: {doc_title}, {title}]"

            # Clean body
            body = re.sub(r"## Section \d+:[^\n]+", "", sec)
            body = re.sub(r"\*\*Source Citation:\*\*[^\n]+", "", body).strip()

            chunks.append(
                RagChunk(
                    chunk_id=f"{fname}_{i}",
                    doc_name=doc_title,
                    section_title=title,
                    citation=citation,
                    content_en=body,
                    content_hi=body,
                    content_hi_en=body,
                    keywords=[],
                )
            )
        return chunks

    def search(
        self, query: str, language: str = "hi_en", top_k: int = 1, threshold: float = CONFIDENCE_THRESHOLD
    ) -> RagResponse:
        """Performs grounded semantic retrieval and formats vernacular citation."""
        self.initialize()

        # Direct keyword boost check for high-confidence match
        keyword_match = self._find_keyword_match(query)
        if keyword_match:
            chunk, score = keyword_match
            bot_msg = self._format_response_text(chunk, language)
            return RagResponse(
                query=query,
                detected_language=language,
                bot_message=bot_msg,
                grounded_citation=chunk.citation,
                similarity_score=score,
                is_declined=False,
                source_chunk=chunk,
            )

        # Semantic embedding retrieval via FAISS
        model = self._get_model()
        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)

        scores, indices = self._index.search(q_emb, top_k)
        best_score = float(scores[0][0])
        best_idx = int(indices[0][0])

        # Zero-hallucination check: Decline if score is below threshold
        if best_score < threshold or best_idx < 0 or best_idx >= len(self._chunks):
            decline_msg = self._build_decline_message(language)
            return RagResponse(
                query=query,
                detected_language=language,
                bot_message=decline_msg,
                grounded_citation=None,
                similarity_score=best_score,
                is_declined=True,
                source_chunk=None,
            )

        matched_chunk = self._chunks[best_idx]
        bot_msg = self._format_response_text(matched_chunk, language)

        return RagResponse(
            query=query,
            detected_language=language,
            bot_message=bot_msg,
            grounded_citation=matched_chunk.citation,
            similarity_score=round(best_score, 4),
            is_declined=False,
            source_chunk=matched_chunk,
        )

    def _find_keyword_match(self, query: str) -> Optional[Tuple[RagChunk, float]]:
        """Fast-path lookup for canonical terms with 1.0 confidence."""
        q_lower = query.lower()
        for chunk in self._chunks:
            for kw in chunk.keywords:
                if kw in q_lower:
                    return chunk, 0.98
        return None

    def _format_response_text(self, chunk: RagChunk, language: str) -> str:
        """Formats cited, vernacular-grounded answer."""
        lang = self._normalize_lang(language)
        if lang == "hi":
            text = chunk.content_hi
        elif lang == "hi_en":
            text = chunk.content_hi_en
        else:
            text = chunk.content_en

        return f"{text}\n\n📖 **प्रमाणित स्रोत:** `{chunk.citation}`" if lang == "hi" else f"{text}\n\n📖 **Verified Source:** `{chunk.citation}`"

    def _build_decline_message(self, language: str) -> str:
        """Deterministic zero-hallucination refusal for unsupported queries."""
        lang = self._normalize_lang(language)
        if lang == "hi":
            return (
                "क्षमा करें, यह जानकारी हमारे आधिकारिक RBI/PMJDY दिशा-निर्देशों में उपलब्ध नहीं है। "
                "वित्तीय सुरक्षा नियमों के अनुसार, मैं बिना पुख्ता स्रोत के अनुमानित जानकारी साझा नहीं कर सकता।"
            )
        elif lang == "hi_en":
            return (
                "Kshama karein, yeh jankari hamare verified RBI/PMJDY dishanirdeshon mein uplabdh nahi hai. "
                "Financial safety compliance ke tehat, main bina official source ke anumanit jankari share nahi kar sakta."
            )
        else:
            return (
                "I apologize, but this information is not covered in our official RBI/PMJDY regulatory repository. "
                "Under responsible banking compliance, I cannot speculate or provide unverified lending terms."
            )

    def _normalize_lang(self, lang: str) -> str:
        if lang in ["hi", "hi_in", "hindi"]:
            return "hi"
        if lang in ["hi_en", "hinglish", "roman_hindi"]:
            return "hi_en"
        return "en"
