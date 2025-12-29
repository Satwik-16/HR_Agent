import logging
import re
import pandas as pd
import sys

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def setup_logging():
    """Returns the configured logger instance."""
    return logger

def format_phone_number(raw_phone):
    """
    Standardizes phone numbers to (XXX) XXX-XXXX format.
    Returns None if the input does not contain exactly 10 digits.
    """
    if pd.isna(raw_phone):
        return None
    
    digits = re.sub(r'\D', '', str(raw_phone))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    return None

def clean_salary(raw_salary):
    """
    Converts salary input to integer, handling string formatting and NaN values.
    Returns pd.NA for invalid inputs.
    """
    try:
        val = pd.to_numeric(raw_salary, errors='coerce')
        if pd.isna(val):
            return pd.NA
        return int(round(val))
    except (ValueError, TypeError):
        return pd.NA

def check_schema(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Verifies that the DataFrame contains all required columns.
    Raises ValueError if validation fails.
    """
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return True
