import argparse
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from src.etl import run_pipeline
from src.db import init_db
from src.agent import get_agent
from src.eda import generate_eda_report
from src.utils import setup_logging
from dotenv import load_dotenv

# Load env vars
load_dotenv()
logger = setup_logging()

def main():
    parser = argparse.ArgumentParser(description="HR Data Pipeline & SQL Agent")
    parser.add_argument("--input", default="data/raw/employees.csv", help="Path to raw CSV file")
    parser.add_argument("--output", default="data/processed/cleaned_employees.csv", help="Path to output cleaned CSV")
    parser.add_argument("--eda-dir", default="data/eda_output", help="Directory for EDA charts")
    parser.add_argument("--query", help="Question to ask the AI Agent")
    parser.add_argument("--interactive", action="store_true", help="Run agent in interactive mode")
    
    args = parser.parse_args()
    
    # 1. Run ETL Pipeline
    try:
        logger.info("=== Phase 1: Data Engineering ===")
        df_clean = run_pipeline(args.input, args.output)
        
        # 2. Generate EDA
        logger.info("=== Phase 2: Exploratory Data Analysis ===")
        generate_eda_report(df_clean, args.eda_dir)
        
        # 3. AI Agent
        logger.info("=== Phase 3: AI Agent Initialization ===")
        db = init_db(df_clean)
        agent = get_agent(db)
        
        if args.query:
            logger.info(f"Executing Query: {args.query}")
            response = agent.invoke(args.query)
            print(f"\nAnswer: {response['output']}\n")
        
        elif args.interactive:
            print("\n--- Interactive HR Agent (Type 'exit' to quit) ---")
            while True:
                q = input("Query: ")
                if q.lower() in ["exit", "quit"]:
                    break
                try:
                    response = agent.invoke(q)
                    print(f"Answer: {response['output']}\n")
                except Exception as e:
                    logger.error(f"Agent Error: {e}")
        
        else:
            logger.info("No query provided. Pipeline finished successfully.")
            
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
