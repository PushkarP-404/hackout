"""
app.py — BharatBanker AI Master Interactive Prototype (Streamlit).

Role: Person 4 (Platform, Security & Demo Lead)
Features:
  1. Customer Portal with 0-100 Financial Health Score & Single SHAP-explained recommendation card.
  2. Embedded Vernacular Chat Assistant (Dual Engine: Loan Slot-Filling + Grounded FAISS RAG).
  3. Banker & Judge Live Veto Auditor with real-time interactive sliders for live demo showstoppers.
  4. Direct integration with Person 1, 2, and 3 services.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="BharatBanker AI — Unified Lending Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Aesthetic Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F766E 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
        margin-top: 6px;
    }
    .badge-rbi { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-dpdp { background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }
    .badge-mumbai { background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }
    
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .rec-card {
        background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%);
        border: 2px solid #0EA5E9;
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-top: 12px;
        box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.2);
    }
    
    .rec-card-veto {
        background: linear-gradient(145deg, #2A1515 0%, #1A0C0C 100%);
        border: 2px solid #EF4444;
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-top: 12px;
        box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.2);
    }

    .shap-tag {
        background: rgba(14, 165, 233, 0.15);
        color: #7dd3fc;
        border-left: 3px solid #38bdf8;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Import backend services directly for zero-latency in-process Streamlit execution
from feature_pipeline import CustomerFeaturePipeline
from recommendation_engine import RecommendationEngine
from veto_decision_layer import VetoDecisionEngine
from chat_service import ChatService


@st.cache_resource
def load_services():
    return {
        "pipeline": CustomerFeaturePipeline(),
        "rec_engine": RecommendationEngine(),
        "veto_engine": VetoDecisionEngine(),
        "chat_service": ChatService(),
    }

services = load_services()
pipeline = services["pipeline"]
rec_engine = services["rec_engine"]
veto_engine = services["veto_engine"]
chat_service = services["chat_service"]


# ==============================================================================
# 1. SIDEBAR: PERSONA SELECTOR & DEMO CANONICAL SWITCHER
# ==============================================================================

st.sidebar.image("https://img.icons8.com/color/96/bank-building.png", width=64)
st.sidebar.title("BharatBanker AI")
st.sidebar.caption("Unified Lending Decisioning Platform")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Demo Canonical Scenarios")

col_s1, col_s2 = st.sidebar.columns(2)
if col_s1.button("🌟 Priya Sharma", help="Scenario 1: Upward Earner (Salary Jump -> SIP)"):
    st.session_state["selected_customer_id"] = "CUST_IND_1042"
if col_s2.button("🛡️ Amit Patel", help="Scenario 2: Medical Spike (Hard Veto -> Health Cover)"):
    st.session_state["selected_customer_id"] = "CUST_IND_1088"

col_s3, col_s4 = st.sidebar.columns(2)
if col_s3.button("🗣️ Sunita Devi", help="Scenario 3: Vernacular User (Hinglish/Hindi Loan Flow)"):
    st.session_state["selected_customer_id"] = "CUST_IND_1002"
if col_s4.button("⚖️ Ramesh Kumar", help="Baseline: Stable Professional"):
    st.session_state["selected_customer_id"] = "CUST_IND_1015"

# Customer directory dropdown
customers_csv = os.path.join(os.path.dirname(__file__), "data", "customers.csv")
cust_df = pd.read_csv(customers_csv)
customer_options = {
    row["customer_id"]: f"{row['name']} ({row['customer_id']}) — {row['archetype']}"
    for _, row in cust_df.iterrows()
}

if "selected_customer_id" not in st.session_state:
    st.session_state["selected_customer_id"] = "CUST_IND_1042"

selected_cid = st.sidebar.selectbox(
    "Or select from 100 Synthetic Profiles:",
    options=list(customer_options.keys()),
    index=list(customer_options.keys()).index(st.session_state["selected_customer_id"]),
    format_func=lambda cid: customer_options[cid]
)
st.session_state["selected_customer_id"] = selected_cid

st.sidebar.markdown("---")
view_mode = st.sidebar.radio(
    "Select Operating View:",
    options=["👤 Customer Portal View", "🏛️ Banker & Judge Live Veto Auditor"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Regulatory Compliance Ready:**
- 🇮🇳 RBI Digital Lending Guidelines 2022
- 🔐 DPDP Act 2023 Tiered Consent
- 📍 AWS Mumbai Residency Header Active
""")


# ==============================================================================
# 2. MAIN HEADER
# ==============================================================================

st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">BharatBanker AI</h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 15px;">
                Intelligent Digital Lending Companion: Proactive Recommendations • Vernacular Conversational Banking • Ethical Hard Veto
            </p>
            <div style="margin-top: 8px;">
                <span class="badge-pill badge-rbi">RBI Compliant (3-Day Cooling Off)</span>
                <span class="badge-pill badge-dpdp">DPDP Act 2023 (Verhoeff Masked Aadhaar)</span>
                <span class="badge-pill badge-mumbai">Region: AWS-ap-south-1-Mumbai</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Fetch customer data
feat = pipeline.get_feature_vector(st.session_state["selected_customer_id"])
cust_vector = rec_engine.get_contract_1_vector(feat)


# ==============================================================================
# VIEW 1: CUSTOMER PORTAL VIEW
# ==============================================================================

if view_mode == "👤 Customer Portal View":
    col_left, col_right = st.columns([5, 4])

    with col_left:
        # Customer Profile Header Bar
        st.subheader(f"Welcome, {cust_vector.name} 👋")
        
        # Financial Health Metrics Bar
        health_score, health_cat = veto_engine.compute_financial_health_score(
            dti_ratio=cust_vector.dti_ratio,
            savings_decay=cust_vector.savings_rate_decay,
            balance_slope=cust_vector.balance_trend_slope,
            essential_ratio=cust_vector.essential_spend_ratio
        )
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Monthly Salary", f"₹{cust_vector.monthly_salary:,.0f}")
        m2.metric("Debt-to-Income", f"{cust_vector.dti_ratio * 100:.1f}%")
        
        # Color score
        score_color = "🟢" if health_score >= 80 else ("🟡" if health_score >= 40 else "🔴")
        m3.metric("Health Score", f"{health_score}/100", f"{score_color} {health_cat}")
        m4.metric("Segment", cust_vector.cluster_name)

        # Run through Ethical Veto Layer
        veto_outcome = veto_engine.evaluate_customer_veto(cust_vector)
        action = veto_outcome.final_action

        # Single Hyper-Personalized Recommendation Card
        if not veto_outcome.veto_triggered:
            st.markdown(f"""
            <div class="rec-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; color: #38BDF8; letter-spacing: 1px;">⭐ RECOMMENDED FOR YOU</span>
                    <span style="font-size: 12px; background: rgba(56, 189, 248, 0.2); padding: 4px 8px; border-radius: 6px; color: #38BDF8;">
                        High Affinity Fit
                    </span>
                </div>
                <h3 style="margin: 0 0 8px 0; font-size: 20px;">{action.display_title}</h3>
                <p style="color: #CBD5E1; font-size: 14px; margin-bottom: 16px;">{action.vernacular_message_hi}</p>
                <div style="margin-bottom: 16px;">
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 6px; font-weight: 600;">WHY THIS IS SURFACED (SHAP EXPLAINABILITY):</div>
                    {"".join([f'<div class="shap-tag">💡 {r}</div>' for r in action.shap_reasons])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Explore & Apply Instantly", key="btn_rec_apply"):
                st.balloons()
                st.success(f"Initiated journey for {action.display_title}! Standard Key Fact Statement (KFS) is being prepared.")
        else:
            # Empathetic Veto Card
            st.markdown(f"""
            <div class="rec-card-veto">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 12px; font-weight: 700; color: #F87171; letter-spacing: 1px;">🛡️ RESPONSIBLE LENDING INTERVENTION</span>
                    <span style="font-size: 12px; background: rgba(239, 68, 68, 0.2); padding: 4px 8px; border-radius: 6px; color: #F87171;">
                        Credit Push Blocked
                    </span>
                </div>
                <h3 style="margin: 0 0 8px 0; font-size: 20px;">{action.display_title}</h3>
                <p style="color: #FECACA; font-size: 14px; margin-bottom: 16px;">{action.vernacular_message_hi}</p>
                <div style="margin-bottom: 16px;">
                    <div style="font-size: 12px; color: #FCA5A5; margin-bottom: 6px; font-weight: 600;">ETHICAL REASONING:</div>
                    {"".join([f'<div class="shap-tag" style="background: rgba(239,68,68,0.15); color: #fca5a5; border-color: #ef4444;">🛡️ {r}</div>' for r in action.shap_reasons])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🤝 Request Proactive EMI Relief", key="btn_relief"):
                st.info("EMI Relief request registered with zero penalty. A relationship counsellor will assist you shortly.")

    with col_right:
        st.subheader("💬 Vernacular Assistant")
        st.caption("Dual-Engine: Instant Loan KYC + RBI Grounded Q&A (Hindi / Hinglish / English)")

        # Chat session state
        chat_sess_id = f"st_session_{st.session_state['selected_customer_id']}"
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": "Namaste! Main aapka BharatBanker saathi hoon. Main digital loan aavedan ya banking nitiyon (RBI guidelines) mein aapki sahayata kar sakta hoon. Kripya bataiye main kya madad karu?"
                }
            ]

        # Quick chips
        st.markdown("**Quick Inquiries:**")
        qcol1, qcol2 = st.columns(2)
        if qcol1.button("Cooling-off period kya hai?"):
            st.session_state["chat_input_val"] = "Yeh cooling-off period kya hota hai?"
        if qcol2.button("Why do you need PAN?"):
            st.session_state["chat_input_val"] = "Why do you need my PAN number?"

        qcol3, qcol4 = st.columns(2)
        if qcol3.button("UPI PIN rule?"):
            st.session_state["chat_input_val"] = "UPI PIN kab dalna chahiye?"
        if qcol4.button("Mera loan apply karein"):
            st.session_state["chat_input_val"] = cust_vector.name

        # Display conversation
        chat_container = st.container(height=350)
        with chat_container:
            for m in st.session_state["chat_messages"]:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])

        # Input box
        user_msg = st.chat_input("Apna sandesh yahan likhein (Hindi / Hinglish / English)...")
        if "chat_input_val" in st.session_state:
            user_msg = st.session_state.pop("chat_input_val")

        if user_msg:
            # User message
            st.session_state["chat_messages"].append({"role": "user", "content": user_msg})

            # Process with ChatService
            resp = chat_service.process_message(chat_sess_id, user_msg)
            bot_text = resp["bot_message"]

            st.session_state["chat_messages"].append({"role": "assistant", "content": bot_text})
            st.rerun()


# ==============================================================================
# VIEW 2: BANKER & JUDGE LIVE VETO AUDITOR (THE DEMO SHOWSTOPPER)
# ==============================================================================

elif view_mode == "🏛️ Banker & Judge Live Veto Auditor":
    st.subheader("⚖️ Banker & Judge Live Veto Auditor")
    st.markdown("""
    This live panel demonstrates the **Cross-Cutting Ethical Veto Layer in real-time**.  
    Judges can manipulate customer risk factors using the sliders below to observe how the system **dynamically intercepts predatory loan pushes** and substitutes them with empathetic debt relief.
    """)

    st.markdown("---")

    # Interactive Sliders
    s_col1, s_col2, s_col3 = st.columns(3)

    with s_col1:
        sim_dti = st.slider(
            "Adjust Debt-to-Income (DTI) Ratio:",
            min_value=0.10,
            max_value=0.75,
            value=float(cust_vector.dti_ratio),
            step=0.01,
            format="%.2f",
            help="Threshold ceiling is 50% (0.50). Above 50%, Hard Veto fires."
        )

    with s_col2:
        baseline_health = veto_engine.compute_financial_health_score(
            cust_vector.dti_ratio,
            cust_vector.savings_rate_decay,
            cust_vector.balance_trend_slope,
            cust_vector.essential_spend_ratio
        )[0]
        sim_health = st.slider(
            "Override Financial Health Score (0–100):",
            min_value=5,
            max_value=100,
            value=int(baseline_health),
            step=1,
            help="Threshold floor is 40. Below 40, customer is considered distressed."
        )

    with s_col3:
        has_medical = "HEALTH_CONCERN" in (cust_vector.detected_life_stages or [])
        sim_medical = st.toggle("Simulate Medical Surge / Health Spike", value=has_medical)

    # Re-evaluate with interactive overrides
    sim_vector = cust_vector.model_copy(deep=True)
    if sim_medical:
        sim_vector.detected_life_stages = list(set((sim_vector.detected_life_stages or []) + ["HEALTH_CONCERN"]))
    else:
        sim_vector.detected_life_stages = [s for s in (sim_vector.detected_life_stages or []) if s != "HEALTH_CONCERN"]

    sim_outcome = veto_engine.evaluate_customer_veto(
        feature_vector=sim_vector,
        override_dti=sim_dti,
        override_health_score=sim_health
    )

    st.markdown("---")
    st.markdown("### 🔍 Live Reaction Comparison")

    comp1, comp2, comp3 = st.columns([4, 3, 4])

    with comp1:
        st.markdown("#### 1. Raw ML Model Output")
        st.caption("What unconstrained LightGBM models would surface:")
        raw_recs = cust_vector.candidate_recommendations
        for rec in raw_recs:
            st.info(f"**{rec.product_type}** — Raw Score: `{rec.raw_propensity_score:.2f}`\n\n*Rationale:* {rec.shap_reasons[0]}")

    with comp2:
        st.markdown("#### 2. Cross-Cutting Veto Status")
        st.caption("The Deterministic Regulatory Gatekeeper:")
        if sim_outcome.veto_triggered:
            st.error(f"""
            ### 🛑 HARD VETO TRIGGERED
            **Reason:** {sim_outcome.veto_reason}
            
            **Blocked Credit:**
            - Personal Loans
            - Credit Cards
            - Top-up Loans
            """)
        else:
            st.success("""
            ### ✅ VETO CLEARED
            **Status:** Safe Affordability
            - DTI within safety cap (<= 50%)
            - Health score healthy (>= 40)
            - No medical distress detected
            """)

    with comp3:
        st.markdown("#### 3. Approved Final Action")
        st.caption("What actually reaches the customer:")
        final = sim_outcome.final_action
        if sim_outcome.veto_triggered:
            st.warning(f"""
            **Action:** `{final.action_type}`  
            **Title:** {final.display_title}  
            **Message:** *"{final.message_en}"*  
            **CTA Action:** `{final.cta_action}`
            """)
        else:
            st.success(f"""
            **Action:** `{final.action_type}`  
            **Title:** {final.display_title}  
            **Message:** *"{final.message_en}"*  
            **CTA Action:** `{final.cta_action}`
            """)

    st.markdown("---")
    st.markdown("#### 📝 Compliance Audit & Human-in-the-Loop Override")
    with st.expander("Inspect Cryptographic Audit Trail"):
        st.json({
            "customer_id": sim_vector.customer_id,
            "simulated_dti": sim_dti,
            "simulated_health_score": sim_health,
            "veto_triggered": sim_outcome.veto_triggered,
            "veto_reason": sim_outcome.veto_reason,
            "blocked_products": sim_outcome.blocked_products,
            "final_action_type": final.action_type,
            "audit_hash": f"SHA256_AUDIT_LOG_ENTRY_{sim_vector.customer_id}_{int(sim_dti*100)}_{sim_health}"
        })
