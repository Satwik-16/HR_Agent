import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

logger = logging.getLogger(__name__)

def generate_eda_report(df: pd.DataFrame, output_dir: str):
    """
    Generates EDA charts and statistics as per requirements.
    Saves outputs to output_dir.
    """
    logger.info("Generating EDA Report...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    sns.set_theme(style="whitegrid")
    
    # 1. Descriptive Statistics
    desc_stats = df.describe()
    stats_path = os.path.join(output_dir, "descriptive_statistics.csv")
    desc_stats.to_csv(stats_path)
    logger.info(f"Saved descriptive statistics to {stats_path}")

    # 2. Total Salary per Department
    plt.figure(figsize=(10, 6))
    salary_by_dept = df.groupby('Department')['Salary'].sum().sort_values(ascending=False)
    sns.barplot(x=salary_by_dept.values, y=salary_by_dept.index, palette="viridis")
    plt.title('Total Salary per Department')
    plt.xlabel('Total Salary ($)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "salary_by_department.png"))
    plt.close()
    
    # 3. Distribution of Performance by Department
    plt.figure(figsize=(12, 8))
    # Check if column exists, handle case sensitivity or missing col
    if 'Performance_Score' in df.columns:
        sns.countplot(data=df, x='Department', hue='Performance_Score', palette="Set2")
        plt.title('Performance Score Distribution by Department')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "performance_by_department.png"))
    else:
        logger.warning("Column 'Performance_Score' not found. Skipping chart.")
    plt.close()

    # 4. Distribution of Employees by Region
    plt.figure(figsize=(10, 6))
    if 'Region' in df.columns:
        region_counts = df['Region'].value_counts()
        sns.barplot(x=region_counts.values, y=region_counts.index, palette="mako")
        plt.title('Employee Distribution by Region')
        plt.xlabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "employees_by_region.png"))
    else:
         logger.warning("Column 'Region' not found. Skipping chart.")
    plt.close()
    
    logger.info(f"EDA charts saved to {output_dir}")
