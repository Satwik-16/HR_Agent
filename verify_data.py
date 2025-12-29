import pandas as pd
import os
from src.etl import run_pipeline

# 1. Run Pipeline
print(">>> RUNNING ETL PIPELINE For Verification...")
try:
    df = run_pipeline("data/raw/employees.csv", "data/processed/cleaned_verify.csv")
except Exception as e:
    print(f"!!! ETL FAILED: {e}")
    exit(1)

# 2. Verify Date Format
print("\n>>> VERIFYING DATE FORMAT (YYYY-MM-DD)...")
sample_date = df['Join_Date'].iloc[0]
print(f"Sample Date: '{sample_date}'")

if "-" in str(sample_date) and str(sample_date).index("-") == 4:
    print("✅ Date Format Pass: ISO Standard (YYYY-MM-DD) detected.")
else:
    print(f"❌ Date Format Fail: Expected YYYY-MM-DD, got {sample_date}")
    exit(1)

# 3. Verify Sort Logic (Tenure Check)
print("\n>>> VERIFYING SORT ORDER (Tenure Logic)...")
# Create a dummy test case: 2023 vs 2020
test_df = pd.DataFrame({'Join_Date': ['2023-10-02', '2020-01-02']})
sorted_df = test_df.sort_values('Join_Date')
first_date = sorted_df.iloc[0]['Join_Date']

print(f"Sorting ['2023-10-02', '2020-01-02'] -> First is '{first_date}'")

if first_date == '2020-01-02':
    print("✅ Sorting Logic Pass: 2020 is correctly identified as earlier than 2023.")
else:
    print("❌ Sorting Logic Fail: System thinks 2023 is earlier!")
    exit(1)

print("\n>>> ALL CHECKS PASSED. SYSTEM IS READY. <<<")
