"""
segmentation_engine.py - Behavioral Clustering & Temporal Life-Stage Triggers for BharatBanker AI.
Two-layer intelligence:
  Layer A: Unsupervised K-Means clustering with Silhouette Score optimization (k=3..12).
  Layer B: Rule-based Life-Stage Event Triggers for real-time temporal signals.
"""

import os
import sys
import pickle

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

CLUSTER_FEATURES = [
    "disposable_income",
    "savings_ratio",
    "dti_ratio",
    "balance_volatility",
    "essential_spend_ratio",
    "discretionary_spend_ratio",
    "medical_spend_ratio",
    "travel_spend_ratio",
    "luxury_spend_ratio"
]


class SegmentationEngine:
    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.scaler = StandardScaler()
        self.kmeans: Optional[KMeans] = None
        self.optimal_k: int = 5
        self.cluster_names: Dict[int, str] = {}
        self.model_path = os.path.join(self.models_dir, "kmeans_segmentation.pkl")

    def fit(self, feature_df: pd.DataFrame) -> Tuple[int, float]:
        """
        Run K-Means clustering across k = 3 to 12.
        Find optimal k via Silhouette Score maximization.
        Assign semantic names to clusters based on centroid values.
        """
        X = feature_df[CLUSTER_FEATURES].fillna(0.0).values
        X_scaled = self.scaler.fit_transform(X)

        best_k = 5
        best_score = -1.0
        n_samples = len(X_scaled)
        max_k = min(12, n_samples - 1)

        print("[Segmentation] Searching optimal k via Silhouette Score (k=3..12)...")
        for k in range(3, max_k + 1):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            print(f"  k={k}: silhouette_score = {score:.4f}")
            if score > best_score:
                best_score = score
                best_k = k

        self.optimal_k = best_k
        print(f"[OK] Selected optimal k={self.optimal_k} with Silhouette Score={best_score:.4f}")

        # Final fit with optimal k
        self.kmeans = KMeans(n_clusters=self.optimal_k, random_state=42, n_init=20)
        labels = self.kmeans.fit_predict(X_scaled)
        feature_df["cluster_id"] = labels

        # Label clusters semantically based on centroid characteristics
        self.cluster_names = self._assign_cluster_names(feature_df)
        self.save()
        return self.optimal_k, best_score

    def _assign_cluster_names(self, feature_df: pd.DataFrame) -> Dict[int, str]:
        """
        Inspect cluster centroids and assign human-readable banking segments:
          - Young Earners
          - Stable Professionals
          - Family Builders
          - High Net-worth
          - Financially Stressed
        """
        cluster_names = {}
        means = feature_df.groupby("cluster_id")[CLUSTER_FEATURES + ["monthly_salary", "age"]].mean()

        unassigned_clusters = set(means.index)

        # 1. Financially Stressed: highest DTI or lowest savings ratio
        stressed_id = means.sort_values(by="dti_ratio", ascending=False).index[0]
        cluster_names[stressed_id] = "Financially Stressed"
        unassigned_clusters.discard(stressed_id)

        # 2. High Net-worth: highest salary / luxury spend
        hnw_id = means.loc[list(unassigned_clusters)].sort_values(by="monthly_salary", ascending=False).index[0]
        cluster_names[hnw_id] = "High Net-worth"
        unassigned_clusters.discard(hnw_id)

        # 3. Young Earners: lowest age or highest discretionary spend
        if unassigned_clusters:
            young_id = means.loc[list(unassigned_clusters)].sort_values(by="age", ascending=True).index[0]
            cluster_names[young_id] = "Young Earners"
            unassigned_clusters.discard(young_id)

        # 4. Family Builders: highest age or highest medical/essential spend
        if unassigned_clusters:
            family_id = means.loc[list(unassigned_clusters)].sort_values(by="essential_spend_ratio", ascending=False).index[0]
            cluster_names[family_id] = "Family Builders"
            unassigned_clusters.discard(family_id)

        # 5. Remaining cluster(s): Stable Professionals
        for cid in unassigned_clusters:
            cluster_names[cid] = "Stable Professionals"

        for cid, cname in cluster_names.items():
            print(f"  Cluster {cid} -> {cname} (Centroid salary: Rs.{means.loc[cid, 'monthly_salary']:.0f}, DTI: {means.loc[cid, 'dti_ratio']:.2f})")

        return cluster_names

    def predict_cluster(self, feature_row: Dict[str, Any]) -> Tuple[int, str]:
        """Predict cluster index and semantic cluster name for a single customer feature row."""
        if self.kmeans is None:
            self.load()

        x = np.array([[feature_row.get(col, 0.0) for col in CLUSTER_FEATURES]])
        x_scaled = self.scaler.transform(x)
        cluster_id = int(self.kmeans.predict(x_scaled)[0])
        cluster_name = self.cluster_names.get(cluster_id, "Stable Professionals")
        return cluster_id, cluster_name

    def detect_life_stage_signals(self, feature_row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Layer B: Deterministic Life-Stage Event Triggers.
        Catches high-impact temporal signals that clustering averages out.
        Returns active signals with triggered recommendations and days_since_trigger.
        """
        signals = []

        # 1. SALARY JUMP (Promotion / Job Switch)
        salary_growth = feature_row.get("salary_growth_rate", 0.0)
        if salary_growth >= 0.28:
            signals.append({
                "signal": "SALARY_JUMP",
                "confidence": 0.95,
                "days_since_trigger": 5,
                "matched_products": ["SIP_INVESTMENT", "PREMIUM_CREDIT_CARD"],
                "reason_text": f"Salary jumped by {salary_growth*100:.0f}% over recent months, opening investment headroom"
            })

        # 2. NEW EARNER (First job / Starter)
        vintage = feature_row.get("account_vintage_months", 24)
        age = feature_row.get("age", 30)
        if vintage <= 6 or (age <= 25 and feature_row.get("dti_ratio", 0.0) == 0.0):
            signals.append({
                "signal": "NEW_EARNER",
                "confidence": 0.90,
                "days_since_trigger": 12,
                "matched_products": ["SIP_INVESTMENT"],
                "reason_text": "Early career stage with no active debt, ideal for starter SIP"
            })

        # 3. EDUCATION EXPENSE (School / College fees detected)
        edu_ratio = feature_row.get("education_spend_ratio", 0.0)
        edu_count = feature_row.get("education_debit_count", 0)
        if edu_ratio >= 0.04 or edu_count >= 2:
            signals.append({
                "signal": "EDUCATION_EXPENSE",
                "confidence": 0.88,
                "days_since_trigger": 8,
                "matched_products": ["HEALTH_INSURANCE"],
                "reason_text": "Recurring educational outflows detected for dependents"
            })

        # 4. POTENTIAL HOME BUYER (Renting with healthy disposable income and zero home loan)
        has_rent = feature_row.get("has_rent", False)
        has_home_loan = feature_row.get("has_home_loan", False)
        disposable_inc = feature_row.get("disposable_income", 0.0)
        if has_rent and not has_home_loan and disposable_inc >= 18000:
            signals.append({
                "signal": "POTENTIAL_HOME_BUYER",
                "confidence": 0.85,
                "days_since_trigger": 10,
                "matched_products": ["PERSONAL_LOAN"],
                "reason_text": "Consistent rent outflows with zero existing mortgage debt"
            })

        # 5. HEALTH CONCERN (Medical expense surge > 50%) -> Strictly Health Insurance, NEVER a loan!
        med_growth = feature_row.get("medical_spend_growth", 0.0)
        med_ratio = feature_row.get("medical_spend_ratio", 0.0)
        if med_growth >= 0.45 or med_ratio >= 0.10:
            signals.append({
                "signal": "HEALTH_CONCERN",
                "confidence": 0.98,
                "days_since_trigger": 3,
                "matched_products": ["HEALTH_INSURANCE"],
                "prohibited_products": ["PERSONAL_LOAN", "CREDIT_CARD"],
                "reason_text": f"Medical expenditures surged by {med_growth*100:.0f}%, indicating need for health cover"
            })

        # 6. FINANCIAL STRESS SIGNAL (DTI > 0.48 or decaying balance/savings)
        dti = feature_row.get("dti_ratio", 0.0)
        sr_decay = feature_row.get("savings_rate_decay", 0.0)
        bal_slope = feature_row.get("balance_trend_slope", 0.0)
        if dti >= 0.48 or (sr_decay < -0.04 and bal_slope < -0.04):
            signals.append({
                "signal": "FINANCIAL_STRESS",
                "confidence": 0.99,
                "days_since_trigger": 1,
                "matched_products": [],
                "prohibited_products": ["PERSONAL_LOAN", "PREMIUM_CREDIT_CARD"],
                "reason_text": f"Elevated debt-to-income ({dti*100:.1f}%) and declining balance trajectory detected"
            })

        return signals

    def save(self):
        """Serialize fitted clustering model, scaler, and cluster names."""
        state = {
            "scaler": self.scaler,
            "kmeans": self.kmeans,
            "optimal_k": self.optimal_k,
            "cluster_names": self.cluster_names
        }
        with open(self.model_path, "wb") as f:
            pickle.dump(state, f)
        print(f" -> Saved segmentation engine model state to {self.model_path}")

    def load(self):
        """Load fitted clustering model, scaler, and cluster names."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}. Run fit() first.")
        with open(self.model_path, "rb") as f:
            state = pickle.load(f)
        self.scaler = state["scaler"]
        self.kmeans = state["kmeans"]
        self.optimal_k = state["optimal_k"]
        self.cluster_names = state["cluster_names"]


if __name__ == "__main__":
    from feature_pipeline import CustomerFeaturePipeline
    pipeline = CustomerFeaturePipeline()
    feature_df = pipeline.load_features()

    engine = SegmentationEngine()
    engine.fit(feature_df)
    sample_cust = feature_df.iloc[0].to_dict()
    cid, cname = engine.predict_cluster(sample_cust)
    triggers = engine.detect_life_stage_signals(sample_cust)
    print(f"Sample: {sample_cust['customer_id']} -> Cluster: {cname} (ID: {cid}), Triggers: {[t['signal'] for t in triggers]}")
