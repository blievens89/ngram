"""
Data loading utilities
"""

import pandas as pd
import io
import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def load_data_from_paste(pasted_data: str) -> Optional[pd.DataFrame]:
    """
    Load DataFrame from pasted CSV text

    Args:
        pasted_data: Raw CSV text pasted by user

    Returns:
        DataFrame if successful, None if error
    """
    if not pasted_data or not pasted_data.strip():
        return None

    try:
        logger.info("Loading data from pasted text")
        df = pd.read_csv(io.StringIO(pasted_data))
        logger.info(f"Successfully loaded {len(df)} rows from pasted data")
        return df
    except Exception as e:
        error_msg = f"Error parsing pasted data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return None


def load_data_from_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Load DataFrame from uploaded CSV file

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        DataFrame if successful, None if error
    """
    if uploaded_file is None:
        return None

    try:
        logger.info(f"Loading data from file: {uploaded_file.name}")
        df = pd.read_csv(uploaded_file)
        logger.info(f"Successfully loaded {len(df)} rows from {uploaded_file.name}")
        return df
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return None


def load_example_data() -> pd.DataFrame:
    """
    Load example data for demonstration

    Returns:
        DataFrame with example query data
    """
    try:
        logger.info("Loading example data")
        df = pd.read_csv('example_data.csv')
        logger.info(f"Loaded {len(df)} rows from example data")
        return df
    except FileNotFoundError:
        logger.warning("Example data file not found")
        st.warning("Example data file not found")
        return pd.DataFrame()
