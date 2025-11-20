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
    import os

    # Try multiple possible paths
    possible_paths = [
        'example_data.csv',
        os.path.join(os.path.dirname(__file__), '..', 'example_data.csv'),
        '/home/user/ngram/example_data.csv'
    ]

    for path in possible_paths:
        try:
            logger.info(f"Trying to load example data from: {path}")
            df = pd.read_csv(path)
            logger.info(f"✅ Loaded {len(df)} rows from {path}")
            return df
        except FileNotFoundError:
            continue
        except Exception as e:
            logger.error(f"Error loading from {path}: {e}")
            continue

    # If we get here, none of the paths worked
    logger.error("Could not find example_data.csv in any location")
    st.error("❌ Could not find example_data.csv - please ensure it exists in the project directory")
    return pd.DataFrame()
