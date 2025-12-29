from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def init_db(df: pd.DataFrame):
    """
    Initializes a SQLite database from the provided DataFrame.
    Persists data to disk to allow access across Streamlit threads.
    """
    try:
        db_path = "data/processed/hr.db"
        engine = create_engine(f"sqlite:///{db_path}") 
        
        # Persist DataFrame to 'employees' table
        df.to_sql("employees", engine, index=False, if_exists='replace')
        
        logger.info("Database initialized with 'employees' table.")
        
        return SQLDatabase(engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
