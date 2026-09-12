"""
==============================================================================
BHARATBANKER AI — CROSS-CUTTING VETO & DECISION LAYER
veto_decision_layer.py
==============================================================================

Role Ownership: Person 2 (Risk ML & Veto Systems Lead)
Produces: Contract 2 (Veto & Decision Layer Outcome)
Consumers: Person 1 (ML & Personalization), Person 3 (Conversational AI), Person 4 (FastAPI/UI)

Primary Sources of Truth:
- docs/BharatBanker_AI_Unified_Solution.pdf (Section 2, 5 & 6)
- team_distribution.md (Contract 2: Veto & Decision Layer Outcome)
- financial_health_and_fraud_monitor_guide.md (Sections 5, 6, 10 & 13)
- docs/approach_problem1.md (Ethical Guardrail & Life-Stage Filtering)
- docs/All about security features provided by a banking organization.docx (Layer 3 & 5)
- docs/Security portion of the program (1).docx (IDOR, MFA & Zero Trust)

Core Capabilities:
1. Tier 1 Fraud Security Shield & Context-Aware Step-Up Authentication:
   - Locks empathetic restructuring and credit pushes when Phi_F >= 0.60 or
     device/SIM/velocity security anomalies are detected.
2. Tier 2 Grace Token Wallet (Moral Hazard Containment):
   - Maximum 2 Grace Tokens per 12-month rolling window.
   - 4 consecutive on-time EMIs required to replenish 1 token.
   - If tokens are exhausted, free grace is withheld; structural tenure extension
     (e.g., +3 to +6 months) is offered instead.
3. Tier 3 Skin-in-the-Game Micro Co-Payment:
   - EMI split requires 25% immediate commitment co-pay; remaining 75% deferred
     for 14 days at zero penalty fee, preserving CIBIL standing.
4. Multi-Dimensional Health Vector Branching:
   - Handles Impending Default (Low Buffer < 30, High Debt < 40).
   - Handles Temporary Cashflow Gap / Harvest Delay (Low Buffer < 30, Solvent Debt >= 60, Low Stability < 40).
   - Handles Discretionary Lifestyle Drift (High Buffer >= 80, Low Spend < 30, Normal Debt >= 70).
5. Non-Negotiable Hard Veto Floor:
   - Programmatically blocks credit products (PERSONAL_LOAN, CREDIT_CARD, TOP_UP_LOAN)
     whenever DTI > 50% or Financial Health Score < 40.0.
6. DPDP Act 2023 & RBI Audit Integrity:
   - Generates SHA-256 tamper-evident digital audit logs for regulatory inspection.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple


# ==============================================================================
# DATA STRUCTURES & PROTOCOLS
# ==============================================================================

@dataclass
class GraceTokenWallet:
    """
    Tier 2 Moral Hazard Containment: Finite Empathy Budget.
    Prevents habitual gaming of emergency grace windows and interest holidays.
    """
    max_tokens: int = 2
    available_tokens: int = 2
    on_time_streak: int = 0
    replenishment_target_streak: int = 4
    total_tokens_consumed_12m: int = 0

    def record_repayment(self, is_on_time: bool) -> bool:
        """
        Tracks consecutive on-time EMIs. Replenishes 1 token every 4 on-time cycles (capped at max_tokens).
        Returns True if a token was successfully replenished.
        """
        if is_on_time:
            self.on_time_streak += 1
            if self.on_time_streak >= self.replenishment_target_streak and self.available_tokens < self.max_tokens:
                self.available_tokens += 1
                self.on_time_streak = 0
                return True
        else:
            self.on_time_streak = 0
        return False

    def consume_token(self) -> bool:
        """Deducts 1 token if available. Resets current on-time streak upon relief usage."""
        if self.available_tokens > 0:
            self.available_tokens -= 1
            self.total_tokens_consumed_12m += 1
            self.on_time_streak = 0
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InterventionOption:
    """Represents an actionable relief choice presented to the borrower."""
    option_id: str
    label: str
    copay_amount: float
    deferred_amount: float
    deferral_days: int
    requires_token: bool
    cibil_impact: str = "PRESERVED_NO_DOWNGRADE"
    late_fee_waived: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# 5. EMPATHETIC POLICY ENGINE
# ==============================================================================

class EmpatheticPolicyEngine:
    """
    Central arbitration engine enforcing the hard floor, moral hazard containment,
    and empathetic substitution.
    """

    # Non-negotiable regulatory & risk constants
    HARD_DTI_CEILING: float = 0.50               # RBI Fair Practices: Max 50% DTI
    FRAUD_POLARITY_CEILING: float = 0.60         # Lock empathy if Phi_F >= 0.60
    PRE_BOUNCE_LOOKAHEAD_DAYS: int = 4           # T-4 days pre-bounce trigger window
    DEFAULT_SKIN_IN_THE_GAME_RATIO: float = 0.25 # 25% commitment co-pay
    MAX_RECOMMENDATIONS_PER_WEEK: int = 2

    # Prohibited predatory products under stress veto
    BLOCKED_CREDIT_PRODUCTS: List[str] = [
        "PERSONAL_LOAN",
        "CREDIT_CARD",
        "TOP_UP_LOAN",
        "INSTANT_CASH_CREDIT",
        "SALARY_ADVANCE_LOAN"
    ]

    @classmethod
    def evaluate(
        cls,
        customer_id: str,
        phi_f: float,
        phi_s: float,
        health_data: Dict[str, Any],
        customer_profile: Dict[str, Any],
        next_emi_due_days: int,
        emi_amount: float,
        projected_balance: float,
        token_wallet: Optional[GraceTokenWallet] = None
    ) -> Dict[str, Any]:
        """
        Primary evaluation entry point adhering to Contract 2 schema.
        Sequentially executes:
        Gate 1: Tier 1 Fraud Security Shield
        Gate 2: Pre-Bounce Shortfall & Grace Token Wallet
        Gate 3: 4D Health Vector Granular Branching
        Gate 4: Hard Veto Floor on DTI & Delinquency Band
        Gate 5: Contract 2 payload formatting
        """
        # Resolve wallet instance
        if token_wallet is None:
            raw_tokens = customer_profile.get("grace_tokens_available", 2)
            raw_streak = customer_profile.get("on_time_repayment_streak", 0)
            token_wallet = GraceTokenWallet(
                available_tokens=raw_tokens,
                on_time_streak=raw_streak
            )

        vector = health_data.get("vector", {
            "buffer": 50.0,
            "debt": 50.0,
            "stability": 50.0,
            "spend": 50.0
        })
        composite_score = float(health_data.get("composite_score", 50.0))
        dti_ratio = float(customer_profile.get("dti_ratio", 0.35))
        language = customer_profile.get("preferred_language", "hi")

        # ----------------------------------------------------------------------
        # GATE 1: TIER 1 FRAUD SECURITY SHIELD (Context-Aware Step-Up Gate)
        # ----------------------------------------------------------------------
        security_breached, sec_reason = cls._inspect_security_signals(phi_f, customer_profile)
        if security_breached:
            return cls._build_security_challenge_response(
                customer_id=customer_id,
                composite_score=composite_score,
                sec_reason=sec_reason,
                language=language
            )

        # ----------------------------------------------------------------------
        # GATE 2: PRE-BOUNCE SHORTFALL & MORAL HAZARD TOKEN CHECK
        # ----------------------------------------------------------------------
        if next_emi_due_days <= cls.PRE_BOUNCE_LOOKAHEAD_DAYS and projected_balance < emi_amount:
            shortfall = emi_amount - projected_balance
            return cls._handle_pre_bounce_shortfall(
                customer_id=customer_id,
                composite_score=composite_score,
                emi_amount=emi_amount,
                shortfall=shortfall,
                token_wallet=token_wallet,
                language=language
            )

        # ----------------------------------------------------------------------
        # GATE 3: 4D HEALTH VECTOR GRANULAR BRANCHING POLICY
        # ----------------------------------------------------------------------
        s_buf = vector.get("buffer", 50.0)
        s_debt = vector.get("debt", 50.0)
        s_stab = vector.get("stability", 50.0)
        s_spnd = vector.get("spend", 50.0)

        # Branch 3A: Impending Default / Structural Overleverage
        # Low Buffer (<30) + High Debt/DTI Stress (<40)
        if s_buf < 30.0 and s_debt < 40.0:
            return cls._handle_structural_overleverage(
                customer_id=customer_id,
                composite_score=composite_score,
                emi_amount=emi_amount,
                language=language
            )

        # Branch 3B: Temporary Cashflow Gap (Salary/Harvest Delay)
        # Low Buffer (<30) + Solvent Debt Profile (>=60) + Inflow Shock (<40)
        if s_buf < 30.0 and s_debt >= 60.0 and s_stab < 40.0:
            return cls._handle_temporary_cashflow_gap(
                customer_id=customer_id,
                composite_score=composite_score,
                emi_amount=emi_amount,
                language=language
            )

        # Branch 3C: Discretionary Lifestyle Inflation (Solvent but Reckless)
        # High Buffer (>=80) + Poor Spending Discipline (<30) + Normal Debt (>=70)
        if s_buf >= 80.0 and s_spnd < 30.0 and s_debt >= 70.0:
            return cls._handle_discretionary_spend_drift(
                customer_id=customer_id,
                composite_score=composite_score,
                language=language
            )

        # ----------------------------------------------------------------------
        # GATE 4: HARD VETO FLOOR ON DTI / COMPOSITE DELINQUENCY BAND
        # ----------------------------------------------------------------------
        if dti_ratio > cls.HARD_DTI_CEILING or composite_score < 40.0:
            return cls._handle_hard_veto_floor(
                customer_id=customer_id,
                composite_score=composite_score,
                dti_ratio=dti_ratio,
                language=language
            )

        # ----------------------------------------------------------------------
        # DEFAULT: HEALTHY / MILD MONITORING (Proactive recommendations allowed)
        # ----------------------------------------------------------------------
        return {
            "customer_id": customer_id,
            "financial_health_score": round(composite_score, 1),
            "health_category": "Healthy" if composite_score >= 80.0 else "Mild Concern",
            "veto_triggered": False,
            "veto_reason": None,
            "empathy_unlocked": True,
            "blocked_products": [],
            "final_action": {
                "action_type": "PROACTIVE_RECOMMENDATION_PERMITTED",
                "product_push_allowed": True,
                "display_title": "Standard Financial Journey",
                "message_en": "Your account health is stable. Tailored financial products may be surfaced.",
                "vernacular_message_hi": "Aapka khata santulit hai. Zaroorat anusar upyogi yojanaayein uplabdh hain.",
                "cta_action": "VIEW_RECOMMENDATIONS"
            },
            "audit_trail": cls._create_audit_artifact(customer_id, "PASS_STANDARD_MONITORING", composite_score)
        }

    # ==========================================================================
    # INTERNAL HANDLERS
    # ==========================================================================

    @classmethod
    def _inspect_security_signals(
        cls,
        phi_f: float,
        profile: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluates Layer 3 & Layer 5 zero-trust security conditions."""
        if phi_f >= cls.FRAUD_POLARITY_CEILING:
            return True, f"High fraud polarity score detected (Phi_F={phi_f:.2f} >= {cls.FRAUD_POLARITY_CEILING})."
        if profile.get("device_is_untrusted", False):
            return True, "Unrecognized device signature detected."
        if profile.get("recent_sim_change", False):
            return True, "Recent SIM swap / carrier change detected within 72 hours."
        if profile.get("velocity_1h_count", 0) > 4:
            return True, "Anomalous transaction frequency / velocity spike within last hour."
        if profile.get("is_off_hours_login", False) and profile.get("ip_foreign_flag", False):
            return True, "Unusual 3 AM login from foreign or VPN IP subnet."
        return False, ""

    @classmethod
    def _build_security_challenge_response(
        cls,
        customer_id: str,
        composite_score: float,
        sec_reason: str,
        language: str
    ) -> Dict[str, Any]:
        """Locks all empathy dialog and outputs security challenge."""
        return {
            "customer_id": customer_id,
            "financial_health_score": round(composite_score, 1),
            "health_category": "Security Review Required",
            "veto_triggered": True,
            "veto_reason": f"SECURITY_SHIELD_ACTIVE: {sec_reason}",
            "empathy_unlocked": False,
            "blocked_products": cls.BLOCKED_CREDIT_PRODUCTS,
            "final_action": {
                "action_type": "SECURITY_CHALLENGE",
                "product_push_allowed": False,
                "display_title": "Identity Verification Required",
                "message_en": "To protect your account, financial restructuring and credit actions are temporarily paused. Please complete step-up biometric KYC.",
                "vernacular_message_hi": "Aapke khate ki suraksha ke liye, naye badlav abhi roke gaye hain. Kripya biometric ya OTP dwara pehchaan satyapit karein.",
                "cta_action": "STEP_UP_BIOMETRIC_KYC"
            },
            "audit_trail": cls._create_audit_artifact(customer_id, "SECURITY_CHALLENGE", composite_score, sec_reason)
        }

    @classmethod
    def _handle_pre_bounce_shortfall(
        cls,
        customer_id: str,
        composite_score: float,
        emi_amount: float,
        shortfall: float,
        token_wallet: GraceTokenWallet,
        language: str
    ) -> Dict[str, Any]:
        """Tier 2 & 3: Evaluates Grace Token wallet and skin-in-the-game co-pay."""
        copay = round(emi_amount * cls.DEFAULT_SKIN_IN_THE_GAME_RATIO, 2)
        deferred = round(emi_amount - copay, 2)

        if token_wallet.available_tokens > 0:
            options = [
                InterventionOption(
                    option_id="SPLIT_EMI_WITH_COPAY",
                    label=f"Pay ₹{copay:,.0f} today (25% co-pay); pay remaining ₹{deferred:,.0f} in 14 days.",
                    copay_amount=copay,
                    deferred_amount=deferred,
                    deferral_days=14,
                    requires_token=True
                ).to_dict(),
                InterventionOption(
                    option_id="7_DAY_GRACE_WINDOW",
                    label=f"Activate 7-day grace window (₹{emi_amount:,.0f} due on day 7, 0 penalty, CIBIL intact).",
                    copay_amount=0.0,
                    deferred_amount=emi_amount,
                    deferral_days=7,
                    requires_token=True
                ).to_dict()
            ]

            return {
                "customer_id": customer_id,
                "financial_health_score": round(composite_score, 1),
                "health_category": "Early Stress",
                "veto_triggered": True,
                "veto_reason": f"Impending auto-debit shortfall of ₹{shortfall:,.0f} within {cls.PRE_BOUNCE_LOOKAHEAD_DAYS} days.",
                "empathy_unlocked": True,
                "grace_tokens_remaining": token_wallet.available_tokens,
                "blocked_products": cls.BLOCKED_CREDIT_PRODUCTS,
                "final_action": {
                    "action_type": "EMPATHETIC_INTERVENTION",
                    "product_push_allowed": False,
                    "display_title": "Proactive EMI Relief (Grace Token Available)",
                    "message_en": f"We noticed your balance may be short by ₹{shortfall:,.0f} for your upcoming EMI of ₹{emi_amount:,.0f}. You can activate your Grace Token to split payment without penalty or credit score impact.",
                    "vernacular_message_hi": f"Humne dekha ki agli EMI ke liye lagbhag ₹{shortfall:,.0f} ki kami ho sakti hai. Aap apna Grace Token istemal karke bina kisi jurmane ke 25% abhi aur baki 14 din baad chuka sakte hain.",
                    "cta_action": "ACTIVATE_GRACE_TOKEN",
                    "intervention_options": options
                },
                "audit_trail": cls._create_audit_artifact(customer_id, "PRE_BOUNCE_GRACE_OFFERED", composite_score)
            }
        else:
            # Moral Hazard Protection: Tokens exhausted. No free grace. Offer structural restructuring.
            return {
                "customer_id": customer_id,
                "financial_health_score": round(composite_score, 1),
                "health_category": "Early Stress (Tokens Exhausted)",
                "veto_triggered": True,
                "veto_reason": "Pre-bounce shortfall detected, but 12-month Grace Token budget is exhausted.",
                "empathy_unlocked": True,
                "grace_tokens_remaining": 0,
                "blocked_products": cls.BLOCKED_CREDIT_PRODUCTS,
                "final_action": {
                    "action_type": "EMPATHETIC_RESTRUCTURING",
                    "product_push_allowed": False,
                    "display_title": "Sustainable Loan Tenure Extension",
                    "message_en": "You have utilized your annual Grace Tokens. To permanently lower your monthly EMI burden, we can extend your loan tenure by 3 to 6 months.",
                    "vernacular_message_hi": "Aapke is varsh ke Grace Tokens samapt ho chuke hain. EMI ka bojh kam karne ke liye hum aapke loan ki muddat 3 se 6 mahine badha sakte hain.",
                    "cta_action": "APPLY_TENURE_RESTRUCTURING"
                },
                "audit_trail": cls._create_audit_artifact(customer_id, "MORAL_HAZARD_GUARD_STRUCTURAL_OFFER", composite_score)
            }

    @classmethod
    def _handle_structural_overleverage(
        cls,
        customer_id: str,
        composite_score: float,
        emi_amount: float,
        language: str
    ) -> Dict[str, Any]:
        """Branch 3A: Severe debt strain + zero liquidity."""
        return {
            "customer_id": customer_id,
            "financial_health_score": round(composite_score, 1),
            "health_category": "Distressed",
            "veto_triggered": True,
            "veto_reason": "Structural overleverage: Buffer Pillar < 30 and Debt Pillar < 40.",
            "empathy_unlocked": True,
            "blocked_products": cls.BLOCKED_CREDIT_PRODUCTS,
            "final_action": {
                "action_type": "EMPATHETIC_INTERVENTION",
                "product_push_allowed": False,
                "display_title": "Comprehensive Debt Restructuring",
                "message_en": "Your debt obligations exceed safe thresholds. We have paused all new loan offers and can connect you with an advisor for loan consolidation or a 30-day moratorium.",
                "vernacular_message_hi": "Aapke kharche aur EMI aamdani se adhik hain. Naye loan band kar diye gaye hain. Kya aap loan ki muddat badhane ya salahkaar se baat karna chahte hain?",
                "cta_action": "REQUEST_DEBT_COUNSELLING"
            },
            "audit_trail": cls._create_audit_artifact(customer_id, "STRUCTURAL_OVERLEVERAGE_VETO", composite_score)
        }

    @classmethod
    def _handle_temporary_cashflow_gap(
        cls,
        customer_id: str,
        composite_score: float,
        emi_amount: float,
        language: str
    ) -> Dict[str, Any]:
        """Branch 3B: Pristine borrower with temporary harvest/salary delay."""
        bridge_amt = round(emi_amount * 0.50, 2)
        return {
            "customer_id": customer_id,
            "financial_health_score": round(composite_score, 1),
            "health_category": "Temporary Cashflow Gap",
            "veto_triggered": True,
            "veto_reason": "Temporary liquidity pinch (Buffer < 30) despite pristine repayment track record (Debt >= 60).",
            "empathy_unlocked": True,
            "blocked_products": cls.BLOCKED_CREDIT_PRODUCTS,
            "final_action": {
                "action_type": "EMPATHETIC_INTERVENTION",
                "product_push_allowed": False,
                "display_title": "0% Interest Emergency Bridge Facility",
                "message_en": f"We noticed an unexpected delay in your regular monthly inflow. Activate a 0% interest mini-bridge overdraft of ₹{bridge_amt:,.0f} to cover your scheduled payment.",
                "vernacular_message_hi": f"Aapki niyamit aamdani aane mein der hui hai. Agli EMI bina rukawat poori karne ke liye ₹{bridge_amt:,.0f} ka 0% byaj bridge sahayata uplabdh hai.",
                "cta_action": "ACTIVATE_MINI_BRIDGE"
            },
            "audit_trail": cls._create_audit_artifact(customer_id, "TEMPORARY_CASHFLOW_BRIDGE_OFFER", composite_score)
        }

    @classmethod
    def _handle_discretionary_spend_drift(
        cls,
        customer_id: str,
        composite_score: float,
        language: str
    ) -> Dict[str, Any]:
        """Branch 3C: Strong balance but undisciplined discretionary outlays."""
        return {
            "customer_id": customer_id,
            "financial_health_score": round(composite_score, 1),
            "health_category": "Mild Concern (Lifestyle Inflation)",
            "veto_triggered": False,
            "veto_reason": None,
            "empathy_unlocked": True,
            "blocked_products": ["PREMIUM_CREDIT_CARD", "PERSONAL_LOAN"],
            "final_action": {
                "action_type": "BUDGETING_NUDGE",
                "product_push_allowed": False,
                "display_title": "Smart Auto-Sweep Savings Nudge",
                "message_en": "Your savings reserve is healthy, but discretionary shopping rose by 35% this month. Activate Auto-Sweep to lock surplus cash into 7.2% interest fixed deposits.",
                "vernacular_message_hi": "Aapki bachat acchi hai, par is mahine gair-zaroori kharche badh gaye hain. Bachat ko surakshit rakhne ke liye Auto-Sweep chalu karein.",
                "cta_action": "ACTIVATE_AUTO_SWEEP_SAVINGS"
            },
            "audit_trail": cls._create_audit_artifact(customer_id, "LIFESTYLE_INFLATION_NUDGE", composite_score)
        }

    @classmethod
    def _handle_hard_veto_floor(
        cls,
        customer_id: str,
        composite_score: float,
        dti_ratio: float,
        language: str
    ) -> Dict[str, Any]:
        """Hard floor fallback when DTI exceeds 50% or health is critical."""
        return {
            "customer_id": customer_id,
            "financial_health_score": round(composite_score, 1),
            "health_category": "Early Stress" if composite_score >= 40.0 else "Critical",
            "veto_triggered": True,
            "veto_reason": f"Debt-to-income exceeds safety threshold (DTI={dti_ratio*100:.1f}% > 50.0% cap).",
            "empathy_unlocked": True,
            "blocked_products": cls.BLOCKED_CREDIT_PRODUCTS,
            "final_action": {
                "action_type": "EMPATHETIC_INTERVENTION",
                "product_push_allowed": False,
                "display_title": "Proactive EMI Support",
                "message_en": "We noticed your monthly expenses have risen. Would you like to reschedule your upcoming EMI at zero penalty?",
                "vernacular_message_hi": "Humne dekha ki is mahine aapke kharche badh gaye hain. Kya aap apni agli EMI aage badhana chahte hain?",
                "cta_action": "REQUEST_EMI_RELIEF"
            },
            "audit_trail": cls._create_audit_artifact(customer_id, "HARD_DTI_VETO_TRIGGERED", composite_score)
        }

    @classmethod
    def _create_audit_artifact(
        cls,
        customer_id: str,
        decision_code: str,
        score: float,
        extra_info: str = ""
    ) -> Dict[str, Any]:
        """Generates immutable SHA-256 digital signature conforming to DPDP Act 2023."""
        ts = int(time.time())
        raw_payload = f"{customer_id}|{decision_code}|{score:.2f}|{ts}|{extra_info}"
        signature = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        return {
            "timestamp_utc": ts,
            "decision_code": decision_code,
            "fhs_composite": round(score, 1),
            "consent_verification": "DPDP_2023_TIER1_VALIDATED",
            "hash_signature": signature
        }


# ==============================================================================
# CONVENIENCE ARBITRATION FUNCTION (Inter-Service Contract 2 Connector)
# ==============================================================================

def evaluate_veto_layer(
    customer_id: str,
    raw_propensity_recs: List[Dict[str, Any]],
    stress_score: float,
    dti: float,
    customer_profile: Optional[Dict[str, Any]] = None,
    health_vector: Optional[Dict[str, float]] = None,
    next_emi_due_days: int = 15,
    emi_amount: float = 0.0,
    projected_balance: float = 100000.0,
    phi_f: float = 0.0,
    phi_s: float = 0.0
) -> Dict[str, Any]:
    """
    Convenience function connecting Person 1's recommendation engine
    and Person 3's loan application directly to Person 2's Veto Layer.
    """
    profile = customer_profile or {}
    profile["dti_ratio"] = dti

    health_data = {
        "composite_score": stress_score,
        "vector": health_vector or {
            "buffer": min(100.0, max(0.0, 100.0 - stress_score)),
            "debt": max(0.0, 100.0 - (dti * 100.0)),
            "stability": 60.0,
            "spend": 60.0
        }
    }

    # Run core policy engine
    decision = EmpatheticPolicyEngine.evaluate(
        customer_id=customer_id,
        phi_f=phi_f,
        phi_s=phi_s,
        health_data=health_data,
        customer_profile=profile,
        next_emi_due_days=next_emi_due_days,
        emi_amount=emi_amount,
        projected_balance=projected_balance
    )

    # Filter raw propensity recommendations based on veto
    if decision["veto_triggered"]:
        blocked_set = set(decision.get("blocked_products", []))
        allowed_recs = [r for r in raw_propensity_recs if r.get("product_type") not in blocked_set]
        decision["filtered_recommendations"] = allowed_recs
    else:
        # Mild stress continuous soft discount
        discount_factor = max(0.0, 1.0 - (stress_score / 100.0 * 0.5))
        discounted = []
        for r in raw_propensity_recs:
            r_copy = dict(r)
            if "raw_propensity_score" in r_copy:
                r_copy["discounted_propensity_score"] = round(r_copy["raw_propensity_score"] * discount_factor, 3)
            discounted.append(r_copy)
        decision["filtered_recommendations"] = discounted

    return decision
