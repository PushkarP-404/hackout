# CLAUDE.md — BharatBanker AI Assistant Guide

> **Hackathon Theme:** Digital Transformation in Lending  
> **Project:** BharatBanker AI  
> **Repository Context:** Unified decisioning platform integrating proactive product recommendations, vernacular conversational banking, and empathetic stress/fraud detection.

---

## 1. Documentation & Knowledge Priority

Always consult documents in this strict order of priority:

1. **Top Priority (Primary Source of Truth):**
   - 📄 [`BharatBanker_AI_Unified_Solution.pdf`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/BharatBanker_AI_Unified_Solution.pdf)  
     *All algorithmic choices (LightGBM, PyOD, SHAP, FAISS, multilingual-e5), unified architecture, decision veto layer, and regulatory safeguards defined here take absolute precedence.*
2. **Team Role & Execution Plan (Strict Adherence):**
   - 📄 [`team_distribution.md`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/team_distribution.md)  
     *Must be followed strictly according to the specific role assigned to the user or task. Do not violate the API contracts or cross role boundaries.*
3. **Reference Documents:**
   - 📄 [`approach_problem1.md`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/approach_problem1.md) (Feature engineering, K-Means clustering, life-stage triggers)
   - 📄 [`hackathon-technical-report.pdf`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/hackathon-technical-report.pdf) (Architecture deep-dive, PaySim/synthetic datasets)
   - 📄 [`Security portion of the program (1).docx`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/Security%20portion%20of%20the%20program%20(1).docx) (IDOR prevention, rate limiting, JWT, DPDP)

---

## 2. Team Role Assignments (Follow the Assigned Role Strictly)

Before writing or editing code, verify which role the current task corresponds to:

| Member | Focus | Key Modules Owned | API Contract / Output |
|---|---|---|---|
| **Person 1** | ML & Personalization | `data_generator.py`, `feature_pipeline.py`, `segmentation_engine.py`, `recommendation_engine.py` | Produces `Contract 1: Customer Feature Vector` (100 synthetic profiles, K-Means clusters, LightGBM propensity, SHAP values). |
| **Person 2** | Risk ML & Veto Layer | `fraud_detector.py`, `stress_detector.py`, `veto_decision_layer.py`, `test_veto_scenarios.py` | Produces `Contract 2: Veto & Decision Layer Outcome` (Isolation Forest on PaySim, trend-slope stress classifier, 0–100 health score, hard veto floor). |
| **Person 3** | Conversational AI & RAG | `slot_filling_engine.py`, `rag_engine.py`, `intent_router.py`, `chat_service.py` | Produces `Contract 3: Conversational Chatbot Payload` (Loan slot-filling with Verhoeff Aadhaar checksum, multilingual FAISS RAG over RBI docs). |
| **Person 4** | Platform, Security & UI | `main_api.py`, `security_middleware.py`, `app.py`, `demo_walkthrough.md` | Central FastAPI gateway, IDOR prevention, rate limiting, JWT auth, DPDP consent tiers, Streamlit Customer Portal & Banker Live Veto Auditor. |

*Rule:* Work within your designated role's files. Do not modify another role's internal logic unless coordinating via the frozen JSON contracts in `team_distribution.md` Section 4.

---

## 3. Mandatory Engineering & Security Guardrails

- **Hard Veto Floor:** If a customer’s stress score exceeds the threshold or projected $\text{DTI} > 50\%$, credit products (loans/cards) **MUST** be programmatically blocked and replaced with empathetic support (EMI restructuring, budgeting advice). No soft weighting may override a hard veto.
- **Explainability:** Attach plain-language explanations generated from SHAP values to every recommendation.
- **RAG Grounding & Citations:** RAG answers must cite their regulatory source (RBI / PMJDY / NPCI). The model must decline to guess if documents lack the answer.
- **Aadhaar Protection:** Never request, store, or log full 12-digit Aadhaar numbers. Only accept last 4 digits and validate via the **Verhoeff algorithm**.
- **Application Security:**
  - Prevent Insecure Direct Object References (IDOR): ensure `authenticated_user_id == resource.owner_id`.
  - Apply API rate limits via `slowapi` on auth, chat, and transaction routes.
  - Sanitize all inputs using Pydantic models to prevent SQLi and XSS.
  - Use short-lived JWTs (15 min) with simulated OTP MFA for loan submissions.

---

## 4. Development Workflow & Commands

### Setup Virtual Environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Install core dependencies:
pip install fastapi uvicorn pydantic streamlit pandas numpy scikit-learn lightgbm shap pyod sentence-transformers faiss-cpu slowapi python-jose[cryptography] passlib
```

### Running Backend API
```bash
uvicorn main_api:app --host 127.0.0.1 --port 8000 --reload
```

### Running UI / Prototype
```bash
streamlit run app.py
```

### Running Tests
```bash
pytest tests/
# Or individual test suites:
python test_recs.py
python test_veto_scenarios.py
```
