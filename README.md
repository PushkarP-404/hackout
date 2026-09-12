# BharatBanker AI

> **Unified Decisioning Platform for Hyper-Personalized Banking, Vernacular Conversational AI, and Empathetic Stress/Fraud Detection**  
> *Theme:* Digital Transformation in Lending  
> *Repository:* `hackout`

---

## 🌟 Overview

BharatBanker AI is an intelligent banking companion built for Bharat. It treats proactive product recommendation, multilingual conversational access, and fraud/financial-stress detection as a single connected decisioning platform.

### Core Architectural Pillars
1. **Smart Recommendation Engine (Sub-Problem 1):** Behavioural segmentation (K-Means) + per-product LightGBM propensity scoring with plain-language SHAP explainability.
2. **Vernacular Conversational AI (Sub-Problem 2):** Dual-engine chatbot combining deterministic slot-filling for KYC/loan applications (with Verhoeff Aadhaar checksum validation) and multilingual RAG over curated RBI/PMJDY policies (using `multilingual-e5`/`LaBSE` + FAISS).
3. **Financial Health & Fraud Monitor (Sub-Problem 3):** Unsupervised transaction anomaly detection (Isolation Forest / PyOD) on PaySim data + multi-week financial stress-trend classifier and 0–100 Financial Health Score.
4. **Unified Cross-Cutting Veto Layer:** The central gatekeeper enforcing a non-negotiable hard floor (`if stress > threshold or DTI > 50%: block credit pushes, swap to empathetic restructuring support`).

---

## 📁 Repository Structure

```
├── .gitignore
├── AGENTS.md                   # Operating guidelines & constraints for AI coding agents
├── CLAUDE.md                   # Developer & assistant guidelines for Claude
├── README.md                   # Project overview & quickstart
├── team_distribution.md        # Roles, responsibilities, deliverables & API contracts
└── docs/                       # Core solution documents & research papers
    ├── BharatBanker_AI_Unified_Solution.pdf  # Primary technical source of truth
    ├── approach_problem1.md                  # Feature engineering & clustering calculations
    ├── hackathon-technical-report.pdf        # Architecture & dataset technical report
    ├── technical_report.pdf                  # Complete solution technical report
    └── Security portion of the program (1).docx # Application security & compliance guide
```

---

## 👥 Team Distribution (Team of 4)

See [`team_distribution.md`](file:///c:/Users/pushk/OneDrive/Desktop/Hackout/team_distribution.md) for full breakdown and API contracts:
- **Person 1:** ML & Personalization Lead (Feature Pipeline, K-Means, LightGBM, SHAP)
- **Person 2:** Risk ML & Veto Systems Lead (PaySim Fraud Isolation Forest, Stress Slope Classifier, Hard Veto Engine)
- **Person 3:** Conversational AI & RAG Lead (Loan Slot-Filling with Verhoeff Checksum, Multilingual FAISS RAG, Intent Router)
- **Person 4:** Platform, Security & Demo Lead (FastAPI Gateway, IDOR/Rate Limiting/JWT Security, Streamlit UI & Banker Audit Mode)

---

## 🚀 Quickstart (Planned)

### 1. Setup Environment
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Launch Backend API
```bash
uvicorn main_api:app --reload --port 8000
```

### 3. Launch Prototype UI
```bash
streamlit run app.py
```
