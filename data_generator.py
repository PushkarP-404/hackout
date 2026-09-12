"""
data_generator.py - Synthetic 100-Customer and 6-Month Transaction Generator for BharatBanker AI.
Generates:
  1. data/customers.csv (100 synthetic profiles, archetypes, consent tiers)
  2. data/transactions.csv (~20,000-25,000 daily transaction events over 180 days)
  3. data/customer_360_data.csv (Consolidated Customer 360 features)
"""

import os
import random
import datetime
from typing import List, Dict, Any
import numpy as np
import pandas as pd

# Set deterministic random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Canonical Demo Profiles specified in team_distribution.md & solution docs
CANONICAL_PROFILES = [
    {
        "customer_id": "CUST_IND_1042",
        "name": "Priya Sharma",
        "age": 26,
        "occupation": "Software Engineer",
        "city": "Bengaluru",
        "state": "Karnataka",
        "account_vintage_months": 28,
        "consent_tier": 2,
        "archetype": "UPWARD_EARNER",  # Salary jump 45k -> 75k
        "base_salary": 45000,
        "promoted_salary": 75000,
        "promotion_month": 4,  # jumps at month 4 (last 2-3 months)
        "base_emi": 8000,
        "initial_balance": 35000
    },
    {
        "customer_id": "CUST_IND_1088",
        "name": "Amit Patel",
        "age": 42,
        "occupation": "Small Merchant",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "account_vintage_months": 45,
        "consent_tier": 1,
        "archetype": "STRESSED_EARNER",  # High medical spend surge > 60%, DTI > 50%
        "base_salary": 55000,
        "promoted_salary": 55000,
        "promotion_month": 99,
        "base_emi": 24000,
        "initial_balance": 40000
    },
    {
        "customer_id": "CUST_IND_1015",
        "name": "Ramesh Kumar",
        "age": 34,
        "occupation": "IT Operations Manager",
        "city": "Pune",
        "state": "Maharashtra",
        "account_vintage_months": 24,
        "consent_tier": 1,
        "archetype": "STABLE_PROFESSIONAL",  # Contract 1 baseline
        "base_salary": 65000,
        "promoted_salary": 65000,
        "promotion_month": 99,
        "base_emi": 24700,  # DTI ~0.38
        "initial_balance": 60000
    },
    {
        "customer_id": "CUST_IND_1002",
        "name": "Sunita Devi",
        "age": 38,
        "occupation": "Textile Artisan",
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "account_vintage_months": 18,
        "consent_tier": 0,
        "archetype": "VERNACULAR_USER",
        "base_salary": 28000,
        "promoted_salary": 28000,
        "promotion_month": 99,
        "base_emi": 3500,
        "initial_balance": 18000
    }
]

ARCHETYPES = [
    "YOUNG_EARNER",
    "STABLE_PROFESSIONAL",
    "FAMILY_BUILDER",
    "HIGH_NETWORTH",
    "FINANCIALLY_STRESSED"
]

INDIAN_FIRST_NAMES = [
    "Aarav", "Aditi", "Ajay", "Alok", "Ananya", "Anil", "Anita", "Anjali", "Arjun", "Ashok",
    "Deepak", "Deepika", "Divya", "Gaurav", "Geeta", "Harish", "Ishaan", "Kavita", "Kiran",
    "Manish", "Meera", "Mohit", "Neha", "Nikhil", "Nisha", "Pooja", "Pradeep", "Rahul", "Rajesh",
    "Rekha", "Ritu", "Rohit", "Rohan", "Sachin", "Sandhya", "Sanjay", "Sapna", "Shalini", "Shikha",
    "Sneha", "Suresh", "Swati", "Tarun", "Umesh", "Varun", "Vandana", "Vikas", "Vikram", "Vivek"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Malhotra", "Bhatia", "Saxena", "Mehta", "Chopra", "Joshi", "Kapoor",
    "Singh", "Yadav", "Trivedi", "Mishra", "Pandey", "Iyer", "Nair", "Reddy", "Patel", "Shah",
    "Deshmukh", "Kulkarni", "Banerjee", "Chatterjee", "Dutta", "Das", "Mukherjee", "Bose", "Ghosh", "Sen"
]

CITIES = [
    ("Bengaluru", "Karnataka"), ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"),
    ("Hyderabad", "Telangana"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"), ("Indore", "Madhya Pradesh"), ("Coimbatore", "Tamil Nadu"),
    ("Chandigarh", "Punjab"), ("Kochi", "Kerala"), ("Varanasi", "Uttar Pradesh")
]

OCCUPATIONS = [
    "Software Engineer", "Data Analyst", "Operations Executive", "Accountant",
    "Sales Manager", "School Teacher", "Healthcare Worker", "Small Merchant",
    "Civil Engineer", "Bank Officer", "Digital Marketer", "Logistics Supervisor"
]

SPEND_CATEGORIES = {
    "ESSENTIALS": [
        ("Kirana & Supermarket", 300, 2500),
        ("Milk & Dairy Delivery", 100, 800),
        ("Electricity & Utility Bill", 800, 3500),
        ("Mobile & Broadband Recharge", 399, 1499),
        ("Pharmacy & Daily Meds", 150, 1200)
    ],
    "DISCRETIONARY": [
        ("Swiggy / Zomato Food Order", 250, 950),
        ("Dining & Restaurant", 600, 3000),
        ("Amazon / Flipkart Shopping", 500, 4500),
        ("PVR Cinema / BookMyShow", 400, 1500),
        ("Weekend Cafe & Social", 300, 1200)
    ],
    "TRAVEL": [
        ("Uber / Ola Ride", 120, 750),
        ("Petrol / Fuel Station", 500, 3000),
        ("Metro / Train Card Recharge", 200, 1000),
        ("IRCTC Ticket Booking", 450, 3500),
        ("MakeMyTrip Flight Booking", 3500, 9000)
    ],
    "MEDICAL": [
        ("Apollo Diagnostics / Lab Test", 1000, 4500),
        ("Consultation at Multi-Specialty Clinic", 800, 2500),
        ("Hospital In-patient Outflow", 8000, 45000),
        ("Specialty Prescription Meds", 1200, 6000)
    ],
    "EDUCATION": [
        ("EuroKids / DPS School Fee", 6000, 25000),
        ("College Tuition Installment", 15000, 50000),
        ("Byju's / Coaching Classes", 2500, 8000)
    ],
    "LUXURY": [
        ("Tanishq Jewelry Store", 15000, 75000),
        ("Apple Store / Croma Electronics", 12000, 65000),
        ("Taj / Marriott Weekend Stay", 10000, 35000)
    ]
}


def generate_customers() -> List[Dict[str, Any]]:
    """Generate 100 customer demographic profiles."""
    customers = list(CANONICAL_PROFILES)
    used_names = {c["name"] for c in CANONICAL_PROFILES}

    # Generate remaining 96 customers across archetypes
    archetype_distribution = (
        ["YOUNG_EARNER"] * 24 +
        ["STABLE_PROFESSIONAL"] * 30 +
        ["FAMILY_BUILDER"] * 22 +
        ["HIGH_NETWORTH"] * 10 +
        ["FINANCIALLY_STRESSED"] * 10
    )
    random.shuffle(archetype_distribution)

    for i, arch in enumerate(archetype_distribution):
        cust_id = f"CUST_IND_{1100 + i}"
        while True:
            full_name = f"{random.choice(INDIAN_FIRST_NAMES)} {random.choice(INDIAN_LAST_NAMES)}"
            if full_name not in used_names:
                used_names.add(full_name)
                break

        city, state = random.choice(CITIES)
        occupation = random.choice(OCCUPATIONS)
        consent_tier = random.choice([0, 1, 1, 2, 2])

        if arch == "YOUNG_EARNER":
            age = random.randint(22, 27)
            account_vintage = random.randint(3, 18)
            base_salary = random.randint(25, 45) * 1000
            promoted_salary = base_salary
            promotion_month = 99
            base_emi = 0 if random.random() < 0.75 else random.randint(2000, 5000)
            initial_balance = random.randint(8000, 25000)

        elif arch == "STABLE_PROFESSIONAL":
            age = random.randint(28, 42)
            account_vintage = random.randint(18, 60)
            base_salary = random.randint(55, 110) * 1000
            promoted_salary = base_salary
            promotion_month = 99
            # DTI between 0.20 and 0.40
            base_emi = int(base_salary * random.uniform(0.20, 0.38))
            initial_balance = random.randint(40000, 150000)

        elif arch == "FAMILY_BUILDER":
            age = random.randint(32, 48)
            account_vintage = random.randint(24, 72)
            base_salary = random.randint(65, 140) * 1000
            promoted_salary = base_salary
            promotion_month = 99
            base_emi = int(base_salary * random.uniform(0.15, 0.35))
            initial_balance = random.randint(35000, 120000)

        elif arch == "HIGH_NETWORTH":
            age = random.randint(35, 58)
            account_vintage = random.randint(36, 120)
            base_salary = random.randint(180, 350) * 1000
            promoted_salary = base_salary
            promotion_month = 99
            base_emi = int(base_salary * random.uniform(0.05, 0.18))
            initial_balance = random.randint(250000, 800000)

        else:  # FINANCIALLY_STRESSED
            age = random.randint(26, 52)
            account_vintage = random.randint(12, 48)
            base_salary = random.randint(30, 65) * 1000
            promoted_salary = base_salary
            promotion_month = 99
            # DTI >= 0.48, high debt burden
            base_emi = int(base_salary * random.uniform(0.48, 0.65))
            initial_balance = random.randint(3000, 15000)

        customers.append({
            "customer_id": cust_id,
            "name": full_name,
            "age": age,
            "occupation": occupation,
            "city": city,
            "state": state,
            "account_vintage_months": account_vintage,
            "consent_tier": consent_tier,
            "archetype": arch,
            "base_salary": base_salary,
            "promoted_salary": promoted_salary,
            "promotion_month": promotion_month,
            "base_emi": base_emi,
            "initial_balance": initial_balance
        })

    return customers


def generate_transactions(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate 6 months (180 days) of realistic daily transactions for all 100 customers."""
    # 6 continuous months: from 2026-03-01 to 2026-08-31
    start_date = datetime.date(2026, 3, 1)
    end_date = datetime.date(2026, 8, 31)
    total_days = (end_date - start_date).days + 1

    all_txns = []
    txn_counter = 1

    for cust in customers:
        cust_id = cust["customer_id"]
        arch = cust["archetype"]
        current_balance = float(cust["initial_balance"])
        base_salary = cust["base_salary"]
        promoted_salary = cust["promoted_salary"]
        promo_month = cust["promotion_month"]
        base_emi = cust["base_emi"]

        # Rent payment determination: Family builder or young earner renting without home loan
        has_rent = arch in ["FAMILY_BUILDER", "YOUNG_EARNER"] or cust["customer_id"] == "CUST_IND_1015"
        monthly_rent = int(base_salary * random.uniform(0.20, 0.28)) if has_rent else 0

        # Simulation loop over 180 days
        for day_offset in range(total_days):
            curr_date = start_date + datetime.timedelta(days=day_offset)
            month_idx = (curr_date.year - start_date.year) * 12 + (curr_date.month - start_date.month) + 1

            # 1. Salary Credit (1st or 5th of each month)
            salary_day = 1 if cust_id != "CUST_IND_1002" else 5
            if curr_date.day == salary_day:
                salary_amt = promoted_salary if month_idx >= promo_month else base_salary
                # Stressed customer might experience delayed or slight variation
                current_balance += salary_amt
                all_txns.append({
                    "txn_id": f"TXN_{txn_counter:07d}",
                    "customer_id": cust_id,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "txn_type": "CREDIT",
                    "category": "SALARY",
                    "description": f"Salary Credit - {cust['occupation']}",
                    "amount": round(salary_amt, 2),
                    "balance_after": round(current_balance, 2)
                })
                txn_counter += 1

            # 2. Monthly Rent Outflow (3rd of month)
            if has_rent and curr_date.day == 3:
                current_balance -= monthly_rent
                all_txns.append({
                    "txn_id": f"TXN_{txn_counter:07d}",
                    "customer_id": cust_id,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "txn_type": "DEBIT",
                    "category": "RENT",
                    "description": "Monthly Rent UPI Transfer to Landlord",
                    "amount": round(monthly_rent, 2),
                    "balance_after": round(current_balance, 2)
                })
                txn_counter += 1

            # 3. Monthly EMI Outflow (5th or 10th of month)
            if base_emi > 0 and curr_date.day == 10:
                current_balance -= base_emi
                all_txns.append({
                    "txn_id": f"TXN_{txn_counter:07d}",
                    "customer_id": cust_id,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "txn_type": "DEBIT",
                    "category": "EMI",
                    "description": "Auto-Debit Recurring Loan EMI",
                    "amount": round(base_emi, 2),
                    "balance_after": round(current_balance, 2)
                })
                txn_counter += 1

            # 4. Recurring Utilities (12th of month)
            if curr_date.day == 12:
                util_amt = random.uniform(1200, 3500)
                current_balance -= util_amt
                all_txns.append({
                    "txn_id": f"TXN_{txn_counter:07d}",
                    "customer_id": cust_id,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "txn_type": "DEBIT",
                    "category": "ESSENTIALS",
                    "description": "Electricity & Broadband Bill Payment",
                    "amount": round(util_amt, 2),
                    "balance_after": round(current_balance, 2)
                })
                txn_counter += 1

            # 5. Education debits for Family Builders (Quarterly / Monthly in May/June/July)
            if arch == "FAMILY_BUILDER" and curr_date.day == 15 and curr_date.month in [4, 6]:
                edu_item, min_a, max_a = random.choice(SPEND_CATEGORIES["EDUCATION"])
                edu_amt = random.uniform(min_a, max_a)
                current_balance -= edu_amt
                all_txns.append({
                    "txn_id": f"TXN_{txn_counter:07d}",
                    "customer_id": cust_id,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "txn_type": "DEBIT",
                    "category": "EDUCATION",
                    "description": edu_item,
                    "amount": round(edu_amt, 2),
                    "balance_after": round(current_balance, 2)
                })
                txn_counter += 1

            # 6. Medical Expense Spikes (Crucial for Amit Patel & Stressed Earner Demo)
            if (cust_id == "CUST_IND_1088" or (arch == "FINANCIALLY_STRESSED" and random.random() < 0.15)) and month_idx >= 4:
                # Spike medical spends in months 4, 5, 6 by > 60%
                if curr_date.day in [8, 18, 26]:
                    med_item, min_a, max_a = random.choice(SPEND_CATEGORIES["MEDICAL"])
                    med_amt = random.uniform(min_a * 1.5, max_a * 1.2)
                    current_balance -= med_amt
                    all_txns.append({
                        "txn_id": f"TXN_{txn_counter:07d}",
                        "customer_id": cust_id,
                        "date": curr_date.strftime("%Y-%m-%d"),
                        "txn_type": "DEBIT",
                        "category": "MEDICAL",
                        "description": f"Urgent Medical: {med_item}",
                        "amount": round(med_amt, 2),
                        "balance_after": round(current_balance, 2)
                    })
                    txn_counter += 1

            # 7. Daily / Variable Spends (1 to 3 per day based on archetype)
            daily_txn_prob = {
                "YOUNG_EARNER": 0.85,
                "UPWARD_EARNER": 0.80,
                "STABLE_PROFESSIONAL": 0.70,
                "FAMILY_BUILDER": 0.75,
                "HIGH_NETWORTH": 0.90,
                "FINANCIALLY_STRESSED": 0.60,
                "VERNACULAR_USER": 0.50
            }.get(arch, 0.65)

            if random.random() < daily_txn_prob:
                num_spends = random.choice([1, 1, 2, 3] if arch == "HIGH_NETWORTH" else [1, 1, 2])
                for _ in range(num_spends):
                    # Category weightings based on archetype
                    if arch == "YOUNG_EARNER" or cust_id == "CUST_IND_1042":
                        cat_weights = [0.30, 0.45, 0.15, 0.05, 0.00, 0.05]
                    elif arch == "HIGH_NETWORTH":
                        cat_weights = [0.20, 0.25, 0.25, 0.05, 0.05, 0.20]
                    elif arch == "FINANCIALLY_STRESSED" or cust_id == "CUST_IND_1088":
                        # Stressed users shift spend towards essentials and away from discretionary
                        cat_weights = [0.65, 0.10, 0.05, 0.20, 0.00, 0.00]
                    else:
                        cat_weights = [0.45, 0.25, 0.15, 0.05, 0.05, 0.05]

                    chosen_cat = random.choices(
                        ["ESSENTIALS", "DISCRETIONARY", "TRAVEL", "MEDICAL", "EDUCATION", "LUXURY"],
                        weights=cat_weights,
                        k=1
                    )[0]

                    desc, min_amt, max_amt = random.choice(SPEND_CATEGORIES[chosen_cat])
                    spend_amt = random.uniform(min_amt, max_amt)

                    # Scale spend by income
                    spend_amt *= min(2.5, max(0.6, (base_salary / 60000) ** 0.5))
                    current_balance -= spend_amt

                    all_txns.append({
                        "txn_id": f"TXN_{txn_counter:07d}",
                        "customer_id": cust_id,
                        "date": curr_date.strftime("%Y-%m-%d"),
                        "txn_type": "DEBIT",
                        "category": chosen_cat,
                        "description": desc,
                        "amount": round(spend_amt, 2),
                        "balance_after": round(current_balance, 2)
                    })
                    txn_counter += 1

    return all_txns


def run():
    """Main generation pipeline saving customers, transactions, and customer_360_data."""
    print("[1/3] Generating 100 realistic customer profiles...")
    customers = generate_customers()
    cust_df = pd.DataFrame(customers)
    cust_path = os.path.join(DATA_DIR, "customers.csv")
    cust_df.to_csv(cust_path, index=False)
    print(f" -> Saved {len(cust_df)} customer profiles to {cust_path}")

    print("[2/3] Generating 6-month daily transaction streams...")
    txns = generate_transactions(customers)
    txns_df = pd.DataFrame(txns)
    txns_path = os.path.join(DATA_DIR, "transactions.csv")
    txns_df.to_csv(txns_path, index=False)
    print(f" -> Saved {len(txns_df)} transactions to {txns_path}")

    print("[3/3] Creating Customer 360 joined dataset...")
    # Aggregated customer metrics
    c360 = []
    for cust in customers:
        cid = cust["customer_id"]
        c_txns = txns_df[txns_df["customer_id"] == cid]
        debits = c_txns[c_txns["txn_type"] == "DEBIT"]
        credits = c_txns[c_txns["txn_type"] == "CREDIT"]
        salary_credits = c_txns[c_txns["category"] == "SALARY"]

        total_inflow = credits["amount"].sum()
        total_outflow = debits["amount"].sum()
        mean_balance = c_txns["balance_after"].mean()
        min_balance = c_txns["balance_after"].min()
        latest_balance = c_txns.iloc[-1]["balance_after"] if len(c_txns) > 0 else 0

        c360.append({
            "customer_id": cid,
            "name": cust["name"],
            "age": cust["age"],
            "occupation": cust["occupation"],
            "city": cust["city"],
            "state": cust["state"],
            "account_vintage_months": cust["account_vintage_months"],
            "consent_tier": cust["consent_tier"],
            "archetype": cust["archetype"],
            "monthly_salary": cust["promoted_salary"] if cust["promotion_month"] <= 6 else cust["base_salary"],
            "total_6m_inflow": round(total_inflow, 2),
            "total_6m_outflow": round(total_outflow, 2),
            "mean_balance": round(mean_balance, 2),
            "min_balance": round(min_balance, 2),
            "latest_balance": round(latest_balance, 2),
            "total_txns_count": len(c_txns)
        })

    c360_df = pd.DataFrame(c360)
    c360_path = os.path.join(DATA_DIR, "customer_360_data.csv")
    c360_df.to_csv(c360_path, index=False)
    print(f" -> Saved Customer 360 data to {c360_path}")
    print("[OK] Synthetic Data Generation Complete!")


if __name__ == "__main__":
    run()
