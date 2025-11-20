"""
Custom CSS styling for the application
"""

import streamlit as st
from config import BrandColors


def apply_custom_styles():
    """Apply Platform81 custom styling to the Streamlit app"""

    colors = BrandColors()

    st.markdown(f"""
    <style>
        .main {{
            background: linear-gradient(135deg, {colors.NIGHT} 0%, {colors.NIGHT_LIGHT} 100%);
        }}

        .stApp {{
            background: linear-gradient(135deg, {colors.NIGHT} 0%, {colors.NIGHT_LIGHT} 100%);
        }}

        h1 {{
            color: {colors.EMERALD} !important;
            font-size: 3rem !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
            text-shadow: 0 0 20px rgba(71, 212, 149, 0.3);
        }}

        .subtitle {{
            text-align: center;
            color: {colors.POWDER_BLUE};
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: linear-gradient(145deg, {colors.NIGHT_LIGHT}, {colors.NIGHT_LIGHTER});
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid {colors.EMERALD};
            box-shadow: 0 4px 20px rgba(71, 212, 149, 0.1);
            margin: 1rem 0;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: {colors.NIGHT_LIGHT};
            padding: 0.5rem;
            border-radius: 10px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: {colors.NIGHT_LIGHTER};
            color: {colors.POWDER_BLUE};
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(45deg, {colors.EMERALD}, {colors.SLATE_BLUE}) !important;
            color: white !important;
        }}

        .stButton > button {{
            background: linear-gradient(45deg, {colors.EMERALD}, {colors.SLATE_BLUE}) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.7rem 1.5rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(71, 212, 149, 0.3) !important;
        }}

        .stButton > button:hover {{
            box-shadow: 0 6px 25px rgba(71, 212, 149, 0.5) !important;
            transform: translateY(-2px);
        }}

        .dataframe {{
            background-color: {colors.NIGHT_LIGHT} !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {colors.EMERALD} !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {colors.POWDER_BLUE} !important;
        }}

        .warning-box {{
            background-color: {colors.BURNT_SIENNA};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 600;
        }}

        .info-box {{
            background-color: {colors.SLATE_BLUE};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }}

        .success-box {{
            background-color: {colors.EMERALD};
            color: {colors.NIGHT};
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 600;
        }}
    </style>
    """, unsafe_allow_html=True)
