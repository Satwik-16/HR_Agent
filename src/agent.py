import os
from langchain_google_vertexai import ChatVertexAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
import logging

logger = logging.getLogger(__name__)

def get_agent(db: SQLDatabase):
    """
    Initializes a secure SQL Agent using Google Vertex AI.
    The agent is restricted to SQL operations on the provided database.
    """
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location = os.getenv("GOOGLE_LOCATION", "us-central1")
    
    if not project_id:
        raise ValueError("GOOGLE_PROJECT_ID not set in environment variables.")

    try:
        # Load Model Configuration
        model_name = os.getenv("VERTEX_MODEL_NAME", "gemini-2.5-flash")
        
        logger.info(f"Initializing Vertex AI Agent with model: {model_name}")

        llm = ChatVertexAI(
            model_name=model_name,
            project=project_id,
            location=location,
            temperature=0
        )

        # Enforce Markdown table formatting for all list/report outputs
        custom_suffix = """
        If the user asks for a list, report or table, YOU MUST return the final answer as a Markdown Table.
        Do not just list names in a sentence. 
        Format:
        | Column 1 | Column 2 | ... |
        |---|---|---|
        | Val 1 | Val 2 | ... |
        
        Ensure you include all relevant columns requested.
        """

        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            verbose=True,
            handle_parsing_errors=True,
            suffix=custom_suffix
        )
        
        logger.info("SQL Agent initialized successfully.")
        return agent_executor
        
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        if "404" in str(e):
             raise ValueError(f"Model '{model_name}' not found or Vertex AI API not enabled in project {project_id}.")
        raise e
