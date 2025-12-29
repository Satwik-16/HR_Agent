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
        df.to_sql("employees", engine, if_exists="replace", index=False)
        
        # Create Logs Table (for Training Data)
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_query TEXT,
                    agent_response TEXT,
                    verification_status TEXT
                )
            """))
            connection.commit()
        
        logger.info(f"Database initialized with {len(df)} employee records and Logging Table.")
        
        return SQLDatabase(engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e

def log_interaction(db: SQLDatabase, user_query: str, agent_response: str, status: str):
    """
    Persists the interaction to the database for future fine-tuning/training.
    """
    try:
        # We need to access the underlying sqlalchemy engine/connection
        # SQLDatabase wrapper is read-only for the agent, but we can write via the engine
        with db._engine.connect() as connection:
            from sqlalchemy import text
            stmt = text("""
                INSERT INTO query_logs (user_query, agent_response, verification_status)
                VALUES (:q, :a, :s)
            """)
            connection.execute(stmt, {"q": user_query, "a": agent_response, "s": status})
            connection.commit()
    except Exception as e:
        logger.error(f"Failed to log interaction: {e}")
