"""
feature_pipeline.py - Shared Feature Engineering Layer for BharatBanker AI.
Transforms raw transaction logs and KYC profiles into standardized financial ratios,
spend distribution vectors, and multi-week trend slopes.

Consolidated output feeds:
  - Person 1: K-Means Segmentation, Life-Stage Triggers, LightGBM Propensity
  - Person 2: Fraud Anomaly Scoring, Trend-Slope Stress Detection (Contract 1)
  - Person 4: FastAPI Gateway & Streamlit Customer Portal
"""

import os
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class CustomerFeaturePipeline:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.feature_matrix: Optional[pd.DataFrame] = None

    def fit_transform(
        self,
        customers_df: Optional[pd.DataFrame] = None,
        transactions_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Compute end-to-end customer financial ratios, spend mix vectors,
        and multi-week trend signals from transaction histories.
        """
        if customers_df is None:
            cust_path = os.path.join(self.data_dir, "customers.csv")
            customers_df = pd.read_csv(cust_path)
        if transactions_df is None:
            txns_path = os.path.join(self.data_dir, "transactions.csv")
            transactions_df = pd.read_csv(txns_path)

        transactions_df["date"] = pd.to_datetime(transactions_df["date"])
        transactions_df["month"] = transactions_df["date"].dt.month
        transactions_df["is_weekend"] = transactions_df["date"].dt.weekday >= 5

        records = []

        for _, cust in customers_df.iterrows():
            cid = cust["customer_id"]
            ctxns = transactions_df[transactions_df["customer_id"] == cid].sort_values("date")

            if ctxns.empty:
                continue

            credits = ctxns[ctxns["txn_type"] == "CREDIT"]
            debits = ctxns[ctxns["txn_type"] == "DEBIT"]

            # 1. Salary & Inflow Metrics
            salary_credits = ctxns[ctxns["category"] == "SALARY"]
            if not salary_credits.empty:
                # Latest salary vs early salary
                monthly_salary = float(salary_credits.iloc[-1]["amount"])
                earliest_salary = float(salary_credits.iloc[0]["amount"])
                salary_growth_rate = float((monthly_salary - earliest_salary) / (earliest_salary + 1e-5))
            else:
                monthly_salary = float(cust.get("base_salary", 35000))
                salary_growth_rate = 0.0

            # 2. Monthly Outflow Breakdowns
            emi_txns = ctxns[ctxns["category"] == "EMI"]
            monthly_emi = float(emi_txns["amount"].mean()) if not emi_txns.empty else 0.0

            rent_txns = ctxns[ctxns["category"] == "RENT"]
            monthly_rent = float(rent_txns["amount"].mean()) if not rent_txns.empty else 0.0

            util_txns = ctxns[(ctxns["category"] == "ESSENTIALS") & (ctxns["description"].str.contains("Bill", case=False, na=False))]
            monthly_utils = float(util_txns["amount"].mean()) if not util_txns.empty else 2000.0

            recurring_bills = monthly_rent + monthly_utils
            disposable_income = max(0.0, monthly_salary - monthly_emi - recurring_bills)

            # 3. Debt-to-Income (DTI) & Savings Ratio
            dti_ratio = float(monthly_emi / (monthly_salary + 1e-5))

            # Monthly savings = monthly inflow - monthly outflow
            monthly_inflows = credits.groupby("month")["amount"].sum()
            monthly_outflows = debits.groupby("month")["amount"].sum()
            all_months = sorted(list(set(ctxns["month"])))

            monthly_savings = []
            monthly_savings_rates = []
            monthly_emi_ratios = []

            for m in all_months:
                inf = float(monthly_inflows.get(m, monthly_salary))
                out = float(monthly_outflows.get(m, 0.0))
                sav = inf - out
                sr = sav / (inf + 1e-5)
                monthly_savings.append(sav)
                monthly_savings_rates.append(sr)

                m_emis = ctxns[(ctxns["month"] == m) & (ctxns["category"] == "EMI")]["amount"].sum()
                monthly_emi_ratios.append(float(m_emis / (inf + 1e-5)))

            avg_monthly_savings = float(np.mean(monthly_savings)) if monthly_savings else 0.0
            savings_ratio = float(avg_monthly_savings / (monthly_salary + 1e-5))

            # 4. Daily Balance Volatility & Mean Balance
            balances = ctxns["balance_after"].values
            mean_balance = float(np.mean(balances))
            std_balance = float(np.std(balances))
            balance_volatility = float(std_balance / (mean_balance + 1e-5))

            # 5. Spend Category Distribution Ratios
            total_debit_amt = float(debits["amount"].sum()) + 1e-5
            spend_by_cat = debits.groupby("category")["amount"].sum().to_dict()

            essential_spend_ratio = float(spend_by_cat.get("ESSENTIALS", 0.0) / total_debit_amt)
            discretionary_spend_ratio = float(spend_by_cat.get("DISCRETIONARY", 0.0) / total_debit_amt)
            medical_spend_ratio = float(spend_by_cat.get("MEDICAL", 0.0) / total_debit_amt)
            travel_spend_ratio = float(spend_by_cat.get("TRAVEL", 0.0) / total_debit_amt)
            education_spend_ratio = float(spend_by_cat.get("EDUCATION", 0.0) / total_debit_amt)
            luxury_spend_ratio = float(spend_by_cat.get("LUXURY", 0.0) / total_debit_amt)

            # Weekend vs Weekday Spend Ratio
            weekend_spend = debits[debits["is_weekend"]]["amount"].mean() if not debits[debits["is_weekend"]].empty else 0.0
            weekday_spend = debits[~debits["is_weekend"]]["amount"].mean() if not debits[~debits["is_weekend"]].empty else 1.0
            weekend_vs_weekday_ratio = float(weekend_spend / (weekday_spend + 1e-5))

            avg_transaction_size = float(debits["amount"].mean()) if not debits.empty else 0.0

            # 6. Multi-Week Trend Slopes (Shared with Person 2 Stress Detector)
            # a) Savings Rate Decay: slope of monthly savings rate over time
            if len(monthly_savings_rates) >= 3:
                x_time = np.arange(len(monthly_savings_rates))
                slope_sr, _ = np.polyfit(x_time, monthly_savings_rates, 1)
                savings_rate_decay = float(slope_sr)
            else:
                savings_rate_decay = 0.0

            # b) Balance Trend Slope: slope of end-of-month balances normalized by mean balance
            eom_balances = [ctxns[ctxns["month"] == m].iloc[-1]["balance_after"] for m in all_months]
            if len(eom_balances) >= 3:
                x_time = np.arange(len(eom_balances))
                slope_bal, _ = np.polyfit(x_time, eom_balances, 1)
                balance_trend_slope = float(slope_bal / (mean_balance + 1e-5))
            else:
                balance_trend_slope = 0.0

            # c) EMI to Inflow Trend Slope
            if len(monthly_emi_ratios) >= 3:
                slope_emi, _ = np.polyfit(np.arange(len(monthly_emi_ratios)), monthly_emi_ratios, 1)
                emi_to_inflow_trend = float(slope_emi)
            else:
                emi_to_inflow_trend = 0.0

            # d) Medical Spend Surge: Last 3 months vs First 3 months
            early_months = all_months[:3] if len(all_months) >= 3 else all_months[:1]
            late_months = all_months[3:] if len(all_months) >= 3 else all_months[1:]

            med_early = ctxns[(ctxns["month"].isin(early_months)) & (ctxns["category"] == "MEDICAL")]["amount"].sum()
            med_late = ctxns[(ctxns["month"].isin(late_months)) & (ctxns["category"] == "MEDICAL")]["amount"].sum()
            medical_spend_growth = float((med_late - med_early) / (med_early + 100.0))

            education_debit_count = int(len(ctxns[ctxns["category"] == "EDUCATION"]))
            has_home_loan = bool(monthly_emi > 0 and monthly_rent == 0 and cust.get("age", 30) > 32)

            records.append({
                "customer_id": cid,
                "name": cust["name"],
                "age": int(cust["age"]),
                "occupation": cust["occupation"],
                "city": cust["city"],
                "account_vintage_months": int(cust["account_vintage_months"]),
                "consent_tier": int(cust.get("consent_tier", 1)),
                "archetype": cust.get("archetype", "UNKNOWN"),
                # Core Financial Ratios
                "monthly_salary": round(monthly_salary, 2),
                "monthly_emi": round(monthly_emi, 2),
                "monthly_rent": round(monthly_rent, 2),
                "disposable_income": round(disposable_income, 2),
                "savings_ratio": round(savings_ratio, 4),
                "dti_ratio": round(dti_ratio, 4),
                "balance_volatility": round(balance_volatility, 4),
                "salary_growth_rate": round(salary_growth_rate, 4),
                "mean_balance": round(mean_balance, 2),
                "latest_balance": round(float(balances[-1]), 2),
                # Spend Mix Distribution
                "essential_spend_ratio": round(essential_spend_ratio, 4),
                "discretionary_spend_ratio": round(discretionary_spend_ratio, 4),
                "medical_spend_ratio": round(medical_spend_ratio, 4),
                "travel_spend_ratio": round(travel_spend_ratio, 4),
                "education_spend_ratio": round(education_spend_ratio, 4),
                "luxury_spend_ratio": round(luxury_spend_ratio, 4),
                "weekend_vs_weekday_ratio": round(weekend_vs_weekday_ratio, 4),
                "avg_transaction_size": round(avg_transaction_size, 2),
                # Trend Slopes for Person 2 & Contract 1
                "savings_rate_decay": round(savings_rate_decay, 4),
                "balance_trend_slope": round(balance_trend_slope, 4),
                "emi_to_inflow_trend": round(emi_to_inflow_trend, 4),
                "medical_spend_growth": round(medical_spend_growth, 4),
                # Triggers Metadata
                "has_rent": bool(monthly_rent > 0),
                "has_home_loan": has_home_loan,
                "education_debit_count": education_debit_count
            })

        self.feature_matrix = pd.DataFrame(records)
        return self.feature_matrix

    def save_features(self, filepath: Optional[str] = None):
        """Save computed feature matrix to disk."""
        if self.feature_matrix is None:
            raise ValueError("Feature matrix has not been computed yet. Call fit_transform() first.")
        path = filepath or os.path.join(self.data_dir, "feature_matrix.csv")
        self.feature_matrix.to_csv(path, index=False)
        print(f" -> Feature matrix successfully saved to {path} ({len(self.feature_matrix)} profiles)")

    def load_features(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """Load feature matrix from disk if already cached."""
        path = filepath or os.path.join(self.data_dir, "feature_matrix.csv")
        if os.path.exists(path):
            self.feature_matrix = pd.read_csv(path)
            return self.feature_matrix
        return self.fit_transform()

    def get_feature_vector(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve single customer feature vector by customer_id."""
        if self.feature_matrix is None:
            self.load_features()
        cust_row = self.feature_matrix[self.feature_matrix["customer_id"] == customer_id]
        if cust_row.empty:
            raise KeyError(f"Customer ID '{customer_id}' not found in feature matrix.")
        return cust_row.iloc[0].to_dict()


if __name__ == "__main__":
    pipeline = CustomerFeaturePipeline()
    feats = pipeline.fit_transform()
    pipeline.save_features()
    print("[OK] Feature pipeline executed successfully!")
    print(feats[["customer_id", "monthly_salary", "dti_ratio", "savings_rate_decay", "balance_trend_slope"]].head())
