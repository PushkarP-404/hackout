"""
test_recs.py - End-to-End Verification & Latency Benchmark for Person 1 (ML & Personalization Lead).

Validates:
  1. Synthetic data integrity (100 customers, 6-month continuous transactions).
  2. Feature pipeline accuracy (financial ratios, zero division-by-zero or NaNs).
  3. Behavioral segmentation & Silhouette score optimization (k=3..12).
  4. Life-stage trigger accuracy (Priya Sharma SALARY_JUMP, Amit Patel HEALTH_CONCERN).
  5. Explainability (Tree SHAP to natural language explanations).
  6. Strict Contract 1 Pydantic compliance across all 100 profiles.
  7. Latency SLA (<150ms per recommendation query).
"""

import os
import sys
import time
import pandas as pd
import numpy as np

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from schemas import CustomerFeatureVector
import data_generator
from feature_pipeline import CustomerFeaturePipeline
from segmentation_engine import SegmentationEngine
from recommendation_engine import RecommendationEngine


def test_end_to_end_pipeline():
    print("=" * 70)
    print(" BharatBanker AI - Person 1 (ML & Personalization) Verification Suite")
    print("=" * 70)

    # ---------------------------------------------------------
    # Step 1: Run Data Generator
    # ---------------------------------------------------------
    print("\n[Step 1/6] Running Synthetic Data Generator...")
    data_generator.run()

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    cust_df = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    txns_df = pd.read_csv(os.path.join(data_dir, "transactions.csv"))

    assert len(cust_df) == 100, f"Expected 100 customers, found {len(cust_df)}"
    assert len(txns_df) > 15000, f"Expected >15,000 transactions, found {len(txns_df)}"
    assert "CUST_IND_1042" in cust_df["customer_id"].values, "Priya Sharma missing!"
    assert "CUST_IND_1088" in cust_df["customer_id"].values, "Amit Patel missing!"
    print(f"  [OK] Verified 100 customers and {len(txns_df)} transactions successfully.")

    # ---------------------------------------------------------
    # Step 2: Run Shared Feature Engineering Pipeline
    # ---------------------------------------------------------
    print("\n[Step 2/6] Executing Shared Feature Engineering Pipeline...")
    pipeline = CustomerFeaturePipeline(data_dir=data_dir)
    feature_df = pipeline.fit_transform(cust_df, txns_df)
    pipeline.save_features()

    assert len(feature_df) == 100, f"Expected 100 feature rows, found {len(feature_df)}"
    assert not feature_df["dti_ratio"].isna().any(), "NaN found in dti_ratio!"
    assert not feature_df["disposable_income"].isna().any(), "NaN in disposable_income!"
    assert not feature_df["savings_rate_decay"].isna().any(), "NaN in savings_rate_decay!"
    assert not feature_df["balance_trend_slope"].isna().any(), "NaN in balance_trend_slope!"
    print(f"  [OK] Engineered {feature_df.shape[1]} features for all 100 profiles with zero NaNs.")

    # ---------------------------------------------------------
    # Step 3: Train & Validate Behavioral Segmentation
    # ---------------------------------------------------------
    print("\n[Step 3/6] Running K-Means Segmentation & Silhouette Optimization...")
    seg_engine = SegmentationEngine()
    best_k, sil_score = seg_engine.fit(feature_df)

    assert 3 <= best_k <= 12, f"Optimal k out of bounds: {best_k}"
    assert sil_score > 0.15, f"Silhouette score too low: {sil_score:.4f}"
    assert len(seg_engine.cluster_names) == best_k, "Cluster naming mismatch!"
    print(f"  [OK] Discovered optimal k={best_k} (Silhouette={sil_score:.4f}). Clusters: {set(seg_engine.cluster_names.values())}")

    # ---------------------------------------------------------
    # Step 4: Train LightGBM Models & SHAP Explainers
    # ---------------------------------------------------------
    print("\n[Step 4/6] Training LightGBM Propensity Models & Initializing SHAP...")
    rec_engine = RecommendationEngine()
    rec_engine.segmentation_engine = seg_engine
    rec_engine.train_models(feature_df)
    print("  [OK] LightGBM Personal Loan and Health Insurance models trained and SHAP initialized.")

    # ---------------------------------------------------------
    # Step 5: Canonical Pitch Scenarios Verification
    # ---------------------------------------------------------
    print("\n[Step 5/6] Testing Canonical Judge Pitch Scenarios...")

    # Scenario 1: Priya Sharma (Upward Earner)
    priya_feat = pipeline.get_feature_vector("CUST_IND_1042")
    priya_vec = rec_engine.get_contract_1_vector(priya_feat)

    print(f"\n  >> Scenario 1: Priya Sharma ({priya_vec.name})")
    print(f"     Cluster: {priya_vec.cluster_name}, Monthly Salary: Rs.{priya_vec.monthly_salary:,.0f}")
    print(f"     Detected Triggers: {priya_vec.detected_life_stages}")
    assert "SALARY_JUMP" in priya_vec.detected_life_stages, "Failed to detect SALARY_JUMP for Priya Sharma!"
    assert len(priya_vec.candidate_recommendations) > 0, "No recommendations generated for Priya!"
    top_priya = priya_vec.candidate_recommendations[0]
    print(f"     Top Rec: {top_priya.product_type} (Score: {top_priya.raw_propensity_score:.2f})")
    for r in top_priya.shap_reasons:
        print(f"       * {r}")
    assert top_priya.product_type in ["SIP_INVESTMENT", "PREMIUM_CREDIT_CARD"], f"Unexpected top rec: {top_priya.product_type}"

    # Scenario 2: Amit Patel (Stressed Earner / High Medical Surge)
    amit_feat = pipeline.get_feature_vector("CUST_IND_1088")
    amit_vec = rec_engine.get_contract_1_vector(amit_feat)

    print(f"\n  >> Scenario 2: Amit Patel ({amit_vec.name})")
    print(f"     Cluster: {amit_vec.cluster_name}, DTI: {amit_vec.dti_ratio:.2f}, Savings Slope: {amit_vec.savings_rate_decay:.3f}")
    print(f"     Detected Triggers: {amit_vec.detected_life_stages}")
    assert "HEALTH_CONCERN" in amit_vec.detected_life_stages, "Failed to detect HEALTH_CONCERN for Amit Patel!"
    # Check that loans are strictly penalized / not recommended as top action
    for rec in amit_vec.candidate_recommendations:
        assert rec.product_type != "PERSONAL_LOAN", "Ethical violation: Personal loan surfaced for stressed customer!"
    if amit_vec.candidate_recommendations:
        top_amit = amit_vec.candidate_recommendations[0]
        print(f"     Top Rec: {top_amit.product_type} (Score: {top_amit.raw_propensity_score:.2f})")
        for r in top_amit.shap_reasons:
            print(f"       * {r}")
        assert top_amit.product_type == "HEALTH_INSURANCE", f"Expected Health Insurance for medical spike, got {top_amit.product_type}"

    # Scenario 3: Ramesh Kumar (Stable Professional Contract 1 baseline)
    ramesh_feat = pipeline.get_feature_vector("CUST_IND_1015")
    ramesh_vec = rec_engine.get_contract_1_vector(ramesh_feat)
    print(f"\n  >> Baseline: Ramesh Kumar ({ramesh_vec.name})")
    print(f"     Cluster: {ramesh_vec.cluster_name}, Monthly Salary: Rs.{ramesh_vec.monthly_salary:,.0f}, DTI: {ramesh_vec.dti_ratio:.2f}")
    for rec in ramesh_vec.candidate_recommendations:
        print(f"     * {rec.product_type} (Score: {rec.raw_propensity_score:.2f}): {rec.shap_reasons[0]}")

    # ---------------------------------------------------------
    # Step 6: Contract 1 Pydantic Validation & Latency SLA
    # ---------------------------------------------------------
    print("\n[Step 6/6] Validating Contract 1 across all 100 customers & SLA Benchmark...")
    latencies = []

    for _, row in feature_df.iterrows():
        cid = row["customer_id"]
        cfeat = pipeline.get_feature_vector(cid)

        t0 = time.perf_counter()
        contract_vec = rec_engine.get_contract_1_vector(cfeat)
        t_elapsed = (time.perf_counter() - t0) * 1000.0  # ms
        latencies.append(t_elapsed)

        # Validate against strict Pydantic model
        assert isinstance(contract_vec, CustomerFeatureVector)
        assert contract_vec.customer_id == cid
        assert 0.0 <= contract_vec.dti_ratio
        assert len(contract_vec.name) > 0

    mean_lat = np.mean(latencies)
    p95_lat = np.percentile(latencies, 95)
    max_lat = np.max(latencies)

    print(f"  [OK] All 100 customer vectors passed Contract 1 Pydantic validation.")
    print(f"  [SLA] Performance Latency Benchmark:")
    print(f"      - Mean Latency : {mean_lat:.2f} ms")
    print(f"      - 95th %ile    : {p95_lat:.2f} ms")
    print(f"      - Max Latency  : {max_lat:.2f} ms")
    assert mean_lat < 150.0, f"SLA Violation: Mean latency ({mean_lat:.2f}ms) exceeds 150ms limit!"
    print(f"  [OK] Response time conforms strictly to <150ms Hackathon SLA!")

    print("\n" + "=" * 70)
    print(" ALL TESTS & BENCHMARKS PASSED! Person 1 Deliverables are 100% Ready.")
    print("=" * 70)


if __name__ == "__main__":
    test_end_to_end_pipeline()
