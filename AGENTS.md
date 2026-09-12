# AGENTS.md — BharatBanker AI Agent Operating Guidelines

> **Theme:** Digital Transformation in Lending  
> **Project:** BharatBanker AI (Unified Decisioning Platform for Hyper-Personalization, Vernacular Conversational Banking, and Empathetic Stress/Fraud Detection)

This file governs the behavior, constraints, and priorities for all AI coding assistants, agents, and automated pair-programmers working on this repository.

---

## 1. Documentation Hierarchy & Source of Truth

When reading context, generating code, or planning architectures, you **MUST** strictly adhere to this order of precedence:

1. **PRIMARY TECHNICAL SOURCE OF TRUTH (Highest Priority):**
   - 📄 [`BharatBanker_AI_Unified_Solution.pdf`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/BharatBanker_AI_Unified_Solution.pdf)
   - *Rule:* All architectural choices, mathematical formulations, technology selections (LightGBM, SHAP, PyOD, FAISS, multilingual-e5), and regulatory guardrails defined in this document supersede any conflicting assumptions or external conventions.

2. **TEAM EXECUTION & ROLE SOURCE OF TRUTH (Strict Adherence Required):**
   - 📄 [`team_distribution.md`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/team_distribution.md)
   - *Rule:* All tasks, deliverables, API schemas, and inter-service contracts MUST strictly follow the role distribution established in this document.

3. **SUPPORTING TECHNICAL REFERENCES:**
   - 📄 [`approach_problem1.md`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/approach_problem1.md): Deep-dive feature engineering calculations, K-Means clustering, and life-stage trigger rules.
   - 📄 [`hackathon-technical-report.pdf`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/hackathon-technical-report.pdf): Extended system architecture and dataset rationale.
   - 📄 [`Security portion of the program (1).docx`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/docs/Security%20portion%20of%20the%20program%20(1).docx): Mandatory baseline application security requirements.

---

## 2. Role-Based Execution Protocol

Every developer on this team has been assigned one of four distinct roles defined in [`team_distribution.md`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/team_distribution.md).

**Before implementing code, identify or ask which role the current session is targeting:**

### 👤 Person 1: ML & Personalization Lead
- **Scope:** Sub-Problem 1 (Smart Recommendation Engine) + Shared Feature Engineering Pipeline.
- **Owned Deliverables:**
  - `data_generator.py`: Synthetic 100-customer, 6-month transaction dataset (`customer_360_data.csv`).
  - `feature_pipeline.py`: Financial ratios (`disposable_income`, `savings_ratio`, `dti_ratio`, `balance_volatility`, spend distribution vector).
  - `segmentation_engine.py`: K-Means clustering ($k=3$ to $12$ silhouette optimization) + life-stage event trigger rules (`SALARY_JUMP`, `NEW_EARNER`, `EDUCATION_EXPENSE`, `POTENTIAL_HOME_BUYER`, `HEALTH_CONCERN`).
  - `recommendation_engine.py`: LightGBM propensity models (Loan, Insurance), multi-factor ranking formula with exponential timing decay, and SHAP-to-plain-text explanation generator.
- **Boundary Constraint:** Output must conform to the **Contract 1: Customer Feature Vector** schema in `team_distribution.md`.

### 👤 Person 2: Risk ML & Veto Systems Lead
- **Scope:** Sub-Problem 3 (Fraud & Financial Stress Detection) + Cross-Cutting Veto / Decision Layer.
- **Owned Deliverables:**
  - `fraud_detector.py`: Unsupervised anomaly detection on PaySim transaction logs using `Isolation Forest` / `PyOD`.
  - `stress_detector.py`: Multi-week trend-slope classifier (EMI-to-inflow rise, savings decay, spend shift toward essentials, balance-floor drift) and 0–100 Financial Health Score.
  - `veto_decision_layer.py`: The single gatekeeper enforcing the **Hard Veto Floor** (`if stress > threshold or dti > 0.50: block credit push, swap to empathetic intervention`).
  - `test_veto_scenarios.py`: Validated edge cases for judge demonstration.
- **Boundary Constraint:** Output must conform to the **Contract 2: Veto & Decision Layer Outcome** schema in `team_distribution.md`.

### 👤 Person 3: Conversational AI & Multilingual RAG Lead
- **Scope:** Sub-Problem 2 (Vernacular Conversational AI — Slot-Filling + Grounded RAG).
- **Owned Deliverables:**
  - `slot_filling_engine.py`: Structured loan application state machine with deterministic PAN regex and **Aadhaar Verhoeff Checksum Algorithm** for last-4 digits. Plain-language vernacular error guidance.
  - `rag_engine.py`: Vector search over curated RBI/PMJDY/NPCI guidelines using `multilingual-e5` / `LaBSE` and local `FAISS` index, with strict source citations.
  - `intent_router.py`: Per-turn dispatcher allowing mid-KYC policy detours without resetting collected slots.
  - `chat_service.py`: High-level controller exposing session-based chat endpoints.
- **Boundary Constraint:** Output must conform to the **Contract 3: Conversational Chatbot Payload** schema in `team_distribution.md`.

### 👤 Person 4: Platform, Security & Demo Lead
- **Scope:** Central API Gateway, Security Guardrails, Interactive Dashboards & Judge Pitch Experience.
- **Owned Deliverables:**
  - `main_api.py`: FastAPI server orchestrating Person 1, 2, and 3 services.
  - `security_middleware.py`: Insecure Direct Object Reference (IDOR) prevention, API rate limiting (`slowapi`), Pydantic input sanitization, JWT auth, and DPDP tiered consent validation.
  - `app.py`: Interactive UI (Streamlit or Next.js) featuring Customer Portal, embedded Vernacular Chat, and the **Banker / Judge Live Veto Auditor**.
  - `demo_walkthrough.md`: Presentation flow and test script.
- **Boundary Constraint:** Must consume contracts from Persons 1, 2, and 3 without forcing ad-hoc schema changes.

---

## 3. Non-Negotiable Core Technical Constraints

1. **The Ethical Hard Veto is Non-Negotiable**:
   - A pure soft-discounting model is prohibited for high-stress users. If a customer is flagged as financially distressed ($\text{DTI} > 50\%$ or health score in critical/distressed band), credit pushes **MUST** be programmatically blocked by a hard floor.
   - Do not recommend loans to customers with medical expense surges—recommend health insurance instead.

2. **Explainability by Construction**:
   - Every product recommendation must include human-readable rationale generated from SHAP values.
   - Every RAG response must cite the official source document and section (e.g., `[Source: RBI Digital Lending Guidelines, Sec 4.2]`).
   - Hallucinating lending terms when retrieval context is missing is strictly forbidden.

3. **Data Privacy & DPDP Act 2023 Compliance**:
   - **Never** store, log, or request full 12-digit Aadhaar numbers. Only collect the last 4 digits and validate them using the Verhoeff checksum.
   - Respect tiered consent: Tier 0 (implicit account data), Tier 1 (opt-in behavioral), Tier 2 (explicit life-stage).

4. **Application Security Standards**:
   - Always implement **IDOR prevention** on customer endpoints (`current_user.id == target_customer.id`).
   - Enforce rate limiting on login, transaction screening, and chat endpoints.
   - Validate and sanitize all inputs via Pydantic models to prevent injection and XSS.

---

## 4. Coding & Architecture Standards

- **Language:** Python 3.10+
- **Primary Web Framework:** FastAPI for backend services.
- **UI Framework:** Streamlit (preferred for hackathon speed and native SHAP support) or Next.js if pre-built.
- **ML/DS Libraries:** `pandas`, `numpy`, `scikit-learn`, `lightgbm`, `shap`, `pyod`, `sentence-transformers`, `faiss-cpu`.
- **Modularity:** Keep modules decoupled. Services must communicate through typed Pydantic models matching the schemas in `team_distribution.md`.
