"""
veto_decision_layer.py — Cross-Cutting Ethical Veto & Decision Layer for BharatBanker AI.

Role: Person 2 (Risk ML & Veto Systems Lead)
Consumers: Person 1 (ML), Person 3 (Chat), Person 4 (FastAPI & Streamlit UI)
Standards:
  - Strict compliance with Contract 2: Veto & Decision Layer Outcome.
  - Non-negotiable Hard Floor: DTI > 50% or Health Score < 40 blocks all credit pushes.
  - Medical surge rule: never push loans for medical distress, recommend healthcare protection.
  - Empathetic substitution (EMI restructuring, debt counselling).
"""

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
