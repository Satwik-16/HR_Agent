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
        
        # 1. Schema Validation
        required_columns = ['Email', 'Phone', 'Department_Region', 'Salary']
        check_schema(df, required_columns)
        
        # 2. Deduplication
        initial_count = len(df)
        # Normalize email for deduplication
        df['email_norm'] = df['Email'].astype(str).str.lower().str.strip()
        df = df.drop_duplicates(subset=['email_norm'], keep='first')
        df = df.drop(columns=['email_norm'])
        logger.info(f"Dropped {initial_count - len(df)} duplicate rows. New count: {len(df)}")
        
        # 3. Data Cleaning
        logger.info("Cleaning Phone numbers and Salaries...")
        df['Phone'] = df['Phone'].apply(format_phone_number)
        df['Salary'] = df['Salary'].apply(clean_salary).astype('Int64')
        
        # 4. Transformations (Department_Region Split)
        logger.info("Splitting Department_Region...")
        split_data = df['Department_Region'].astype(str).str.split('-', n=1, expand=True)
        df['Department'] = split_data[0].str.strip()
        if split_data.shape[1] > 1:
            df['Region'] = split_data[1].str.strip()
        else:
            df['Region'] = pd.NA
            
        # Drop original column if desired, or keep it. Review said "Remove the old column"
        df = df.drop(columns=['Department_Region'])
        
        # 5. Save Output
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
