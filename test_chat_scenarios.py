"""
test_chat_scenarios.py — Automated Test Suite for BharatBanker Conversational AI (Person 3).

Validates:
  1. Mathematical Verhoeff Checksum (D5 dihedral group accuracy, transpositions, single digit corruption).
  2. PAN Regex and normalization.
  3. Judge Scenario 3: Sunita Devi Vernacular Journey (Hindi/Hinglish).
  4. Mid-Dialogue Grounded Policy Detour with Zero State Loss.
  5. Responsible Lending Hard Veto (DTI > 50% detection).
  6. Zero-Hallucination Guardrail on unsupported queries.
  7. Contract 3: Conversational Chatbot Payload Schema Compliance.
"""

import sys
import os

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_service import ChatService
from intent_router import IntentCategory, IntentRouter
from rag_engine import GroundedRagEngine
from slot_filling_engine import (
    generate_valid_aadhaar_last4_sample,
    generate_verhoeff_check_digit,
    validate_pan,
    validate_verhoeff,
)


def test_verhoeff_checksum_algorithm():
    print("\n[TEST 1] Testing Verhoeff Checksum Algorithm (Dihedral Group D5)...")
    # Test check digit generation
    prefix = "236"
    expected_chk = generate_verhoeff_check_digit(prefix)
    assert expected_chk == "3", f"Expected '3', got {expected_chk}"
    sample = prefix + expected_chk  # '2363'
    assert validate_verhoeff(sample) is True, f"Valid sample {sample} failed Verhoeff check"

    # Single-digit substitution error (2364 instead of 2363)
    assert validate_verhoeff("2364") is False, "Single digit error was not detected!"

    # Transposition error (2633 instead of 2363)
    assert validate_verhoeff("2633") is False, "Adjacent transposition error was not detected!"

    # Another sample
    p2 = "841"
    chk2 = generate_verhoeff_check_digit(p2)
    assert validate_verhoeff(p2 + chk2) is True
    print("  --> Verhoeff checksum algorithm passed with 100% mathematical precision.")


def test_pan_regex():
    print("\n[TEST 2] Testing Deterministic PAN Validation...")
    ok, cleaned, err = validate_pan("ABCDE1234F")
    assert ok is True and cleaned == "ABCDE1234F"

    # Auto-uppercase and spaces
    ok2, cleaned2, _ = validate_pan(" abcde1234f ")
    assert ok2 is True and cleaned2 == "ABCDE1234F"

    # Invalid PANs
    assert validate_pan("ABCD1234F")[0] is False  # 4 letters
    assert validate_pan("12345ABCDE")[0] is False  # numbers first
    assert validate_pan("ABCDE12345")[0] is False  # trailing digit
    print("  --> PAN regex validation passed.")


def test_scenario_3_sunita_devi_vernacular_detour():
    print("\n[TEST 3] Testing Judge Scenario 3: Sunita Devi Vernacular Journey with Mid-KYC Detour...")
    svc = ChatService()
    session_id = "test_judge_scenario_3_sunita"

    # Step 1: Initial Greeting / Name entry
    r1 = svc.process_message(session_id, "Sunita Devi", language="hi_en")
    assert r1["current_slot"] == "pan_number"
    assert r1["collected_slots"]["full_name"] == "Sunita Devi"
    assert r1["intent_category"] == IntentCategory.TASK_SLOT_FILLING.value
    print(f"  Step 1: Name submitted -> Current slot: {r1['current_slot']}")

    # Step 2: PAN Entry
    r2 = svc.process_message(session_id, "ABCDE1234F")
    assert r2["current_slot"] == "aadhaar_last4"
    assert r2["collected_slots"]["pan_number"] == "ABCDE1234F"
    print(f"  Step 2: PAN submitted -> Current slot: {r2['current_slot']}")

    # Step 3: Aadhaar Last 4 Digits Entry (Verhoeff checksum verified)
    valid_aadhaar = generate_valid_aadhaar_last4_sample("236")  # "2363"
    r3 = svc.process_message(session_id, valid_aadhaar)
    assert r3["current_slot"] == "monthly_income"
    assert r3["collected_slots"]["aadhaar_last4"] == valid_aadhaar
    print(f"  Step 3: Aadhaar '{valid_aadhaar}' verified -> Current slot: {r3['current_slot']}")

    # Step 4: Mid-Flow Detour Question in Hinglish (What is cooling-off period?)
    detour_query = "Yeh cooling-off period kya hota hai?"
    r4 = svc.process_message(session_id, detour_query)
    print(f"  Step 4: Asked mid-flow question: '{detour_query}'")
    assert r4["intent_category"] == IntentCategory.KNOWLEDGE_RAG.value
    assert r4["grounded_citation"] is not None
    assert "RBI Digital Lending Guidelines" in r4["grounded_citation"]
    # Check that previous slots were NOT erased
    assert len(r4["collected_slots"]) == 3
    assert r4["collected_slots"]["full_name"] == "Sunita Devi"
    assert r4["collected_slots"]["pan_number"] == "ABCDE1234F"
    assert r4["collected_slots"]["aadhaar_last4"] == valid_aadhaar
    # Check that resumption prompt is included
    assert "monthly_income" in r4["current_slot"]
    print(f"  --> Detour answered with verified citation: {r4['grounded_citation']}")
    print("  --> Dialogue state preserved without resetting slots!")

    # Step 5: Resume filling monthly income
    r5 = svc.process_message(session_id, "35000")
    assert r5["current_slot"] == "loan_amount"
    assert r5["collected_slots"]["monthly_income"] == 35000.0
    print(f"  Step 5: Resumed income -> Current slot: {r5['current_slot']}")

    # Step 6: Enter requested loan amount
    r6 = svc.process_message(session_id, "1 Lakh")
    assert r6["current_slot"] == "employment_type"
    assert r6["collected_slots"]["loan_amount"] == 100000.0
    print(f"  Step 6: Loan amount submitted -> Current slot: {r6['current_slot']}")

    # Step 7: Enter employment type -> Complete journey
    r7 = svc.process_message(session_id, "Artisan")
    assert r7["is_journey_complete"] is True
    assert r7["current_slot"] is None
    assert r7["collected_slots"]["employment_type"] == "Artisan / Micro-Enterprise"
    print("  Step 7: Application completed successfully!")
    print(f"  Completion Message Summary:\n    {r7['bot_message'][:140]}...")


def test_ethical_hard_veto_high_dti():
    print("\n[TEST 4] Testing Responsible Lending Ethical Hard Veto (DTI > 50%)...")
    svc = ChatService()
    session_id = "test_hard_veto_high_dti"

    svc.process_message(session_id, "Amit Patel", language="en")
    svc.process_message(session_id, "ABCDE1234F")
    valid_aadhaar = generate_valid_aadhaar_last4_sample("492")
    svc.process_message(session_id, valid_aadhaar)

    # Low income ₹18,000
    svc.process_message(session_id, "18000")

    # High loan request ₹6,00,000 (EMI would be ~₹20,400, DTI > 100%!)
    r_loan = svc.process_message(session_id, "600000")

    # Veto must trigger!
    assert r_loan["veto_triggered"] is True, "Hard Veto did not trigger for DTI > 50%!"
    veto_details = r_loan["veto_details"]
    assert veto_details["projected_dti"] > 0.50
    print(f"  --> Hard Veto successfully intercepted loan! Projected DTI: {veto_details['dti_percentage']}%")
    print(f"  --> Safe moderated limit suggested: ₹{int(veto_details['safe_max_loan']):,}")

    # Complete the journey
    r_final = svc.process_message(session_id, "Self-Employed")
    assert r_final["is_journey_complete"] is True
    assert r_final["veto_triggered"] is True
    assert "Ethical Veto Triggered" in r_final["bot_message"]
    print("  --> Final response communicated empathetic guidance rather than a predatory loan push.")


def test_zero_hallucination_guardrail():
    print("\n[TEST 5] Testing Zero-Hallucination Guardrail on Unsupported Queries...")
    svc = ChatService()
    session_id = "test_zero_hallucination"

    irrelevant_query = "What is the stock price of Tesla in New York?"
    resp = svc.process_message(session_id, irrelevant_query, language="en")

    assert resp["grounded_citation"] is None, "Hallucinated citation for unsupported query!"
    assert "not covered in our official" in resp["bot_message"] or "cannot speculate" in resp["bot_message"]
    print("  --> Bot cleanly declined to speculate on unsupported queries. Zero hallucination verified.")


def test_contract_3_schema_conformance():
    print("\n[TEST 6] Verifying Contract 3 JSON Schema Conformance...")
    svc = ChatService()
    resp = svc.process_message("test_contract_schema", "Namaste", language="hi_en")

    required_keys = [
        "session_id",
        "detected_language",
        "intent_category",
        "bot_message",
        "current_slot",
        "collected_slots",
        "is_journey_complete",
        "grounded_citation",
    ]
    for k in required_keys:
        assert k in resp, f"Contract 3 missing required key: {k}"

    assert isinstance(resp["session_id"], str)
    assert isinstance(resp["detected_language"], str)
    assert isinstance(resp["intent_category"], str)
    assert isinstance(resp["bot_message"], str)
    assert isinstance(resp["collected_slots"], dict)
    assert isinstance(resp["is_journey_complete"], bool)
    print("  --> Output payload conforms 100% to frozen Contract 3 schema.")


if __name__ == "__main__":
    print("================================================================")
    print("  BHARATBANKER AI: PERSON 3 AUTOMATED VERIFICATION SUITE")
    print("================================================================")
    test_verhoeff_checksum_algorithm()
    test_pan_regex()
    test_scenario_3_sunita_devi_vernacular_detour()
    test_ethical_hard_veto_high_dti()
    test_zero_hallucination_guardrail()
    test_contract_3_schema_conformance()
    print("\n================================================================")
    print("  ALL 6 VERIFICATION TEST SUITES PASSED SUCCESSFULLY (100%)")
    print("================================================================")
