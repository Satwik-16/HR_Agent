import os
import pandas as pd
from src.utils import setup_logging, format_phone_number, clean_salary, check_schema

logger = setup_logging()

def run_pipeline(input_path: str, output_path: str):
    """
    Executes the ETL pipeline:
    1. Load Data
    2. Validate Schema
    3. Clean & Transform
    4. Save Data
    """
    logger.info(f"Starting ETL pipeline. Input: {input_path}")
    
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file {input_path} does not exist.")
    
    try:
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} rows.")
        
        # 1. Schema Validation (Strict Mode)
        required_columns = [
            'Email', 'Phone', 'Department_Region', 'Salary', 
            'Join_Date', 'First_Name', 'Last_Name', 'Performance_Score'
        ]
        check_schema(df, required_columns)
        
        # 2. Deduplication
        initial_count = len(df)
        # Normalize email for deduplication
        df['email_norm'] = df['Email'].astype(str).str.lower().str.strip()
        df = df.drop_duplicates(subset=['email_norm'], keep='first')
        df = df.drop(columns=['email_norm'])
        logger.info(f"Dropped {initial_count - len(df)} duplicate rows. New count: {len(df)}")
        
        # 3. Data Cleaning
        # Standardize formats to ensure consistent downstream analysis
        logger.info("Cleaning Phone numbers and Salaries...")
        df['Phone'] = df['Phone'].apply(format_phone_number)
        df['Salary'] = df['Salary'].apply(clean_salary).astype('Int64')
        
        # 4. Feature Engineering & Standardization
        logger.info("Splitting Department_Region and Standardizing Dates...")
        
        # Split 'Department_Region' (e.g., "Sales-US") into separate columns for granular aggregations
        split_data = df['Department_Region'].astype(str).str.split('-', n=1, expand=True)
        df['Department'] = split_data[0].str.strip()
        if split_data.shape[1] > 1:
            df['Region'] = split_data[1].str.strip()
        else:
            df['Region'] = pd.NA
            
        # CRITICAL: Standardization of Date Format
        # Convert all dates to ISO 8601 (YYYY-MM-DD) to ensure correct chronological sorting in SQL.
        # Without this, '10/01/2023' (String) would sort before '02/01/2020' (String).
        if 'Join_Date' in df.columns:
            df['Join_Date'] = pd.to_datetime(df['Join_Date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
        # Remove redundant composite column after splitting
        df = df.drop(columns=['Department_Region'])
        
        # 5. Serialization
        # Save processed data to a stable location for the Agent/DB loader
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Pipeline finished. Cleaned data saved to {output_path}")
        return df

    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        raise e

if __name__ == "__main__":
    # Default paths for standalone testing
    INPUT_FILE = "data/raw/employees.csv"
    OUTPUT_FILE = "data/processed/cleaned_employees.csv"
    run_pipeline(INPUT_FILE, OUTPUT_FILE)
