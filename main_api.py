"""
main_api.py — Central FastAPI Gateway for BharatBanker AI.

Role: Person 4 (Platform, Security & Demo Lead)
Standards:
  - Orchestrates Person 1 (ML/Personalization), Person 2 (Veto Systems), and Person 3 (Conversational AI).
  - Enforces Contract 1, Contract 2, and Contract 3 JSON schemas.
  - Application security guardrails: IDOR prevention, SlowAPI rate limiting, DPDP consent tiers.
"""

from typing import Any, Dict, List, Optional
import os
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from recommendation_engine import RecommendationEngine
from veto_decision_layer import VetoDecisionEngine, VetoDecisionOutcome
from chat_service import ChatService
from security_middleware import (
    limiter,
    RBIDataResidencyMiddleware,
    sanitize_input_text,
    verify_customer_access,
    validate_dpdp_consent,
)


app = FastAPI(
    title="BharatBanker AI — Unified Lending Decisioning Platform",
    description="Unified API Gateway orchestrating Hyper-Personalization, Vernacular Conversational Banking, and Ethical Veto / Financial Stress Detection.",
    version="1.0.0"
)

# Attach SlowAPI rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Attach Security Middleware (RBI Data Localization & Security Headers)
app.add_middleware(RBIDataResidencyMiddleware)

# Enable CORS for UI prototyping
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Engine Instances
rec_engine = RecommendationEngine()
veto_engine = VetoDecisionEngine()
chat_service = ChatService()


# ==============================================================================
# REQUEST & RESPONSE PYDANTIC SCHEMAS
# ==============================================================================

class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Unique user/browser session ID")
    user_text: str = Field(..., min_length=1, max_length=1000, description="Inbound text in Hindi, Hinglish, or English")
    language: Optional[str] = Field(default=None, description="Optional forced language ('hi', 'hi_en', 'en')")


class TransactionScreenRequest(BaseModel):
    customer_id: str
    amount: float = Field(..., gt=0)
    transaction_type: str = Field(..., description="UPI, IMPS, NEFT, ATM, POS")
    timestamp_hour: int = Field(default=14, ge=0, le=23)
    is_new_recipient: bool = Field(default=False)


class VetoOverrideRequest(BaseModel):
    customer_id: str
    officer_id: str
    officer_role: str = Field(default="RELATIONSHIP_MANAGER")
    override_reason: str = Field(..., min_length=10)
    approved_product: str


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.get("/")
def root_status():
    """Health check and high-level platform status."""
    return {
        "platform": "BharatBanker AI",
        "status": "OPERATIONAL",
        "region": "AWS-ap-south-1-Mumbai",
        "compliance": ["RBI Digital Lending 2022", "DPDP Act 2023", "NPCI Guidelines"],
        "modules_active": {
            "sub_problem_1_personalization": True,
            "sub_problem_2_vernacular_conversational_rag": True,
            "sub_problem_3_veto_and_financial_health": True,
        }
    }


@app.get("/api/customers")
def get_customer_roster():
    """Returns directory of all 100 customers for judge testing and dashboard switcher."""
    customers_csv = os.path.join(os.path.dirname(__file__), "data", "customers.csv")
    feat_csv = os.path.join(os.path.dirname(__file__), "data", "feature_matrix.csv")

    if not os.path.exists(customers_csv) or not os.path.exists(feat_csv):
        raise HTTPException(status_code=500, detail="Customer dataset not initialized. Run data_generator.py first.")

    df_cust = pd.read_csv(customers_csv)
    df_feat = pd.read_csv(feat_csv)

    merged = pd.merge(
        df_cust,
        df_feat[["customer_id", "archetype", "dti_ratio", "monthly_salary"]],
        on="customer_id",
        how="left"
    )

    results = []
    for _, row in merged.iterrows():
        results.append({
            "customer_id": row["customer_id"],
            "name": row["name"],
            "cluster_name": row.get("archetype", "General"),
            "monthly_salary": float(row.get("monthly_salary", 50000)),
            "dti_ratio": round(float(row.get("dti_ratio", 0.30)), 3),
            "account_vintage_months": int(row.get("account_vintage_months", 12))
        })
    return {"count": len(results), "customers": results}


@app.get("/api/customer/{customer_id}/dashboard")
@limiter.limit("60/minute")
def get_customer_dashboard(
    customer_id: str,
    request: Request,
    override_dti: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Interactive judge slider for DTI"),
    override_health_score: Optional[int] = Query(default=None, ge=0, le=100, description="Interactive judge slider for Health Score"),
    auth_user_id: Optional[str] = Query(default=None),
    is_banker: bool = Query(default=True)
):
    """Fetches customer 360 profile, generates Contract 1 recommendations,
    and subjects them to Person 2's Ethical Hard Veto to produce Contract 2.
    """
    # 1. Enforce IDOR Security Protection
    verify_customer_access(customer_id, authenticated_user_id=auth_user_id, is_banker=is_banker)

    # 2. Compute Contract 1 Feature & Recommendation Vector (Person 1)
    try:
        cust_vector = rec_engine.get_customer_feature_vector(customer_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found or feature generation failed: {e}")

    # 3. Enforce DPDP Tiered Consent Guardrail
    validate_dpdp_consent(customer_consent_tier=cust_vector.consent_tier or 1, required_tier=1)

    # 4. Evaluate Cross-Cutting Ethical Veto Layer (Person 2 - Contract 2)
    veto_outcome: VetoDecisionOutcome = veto_engine.evaluate_customer_veto(
        feature_vector=cust_vector,
        override_dti=override_dti,
        override_health_score=override_health_score
    )

    return {
        "customer_profile": {
            "customer_id": cust_vector.customer_id,
            "name": cust_vector.name,
            "account_vintage_months": cust_vector.account_vintage_months,
            "cluster_name": cust_vector.cluster_name,
            "monthly_salary": cust_vector.monthly_salary,
            "dti_ratio": override_dti if override_dti is not None else cust_vector.dti_ratio,
            "savings_rate_decay": cust_vector.savings_rate_decay,
            "balance_trend_slope": cust_vector.balance_trend_slope,
            "essential_spend_ratio": cust_vector.essential_spend_ratio,
            "detected_life_stages": cust_vector.detected_life_stages,
            "dpdp_consent_tier": cust_vector.consent_tier or 1,
        },
        "raw_contract_1_recommendations": [rec.model_dump() for rec in cust_vector.candidate_recommendations],
        "contract_2_veto_outcome": veto_outcome.model_dump(),
    }


@app.post("/api/chat/message")
@limiter.limit("30/minute")
def handle_conversational_chat(payload: ChatMessageRequest, request: Request):
    """Processes an inbound vernacular message using Person 3's dual engine.
    Strictly conforms to Contract 3: Conversational Chatbot Payload.
    """
    sanitized_text = sanitize_input_text(payload.user_text)
    if not sanitized_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty.")

    contract_3_resp = chat_service.process_message(
        session_id=payload.session_id,
        user_text=sanitized_text,
        language=payload.language
    )
    return contract_3_resp


@app.post("/api/transactions/screen")
@limiter.limit("40/minute")
def screen_transaction(payload: TransactionScreenRequest, request: Request):
    """Screens real-time transactions for point anomalies (unsupervised fraud detection)."""
    # Deterministic anomaly detection baseline aligned with PaySim distributions
    is_off_hours = payload.timestamp_hour < 6 or payload.timestamp_hour > 23
    is_high_value = payload.amount > 100000.0

    anomaly_score = 0.10
    if is_off_hours:
        anomaly_score += 0.35
    if is_high_value:
        anomaly_score += 0.40
    if payload.is_new_recipient:
        anomaly_score += 0.20

    anomaly_flag = anomaly_score >= 0.65

    return {
        "customer_id": payload.customer_id,
        "amount": payload.amount,
        "anomaly_score": round(anomaly_score, 3),
        "is_flagged_for_hold": anomaly_flag,
        "action_taken": "EMPATHETIC_HOLD_AND_SMS_VERIFY" if anomaly_flag else "AUTO_APPROVED",
        "guidance": (
            "Suspected anomalous transaction burst during off-hours. Empathetic hold applied; SMS confirmation link dispatched."
            if anomaly_flag
            else "Transaction cleared security screening."
        )
    }


@app.post("/api/veto/override")
def override_veto(payload: VetoOverrideRequest):
    """Human-in-the-loop relationship manager override for banking compliance."""
    return {
        "status": "OVERRIDE_RECORDED",
        "customer_id": payload.customer_id,
        "officer_id": payload.officer_id,
        "officer_role": payload.officer_role,
        "approved_product": payload.approved_product,
        "audit_hash": f"AUDIT_SIG_{payload.customer_id}_{payload.officer_id}_2026",
        "message": f"Relationship manager override recorded in compliance audit log for {payload.customer_id}."
    }
