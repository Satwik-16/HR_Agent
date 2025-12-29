import os
import logging
from typing import Optional
from langchain_google_vertexai import ChatVertexAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase

logger = logging.getLogger(__name__)

def _get_llm() -> ChatVertexAI:
    """
    Internal factory for the Vertex AI LLM instance.
    Centralizes configuration and error handling.
    """
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location = os.getenv("GOOGLE_LOCATION", "us-central1")
    model_name = os.getenv("VERTEX_MODEL_NAME", "gemini-2.5-flash")

    if not project_id:
        raise ValueError("GOOGLE_PROJECT_ID not set in environment variables.")

    try:
        return ChatVertexAI(
            model_name=model_name,
            project=project_id,
            location=location,
            temperature=0
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        if "404" in str(e):
             raise ValueError(f"Model '{model_name}' not found. Check permissions or model name.")
        raise e

def get_agent(db: SQLDatabase):
    """
    Constructs the SQL Agent Executor.
    """
    logger.info("Initializing SQL Agent...")
    llm = _get_llm()

    # Inject date context and business constraints into the LLM system prompt
    from datetime import date
    today_str = date.today().strftime("%Y-%m-%d")
    
    custom_suffix = f"""
    CRITICAL INSTRUCTIONS:
    1. **Format**: If the user asks for a list/table, YOU MUST return a Markdown Table.
    2. **Ties**: If asking for "highest" or "top" and there are ties, output ALL tied items.
    3. **Dates**: Sanity check dates. Ignore future dates for tenure. 'Current Date' is {today_str}.
    4. **Data Integrity**: If a field is NULL or invalid, exclude it or treat as 0, but note it.
    5. **Out of Scope**: If asked about data not in the schema (e.g. 'office location'), state it is not available.
    
    Structure your answer as:
    | Col1 | Col2 | ... |
    |---|---|---|
    | Val1 | Val2 | ... |
    """

    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        handle_parsing_errors=True,
        suffix=custom_suffix
    )

def validate_response(user_query: str, agent_response: str) -> str:
    """
    Evaluates the agent's response for correctness and relevance using a critical prompt.
    Reuses the standard LLM configuration.
    """
    try:
        validator_llm = _get_llm()
        
        validation_prompt = f"""
        Role: Senior QA Auditor.
        Task: Verify the SQL Agent's response.
        
        Context: The Agent has access to an Employee HR Database. 
        It CANNOT answer questions about things not in the DB (e.g. PTO, Office Hierarchy, Benefits).
        
        user_query: "{user_query}"
        agent_response: "{agent_response}"
        
        **Verification Rules:**
        1. **Refusals**: If the user asks about missing data (managers, PTO) and the agent says "Not available" or "I don't know", this is **VERIFIED_CORRECT**. Do not flag it.
        2. **Formatting**: Tables are required for list/report questions.
        3. **Logic**: Check for obvious contradictions (e.g. "Highest salary is 0").
        
        **Output:** 
        - Return "VERIFIED_CORRECT" if the answer is reasonable OR a valid refusal.
        - Otherwise, explain specific error.
        """
        
        result = validator_llm.invoke(validation_prompt).content
        return result.strip()
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return "VERIFICATION_ERROR"
