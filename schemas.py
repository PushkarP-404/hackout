"""
schemas.py - Data contracts and Pydantic schemas for BharatBanker AI.
Strictly adheres to Contract 1 in team_distribution.md.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CandidateRecommendation(BaseModel):
    product_type: str = Field(
        ...,
        description="Type of product recommended (e.g. PERSONAL_LOAN, HEALTH_INSURANCE, SIP_INVESTMENT, PREMIUM_CREDIT_CARD)"
    )
    raw_propensity_score: float = Field(
        ...,
        description="Calculated final score / propensity for the product (0.0 to 1.0)"
    )
    shap_reasons: List[str] = Field(
        ...,
        description="Human-readable plain-language explanations derived from SHAP values"
    )


class CustomerFeatureVector(BaseModel):
    """
    Contract 1: Customer Feature & Recommendation Vector
    Producer: Person 1 (ML & Personalization Lead)
    Consumers: Person 2 (Risk ML & Veto Systems Lead), Person 4 (Platform & UI Lead)
    """
    customer_id: str = Field(..., description="Unique customer identifier (e.g. CUST_IND_1042)")
    name: str = Field(..., description="Customer full name")
    account_vintage_months: int = Field(..., description="Account age in months")
    cluster_name: str = Field(..., description="Assigned behavioral cluster name")
    monthly_salary: float = Field(..., description="Average monthly salary credit")
    dti_ratio: float = Field(..., description="Debt-to-Income ratio (total EMI / monthly salary)")
    savings_rate_decay: float = Field(..., description="Linear slope of savings rate over 6 months")
    balance_trend_slope: float = Field(..., description="Linear slope of daily/monthly balance trend")
    essential_spend_ratio: float = Field(..., description="Share of spend on essentials (0.0 to 1.0)")
    candidate_recommendations: List[CandidateRecommendation] = Field(
        ...,
        description="Ranked product recommendations with SHAP explanations"
    )
    # Optional metadata fields useful for downstream services / debugging
    consent_tier: Optional[int] = Field(default=1, description="DPDP Consent Tier (0, 1, or 2)")
    detected_life_stages: Optional[List[str]] = Field(default_factory=list, description="Active event triggers")
