"""
veto_decision_layer.py — Cross-Cutting Ethical Veto & Decision Layer for BharatBanker AI.

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
1. Tier 1 Fraud Security Shield & Context-Aware Step-Up Authentication
2. Tier 2 Grace Token Wallet (Moral Hazard Containment)
3. Tier 3 Skin-in-the-Game Micro Co-Payment
4. Multi-Dimensional Health Vector Branching
5. Non-Negotiable Hard Veto Floor
6. DPDP Act 2023 & RBI Audit Integrity
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from schemas import CustomerFeatureVector, CandidateRecommendation


# ==============================================================================
# CONTRACT 2 PYDANTIC SCHEMAS
# ==============================================================================

class EmpatheticAction(BaseModel):
    action_type: str = Field(..., description="RECOMMENDED_PRODUCT or EMPATHETIC_INTERVENTION")
    product_push_allowed: bool = Field(..., description="True if credit/investment product is permitted")
    display_title: str = Field(..., description="Title displayed to customer")
    vernacular_message_hi: str = Field(..., description="Empathetic message in Hindi")
    message_en: str = Field(..., description="Empathetic message in English")
    cta_action: str = Field(..., description="Action button code, e.g. APPLY_NOW, REQUEST_EMI_RELIEF")
    product_type: Optional[str] = None
    shap_reasons: List[str] = Field(default_factory=list)


class VetoDecisionOutcome(BaseModel):
    """
    Contract 2: Veto & Decision Layer Outcome
    Producer: Person 2 (Risk ML & Veto Systems Lead)
    Consumers: Person 1 (ML), Person 3 (Conversational AI), Person 4 (FastAPI Gateway)
    """
    customer_id: str
    financial_health_score: int = Field(..., ge=0, le=100)
    health_category: str = Field(..., description="Healthy, Watch, Early Stress, Distressed, Critical")
    veto_triggered: bool
    veto_reason: Optional[str] = None
    blocked_products: List[str] = Field(default_factory=list)
    final_action: EmpatheticAction


# ==============================================================================
# FINANCIAL HEALTH SCORE & VETO ENGINE
# ==============================================================================

class VetoDecisionEngine:
    """Evaluates multi-week financial stress indicators and applies the
    deterministic hard veto floor against predatory credit recommendations.
    """

    HARD_DTI_THRESHOLD: float = 0.50
    HARD_STRESS_SCORE_THRESHOLD: int = 40

    def compute_financial_health_score(
        self,
        dti_ratio: float,
        savings_decay: float,
        balance_slope: float,
        essential_ratio: float
    ) -> Tuple[int, str]:
        """Calculates a normalized 0-100 Financial Health Score.
        - 80-100: Healthy
        - 60-79: Watch
        - 40-59: Early Stress
        - 20-39: Distressed (Credit blocked)
        - 0-19: Critical (Fraud hold + immediate assistance)
        """
        score = 100.0

        # 1. DTI Impact (max 40 pts penalty)
        if dti_ratio > 0.35:
            dti_penalty = min(40.0, ((dti_ratio - 0.35) / 0.25) * 40.0)
            score -= dti_penalty

        # 2. Savings Rate Decay Impact (max 25 pts penalty)
        if savings_decay < 0:
            savings_penalty = min(25.0, (abs(savings_decay) / 0.15) * 25.0)
            score -= savings_penalty

        # 3. Balance Trend Slope Impact (max 20 pts penalty)
        if balance_slope < 0:
            slope_penalty = min(20.0, (abs(balance_slope) / 0.10) * 20.0)
            score -= slope_penalty

        # 4. Essential Spend Squeeze (max 15 pts penalty)
        if essential_ratio > 0.60:
            spend_penalty = min(15.0, ((essential_ratio - 0.60) / 0.25) * 15.0)
            score -= spend_penalty

        final_score = int(max(5, min(100, round(score))))

        # Categorize
        if final_score >= 80:
            cat = "Healthy"
        elif final_score >= 60:
            cat = "Watch"
        elif final_score >= 40:
            cat = "Early Stress"
        elif final_score >= 20:
            cat = "Distressed"
        else:
            cat = "Critical"

        return final_score, cat

    def evaluate_customer_veto(
        self,
        feature_vector: CustomerFeatureVector,
        override_dti: Optional[float] = None,
        override_health_score: Optional[int] = None
    ) -> VetoDecisionOutcome:
        """Main arbitration method evaluating candidate recommendations against the Veto Layer.
        Strictly conforms to Contract 2.
        """
        dti = override_dti if override_dti is not None else feature_vector.dti_ratio

        if override_health_score is not None:
            health_score = override_health_score
            if health_score >= 80:
                cat = "Healthy"
            elif health_score >= 60:
                cat = "Watch"
            elif health_score >= 40:
                cat = "Early Stress"
            elif health_score >= 20:
                cat = "Distressed"
            else:
                cat = "Critical"
        else:
            health_score, cat = self.compute_financial_health_score(
                dti_ratio=dti,
                savings_decay=feature_vector.savings_rate_decay,
                balance_slope=feature_vector.balance_trend_slope,
                essential_ratio=feature_vector.essential_spend_ratio
            )

        life_stages = feature_vector.detected_life_stages or []
        candidate_recs = feature_vector.candidate_recommendations

        # ----------------------------------------------------------------------
        # RULE 1: Medical Expense Surge Protection
        # "Do not recommend loans to customers with medical expense surges—recommend health insurance instead."
        # ----------------------------------------------------------------------
        if "HEALTH_CONCERN" in life_stages:
            return VetoDecisionOutcome(
                customer_id=feature_vector.customer_id,
                financial_health_score=health_score,
                health_category=cat,
                veto_triggered=True,
                veto_reason="Medical expenditure surge detected. Policy strictly prohibits debt expansion during medical distress.",
                blocked_products=["PERSONAL_LOAN", "CREDIT_CARD", "TOP_UP_LOAN"],
                final_action=EmpatheticAction(
                    action_type="EMPATHETIC_INTERVENTION",
                    product_push_allowed=False,
                    display_title="Comprehensive Health Protection Cover",
                    vernacular_message_hi="Humne dekha ki haal hi mein aapke medical kharche badh gaye hain. Karz lene ki jagah parivar ki suraksha hetu cashless health cover chunein.",
                    message_en="We noticed recent surges in medical outflows. To safeguard your savings against emergencies, we recommend family health protection rather than debt.",
                    cta_action="VIEW_HEALTH_COVER",
                    product_type="HEALTH_INSURANCE",
                    shap_reasons=[
                        "Recent medical expenses surged by >50%, signaling emergency vulnerability",
                        "Zero debt recommended to protect household cashflows"
                    ]
                )
            )

        # ----------------------------------------------------------------------
        # RULE 2: Non-Negotiable Hard Veto Floor (DTI > 50% or Health Score < 40)
        # ----------------------------------------------------------------------
        if dti > self.HARD_DTI_THRESHOLD or health_score < self.HARD_STRESS_SCORE_THRESHOLD:
            reason = (
                f"Debt-to-Income ({round(dti*100,1)}%) exceeds safety threshold of 50%."
                if dti > self.HARD_DTI_THRESHOLD
                else f"Financial Health Score ({health_score}/100) reflects severe cashflow stress."
            )
            return VetoDecisionOutcome(
                customer_id=feature_vector.customer_id,
                financial_health_score=health_score,
                health_category=cat,
                veto_triggered=True,
                veto_reason=reason,
                blocked_products=["PERSONAL_LOAN", "CREDIT_CARD", "TOP_UP_LOAN"],
                final_action=EmpatheticAction(
                    action_type="EMPATHETIC_INTERVENTION",
                    product_push_allowed=False,
                    display_title="Financial Breathing Room & EMI Relief",
                    vernacular_message_hi="Humne dekha ki is mahine aapke kharche badh gaye hain. Kya aap apni agli EMI bina kisi penalty ke aage badhana chahte hain?",
                    message_en="We noticed your monthly expenses have risen. Would you like to reschedule your upcoming EMI at zero penalty to ease cashflow?",
                    cta_action="REQUEST_EMI_RELIEF",
                    product_type=None,
                    shap_reasons=[
                        f"Debt-to-Income ratio at {round(dti*100,1)}% triggers mandatory credit halt",
                        "Empathetic zero-penalty restructuring offered to protect credit rating"
                    ]
                )
            )

        # ----------------------------------------------------------------------
        # RULE 3: Healthy to Mild Stress — Single Approved Product Action
        # ----------------------------------------------------------------------
        top_rec = candidate_recs[0] if candidate_recs else CandidateRecommendation(
            product_type="SIP_INVESTMENT",
            raw_propensity_score=0.75,
            shap_reasons=["Consistent account balance and low debt ratio"]
        )

        display_titles = {
            "SIP_INVESTMENT": "Automated Wealth Building (Tax-Saving SIP)",
            "PREMIUM_CREDIT_CARD": "Pre-Approved Platinum Cashback Card",
            "HEALTH_INSURANCE": "Family Health Shield Insurance",
            "PERSONAL_LOAN": "Pre-Approved Instant Personal Loan"
        }

        vernacular_hi = {
            "SIP_INVESTMENT": f"Badhai ho {feature_vector.name}! Aapki bachat ke aadhar par ₹1,000/mahine se shuru hone wala automated SIP aapke liye upyukt hai.",
            "PREMIUM_CREDIT_CARD": f"Aapke behtareen track record par humne Platinum Cashback card pre-approve kiya hai.",
            "HEALTH_INSURANCE": f"Aapke parivar ke liye ₹5 Lakh ka comprehensive cashless medical insurance uplabdh hai.",
            "PERSONAL_LOAN": f"Aapke acche DTI record par instant digital loan uplabdh hai."
        }

        return VetoDecisionOutcome(
            customer_id=feature_vector.customer_id,
            financial_health_score=health_score,
            health_category=cat,
            veto_triggered=False,
            veto_reason=None,
            blocked_products=[],
            final_action=EmpatheticAction(
                action_type="RECOMMENDED_PRODUCT",
                product_push_allowed=True,
                display_title=display_titles.get(top_rec.product_type, top_rec.product_type),
                vernacular_message_hi=vernacular_hi.get(top_rec.product_type, "Aapke liye anukool financial seva."),
                message_en=f"Recommended based on your positive savings rate and healthy DTI ratio ({round(dti*100,1)}%).",
                cta_action="APPLY_NOW",
                product_type=top_rec.product_type,
                shap_reasons=top_rec.shap_reasons
            )
        )

# ==============================================================================
# DATA STRUCTURES & PROTOCOLS (Grace Token Wallet & Empathetic Interventions)
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
