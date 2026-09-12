"""
==============================================================================
BHARATBANKER AI — TEST VETO SCENARIOS
test_veto_scenarios.py
==============================================================================

Role Ownership: Person 2 (Risk ML & Veto Systems Lead)
Purpose: Validate all 5 canonical scenarios demonstrating ethical veto enforcement,
moral hazard safeguards, fraud lockout, and proactive assistance.

Adheres strictly to:
- team_distribution.md (Section 4 Contract 2, Section 6 Judge Scenarios)
- AGENTS.md & CLAUDE.md (Non-negotiable ethical hard veto floor)
- financial_health_and_fraud_monitor_guide.md (Section 5 & 13)
"""

import unittest
from veto_decision_layer import EmpatheticPolicyEngine, GraceTokenWallet, evaluate_veto_layer


class TestBharatBankerVetoScenarios(unittest.TestCase):

    def setUp(self):
        self.sample_recs = [
            {"product_type": "PERSONAL_LOAN", "raw_propensity_score": 0.88, "shap_reasons": ["High transaction count"]},
            {"product_type": "CREDIT_CARD", "raw_propensity_score": 0.76, "shap_reasons": ["Regular merchant spends"]},
            {"product_type": "HEALTH_INSURANCE", "raw_propensity_score": 0.65, "shap_reasons": ["Surge in medical expenses"]},
            {"product_type": "SIP_INVESTMENT", "raw_propensity_score": 0.72, "shap_reasons": ["Monthly surplus balance"]}
        ]

    def test_scenario_1_fraud_security_shield_lockout(self):
        """
        Scenario 1: Fraud Security Shield Challenge (Tier 1 Lockout).
        When Phi_F >= 0.60 or an untrusted device/SIM swap is detected,
        all empathy options and credit pushes must be strictly locked.
        """
        outcome = EmpatheticPolicyEngine.evaluate(
            customer_id="CUST_FRAUD_SUSPECT",
            phi_f=0.82, # High fraud polarity
            phi_s=0.15,
            health_data={"composite_score": 35.0, "vector": {"buffer": 15.0, "debt": 30.0, "stability": 40.0, "spend": 45.0}},
            customer_profile={"device_is_untrusted": True, "recent_sim_change": True, "dti_ratio": 0.52},
            next_emi_due_days=2,
            emi_amount=5000.0,
            projected_balance=1000.0
        )

        self.assertTrue(outcome["veto_triggered"])
        self.assertFalse(outcome["empathy_unlocked"])
        self.assertEqual(outcome["final_action"]["action_type"], "SECURITY_CHALLENGE")
        self.assertEqual(outcome["final_action"]["cta_action"], "STEP_UP_BIOMETRIC_KYC")
        self.assertIn("PERSONAL_LOAN", outcome["blocked_products"])
        self.assertIn("hash_signature", outcome["audit_trail"])

    def test_scenario_2_pre_bounce_shortfall_with_grace_token(self):
        """
        Scenario 2: Pre-Bounce Shortfall with Grace Token Available (Tier 2 & 3).
        T-2 days before EMI, customer has available tokens.
        Must offer 25% commitment co-pay split and 7-day grace window.
        """
        wallet = GraceTokenWallet(available_tokens=2, on_time_streak=2)
        outcome = EmpatheticPolicyEngine.evaluate(
            customer_id="CUST_AMIT_PATEL",
            phi_f=0.08,
            phi_s=0.88,
            health_data={"composite_score": 44.0, "vector": {"buffer": 22.0, "debt": 42.0, "stability": 55.0, "spend": 60.0}},
            customer_profile={"device_is_untrusted": False, "grace_tokens_available": 2, "dti_ratio": 0.44},
            next_emi_due_days=2,
            emi_amount=8000.0,
            projected_balance=2500.0,
            token_wallet=wallet
        )

        self.assertTrue(outcome["veto_triggered"])
        self.assertTrue(outcome["empathy_unlocked"])
        self.assertEqual(outcome["final_action"]["action_type"], "EMPATHETIC_INTERVENTION")
        self.assertEqual(outcome["final_action"]["cta_action"], "ACTIVATE_GRACE_TOKEN")
        
        # Verify 25% Skin-in-the-game Co-pay
        options = outcome["final_action"]["intervention_options"]
        self.assertEqual(len(options), 2)
        split_opt = next(opt for opt in options if opt["option_id"] == "SPLIT_EMI_WITH_COPAY")
        self.assertEqual(split_opt["copay_amount"], 2000.0) # 25% of 8000
        self.assertEqual(split_opt["deferred_amount"], 6000.0)
        self.assertEqual(split_opt["deferral_days"], 14)

    def test_scenario_3_moral_hazard_tokens_exhausted(self):
        """
        Scenario 3: Moral Hazard Guard (Tokens Exhausted).
        Customer has already used their 2 annual tokens.
        Free grace/split is BLOCKED; offer structural tenure extension (+3 to +6 months).
        """
        wallet = GraceTokenWallet(available_tokens=0, on_time_streak=1)
        outcome = EmpatheticPolicyEngine.evaluate(
            customer_id="CUST_EXHAUSTED_01",
            phi_f=0.12,
            phi_s=0.79,
            health_data={"composite_score": 46.0, "vector": {"buffer": 20.0, "debt": 45.0, "stability": 48.0, "spend": 50.0}},
            customer_profile={"device_is_untrusted": False, "grace_tokens_available": 0, "dti_ratio": 0.42},
            next_emi_due_days=3,
            emi_amount=6000.0,
            projected_balance=1000.0,
            token_wallet=wallet
        )

        self.assertTrue(outcome["veto_triggered"])
        self.assertEqual(outcome["grace_tokens_remaining"], 0)
        self.assertEqual(outcome["final_action"]["action_type"], "EMPATHETIC_RESTRUCTURING")
        self.assertEqual(outcome["final_action"]["cta_action"], "APPLY_TENURE_RESTRUCTURING")
        self.assertIn("APPLY_TENURE_RESTRUCTURING", outcome["final_action"]["cta_action"])

    def test_scenario_4_temporary_cashflow_gap_mini_bridge(self):
        """
        Scenario 4: Temporary Inflow Shock / Harvest Delay (Branch 3B).
        Pristine borrower (Debt Pillar >= 60) suffers sudden income delay (Buffer < 30, Stability < 40).
        System offers 0% interest emergency mini-bridge overdraft facility.
        """
        outcome = EmpatheticPolicyEngine.evaluate(
            customer_id="CUST_FARMER_RAMESH",
            phi_f=0.04,
            phi_s=0.82,
            health_data={"composite_score": 58.0, "vector": {"buffer": 18.0, "debt": 78.0, "stability": 32.0, "spend": 75.0}},
            customer_profile={"device_is_untrusted": False, "grace_tokens_available": 2, "dti_ratio": 0.28},
            next_emi_due_days=12, # not in T-4 pre-bounce window
            emi_amount=4000.0,
            projected_balance=6000.0
        )

        self.assertTrue(outcome["veto_triggered"])
        self.assertEqual(outcome["final_action"]["cta_action"], "ACTIVATE_MINI_BRIDGE")
        self.assertIn("0% Interest Emergency Bridge", outcome["final_action"]["display_title"])

    def test_scenario_5_healthy_borrower_proactive_flow(self):
        """
        Scenario 5: Healthy Account (Proactive Hyper-Personalization).
        Unrestricted flow. Credit veto is false, product push allowed.
        """
        outcome = EmpatheticPolicyEngine.evaluate(
            customer_id="CUST_PRIYA_SHARMA",
            phi_f=0.0,
            phi_s=0.04,
            health_data={"composite_score": 92.0, "vector": {"buffer": 95.0, "debt": 90.0, "stability": 96.0, "spend": 88.0}},
            customer_profile={"device_is_untrusted": False, "grace_tokens_available": 2, "dti_ratio": 0.18},
            next_emi_due_days=22,
            emi_amount=5000.0,
            projected_balance=65000.0
        )

        self.assertFalse(outcome["veto_triggered"])
        self.assertTrue(outcome["final_action"]["product_push_allowed"])
        self.assertEqual(len(outcome["blocked_products"]), 0)

    def test_convenience_evaluate_veto_layer_filtering(self):
        """
        Tests evaluate_veto_layer integration: verifies that predatory products
        are removed from candidate recommendations when veto fires.
        """
        decision = evaluate_veto_layer(
            customer_id="CUST_INTEGRATION_TEST",
            raw_propensity_recs=self.sample_recs,
            stress_score=36.0, # High stress -> Veto triggers
            dti=0.55 # DTI > 50%
        )

        self.assertTrue(decision["veto_triggered"])
        filtered = decision["filtered_recommendations"]
        allowed_types = [r["product_type"] for r in filtered]

        # Verify Personal Loan and Credit Card are blocked
        self.assertNotIn("PERSONAL_LOAN", allowed_types)
        self.assertNotIn("CREDIT_CARD", allowed_types)
        # Verify Health Insurance and SIP survive
        self.assertIn("HEALTH_INSURANCE", allowed_types)
        self.assertIn("SIP_INVESTMENT", allowed_types)


if __name__ == "__main__":
    unittest.main()
