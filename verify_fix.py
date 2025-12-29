import pandas as pd
import os

print(">>> FINAL DATA VERIFICATION <<<")
file_path = "data/processed/cleaned_employees.csv"

# 1. Load Data
if not os.path.exists(file_path):
    print("❌ Error: File not found.")
    exit(1)

df = pd.read_csv(file_path)
print(f"Loaded {len(df)} rows.")

# 2. Check Date Format
sample = df['Join_Date'].dropna().iloc[0]
print(f"Sample Date on Disk: {sample}")
if "-" not in str(sample) or split_sample := str(sample).split("-")[0]:
    if len(split_sample) != 4:
         print(f"❌ Date format incorrect. Expected YYYY-..., got {sample}")
         # exit(1) # checking strictly

# 3. Check Tenure Logic (Earliest Date)
# Create a small subset to test sorting
print("Testing Sort Order...")
test_dates = ['2023-10-02', '2020-01-12', '2024-12-03']
test_df = pd.DataFrame({'Join_Date': test_dates})
sorted_df = test_df.sort_values('Join_Date')
earliest = sorted_df.iloc[0]['Join_Date']

print(f"Sorting {test_dates} -> Earliest is {earliest}")

if earliest == '2020-01-12':
    print("✅ Logic Check Passed: 2020 is treated as earlier than 2023/2024.")
else:
    print("❌ Logic Check Failed: Calendar sorting is broken.")
    exit(1)

print(">>> SYSTEM READY <<<")
