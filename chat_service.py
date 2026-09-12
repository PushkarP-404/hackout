"""
chat_service.py — Unified Conversational AI Controller for BharatBanker AI.

Author: Person 3 (Conversational AI & Multilingual RAG Lead)
Scope: Sub-Problem 2 (Vernacular-First Conversational Banking)
Standards:
  - Strict compliance with Contract 3: Conversational Chatbot Payload.
  - Seamless coordination between slot-filling and grounded RAG knowledge retrieval.
  - Zero state loss during mid-KYC policy detours.
  - Ethical Hard Veto handshake for Person 2 & Person 4 consumption.
"""

from typing import Any, Dict, Optional

from intent_router import IntentCategory, IntentRouter
from rag_engine import GroundedRagEngine
from slot_filling_engine import SlotFillingEngine


class ChatService:
    """High-level facade orchestrating vernacular loan applications,
    regulatory policy Q&A, and mid-dialogue detours.
    """

    def __init__(self):
        self.slot_engine = SlotFillingEngine()
        self.rag_engine = GroundedRagEngine()
        self.router = IntentRouter()
        self._is_rag_ready = False

    def _ensure_rag_ready(self) -> None:
        if not self._is_rag_ready:
            self.rag_engine.initialize()
            self._is_rag_ready = True

    def process_message(
        self,
        session_id: str,
        user_text: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main entry point processing an inbound message.
        Conforms strictly to Contract 3: Conversational Chatbot Payload.

        Returns:
            Dict conforming to Contract 3:
            {
                "session_id": str,
                "detected_language": str,
                "intent_category": str,
                "bot_message": str,
                "current_slot": Optional[str],
                "collected_slots": Dict[str, Any],
                "is_journey_complete": bool,
                "grounded_citation": Optional[str],
                # Supplementary metadata for Person 2 (Veto) & Person 4 (UI):
                "veto_triggered": bool,
                "veto_details": Optional[dict]
            }
        """
        self._ensure_rag_ready()
        clean_text = user_text.strip()

        # Retrieve current session state
        state = self.slot_engine.get_or_create_state(
            session_id,
            default_language=language if language else "hi_en"
        )
        current_slot = state.current_slot
        is_journey_active = not state.is_journey_complete

        # 1. Per-Turn Intent Routing & Language Detection
        intent, detected_lang = self.router.route_turn(
            clean_text,
            current_slot=current_slot,
            is_journey_active=is_journey_active
        )
        if language:
            detected_lang = language
        state.detected_language = detected_lang

        # ----------------------------------------------------------------------
        # 2. Case A: Reset or Cancel Request
        # ----------------------------------------------------------------------
        if intent == IntentCategory.RESET_FLOW:
            self.slot_engine.reset_journey(session_id, language=detected_lang)
            welcome_msg = self.slot_engine.get_welcome_message(session_id, language=detected_lang)
            return {
                "session_id": session_id,
                "detected_language": detected_lang,
                "intent_category": IntentCategory.RESET_FLOW.value,
                "bot_message": welcome_msg,
                "current_slot": "full_name",
                "collected_slots": {},
                "is_journey_complete": False,
                "grounded_citation": None,
                "veto_triggered": False,
                "veto_details": None,
            }

        # ----------------------------------------------------------------------
        # 3. Case B: Greeting
        # ----------------------------------------------------------------------
        if intent == IntentCategory.GREETING and not state.collected_slots:
            welcome_msg = self.slot_engine.get_welcome_message(session_id, language=detected_lang)
            return {
                "session_id": session_id,
                "detected_language": detected_lang,
                "intent_category": IntentCategory.GREETING.value,
                "bot_message": welcome_msg,
                "current_slot": "full_name",
                "collected_slots": {},
                "is_journey_complete": False,
                "grounded_citation": None,
                "veto_triggered": False,
                "veto_details": None,
            }

        # ----------------------------------------------------------------------
        # 4. Case C: Knowledge Detour (RAG Policy Question)
        # ----------------------------------------------------------------------
        if intent == IntentCategory.KNOWLEDGE_RAG:
            # Query official regulatory repository
            rag_res = self.rag_engine.search(clean_text, language=detected_lang)

            if is_journey_active:
                # Freeze state and construct seamless return prompt
                self.slot_engine.freeze_for_detour(session_id)
                resumption_prompt = self.slot_engine.resume_after_detour(session_id, language=detected_lang)
                combined_message = f"{rag_res.bot_message}\n\n---\n{resumption_prompt}"
            else:
                combined_message = rag_res.bot_message

            return {
                "session_id": session_id,
                "detected_language": detected_lang,
                "intent_category": IntentCategory.KNOWLEDGE_RAG.value,
                "bot_message": combined_message,
                "current_slot": state.current_slot,
                "collected_slots": state.collected_slots,
                "is_journey_complete": state.is_journey_complete,
                "grounded_citation": rag_res.grounded_citation,
                "veto_triggered": state.veto_triggered,
                "veto_details": getattr(state, "veto_details", None),
            }

        # ----------------------------------------------------------------------
        # 5. Case D: Standard Task Slot Filling (Loan Application)
        # ----------------------------------------------------------------------
        slot_res = self.slot_engine.process_turn(session_id, clean_text, language=detected_lang)

        return {
            "session_id": session_id,
            "detected_language": detected_lang,
            "intent_category": IntentCategory.TASK_SLOT_FILLING.value,
            "bot_message": slot_res.bot_message,
            "current_slot": slot_res.current_slot,
            "collected_slots": slot_res.collected_slots,
            "is_journey_complete": slot_res.is_journey_complete,
            "grounded_citation": None,
            "veto_triggered": slot_res.veto_triggered,
            "veto_details": slot_res.veto_details,
        }

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Returns customer data formatted for Person 2 Veto Layer or Person 4 Dashboard."""
        state = self.slot_engine.get_or_create_state(session_id)
        if not state.collected_slots:
            return None
        return {
            "session_id": session_id,
            "name": state.collected_slots.get("full_name"),
            "pan_number": state.collected_slots.get("pan_number"),
            "aadhaar_last4": state.collected_slots.get("aadhaar_last4"),
            "monthly_income": state.collected_slots.get("monthly_income"),
            "loan_amount": state.collected_slots.get("loan_amount"),
            "employment_type": state.collected_slots.get("employment_type"),
            "is_journey_complete": state.is_journey_complete,
            "veto_triggered": state.veto_triggered,
            "veto_reason": state.veto_reason,
        }


# ==============================================================================
# CLI INTERACTIVE TESTING UTILITY
# ==============================================================================

if __name__ == "__main__":
    import sys
    print("=== BharatBanker Conversational AI Test Console ===")
    print("Type your message in Hindi, Hinglish, or English. Type 'exit' to quit.\n")

    svc = ChatService()
    session = "cli_demo_session"

    # Start with welcome
    init_resp = svc.process_message(session, "namaste")
    print(f"Bot: {init_resp['bot_message']}\n")

    while True:
        try:
            user_in = input("User: ").strip()
            if not user_in:
                continue
            if user_in.lower() in ["exit", "quit"]:
                break
            resp = svc.process_message(session, user_in)
            print(f"\nBot [{resp['intent_category']} | Lang: {resp['detected_language']}]:")
            print(resp["bot_message"])
            if resp.get("grounded_citation"):
                print(f"Citation: {resp['grounded_citation']}")
            if resp.get("veto_triggered"):
                print(f"** ETHICAL VETO TRIGGERED ** (DTI: {resp['veto_details'].get('dti_percentage')}%)")
            print(f"Current Slot: {resp['current_slot']} | Completed: {resp['is_journey_complete']}\n")
        except (KeyboardInterrupt, EOFError):
            break
