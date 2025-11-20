"""
Sidebar UI components
"""

import streamlit as st
from typing import Tuple, Optional, Set
import pandas as pd

from config import DEFAULT_STOP_WORDS, AnalysisDefaults
from data import load_data_from_paste, load_data_from_file, load_example_data


def render_sidebar() -> Tuple[Optional[pd.DataFrame], dict]:
    """
    Render the sidebar with data input and settings

    Returns:
        Tuple of (DataFrame, settings_dict)
        - DataFrame: Loaded data (None if no data loaded)
        - settings_dict: Dictionary of analysis settings
    """
    defaults = AnalysisDefaults()

    with st.sidebar:
        st.markdown("## 📊 Data Input")

        # Data input instructions
        st.markdown("""
        <div class="info-box">
        <strong>Required Columns:</strong><br>
        • Search term (or keyword/query)<br>
        • Clicks<br>
        • Cost<br>
        • Conversions (or conv.)<br>
        <br>
        <strong>Optional:</strong><br>
        • Impressions (or impr.)<br>
        <br>
        <em>All other columns will be ignored.<br>
        Perfect for Google Ads exports!</em>
        </div>
        """, unsafe_allow_html=True)

        # Input method selection
        input_method = st.radio(
            "Input Method",
            ["Paste Data", "Upload File", "Use Example Data"]
        )

        df_input = None

        if input_method == "Paste Data":
            pasted_data = st.text_area(
                "Paste your CSV data here",
                height=200,
                placeholder="query,clicks,cost,conversions\nremortgage rates,150,245.50,12\ncheap remortgage,89,156.20,7"
            )
            if pasted_data:
                df_input = load_data_from_paste(pasted_data)

        elif input_method == "Upload File":
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
            if uploaded_file:
                df_input = load_data_from_file(uploaded_file)

        elif input_method == "Use Example Data":
            # Initialize session state
            if 'example_data_loaded' not in st.session_state:
                st.session_state.example_data_loaded = False

            # Show button to load data
            if not st.session_state.example_data_loaded:
                if st.button("📥 Load Example Data", use_container_width=True, type="primary"):
                    st.session_state.example_data_loaded = True
                    st.rerun()  # Force rerun to load data
            else:
                # Data is loaded, show it
                df_input = load_example_data()

                if df_input is not None and not df_input.empty:
                    st.success(f"✅ Example data loaded: {len(df_input)} queries")

                    with st.expander("👀 Preview data", expanded=True):
                        st.dataframe(df_input.head(5), use_container_width=True)

                    # Reset button
                    if st.button("🔄 Clear & Load Different Data", use_container_width=True):
                        st.session_state.example_data_loaded = False
                        st.rerun()
                else:
                    st.error("❌ Could not load example_data.csv")
                    if st.button("Try Again"):
                        st.session_state.example_data_loaded = False
                        st.rerun()

        # Analysis Settings
        st.markdown("---")
        st.markdown("## ⚙️ Analysis Settings")

        ngram_sizes = st.multiselect(
            "N-gram sizes to analyse",
            options=[1, 2, 3, 4],
            default=defaults.NGRAM_SIZES
        )

        min_occurrences = st.slider(
            "Minimum query occurrences",
            min_value=1,
            max_value=10,
            value=defaults.MIN_OCCURRENCES,
            help="N-grams must appear in at least this many queries"
        )

        sort_metric = st.selectbox(
            "Sort results by",
            options=['total_cost', 'total_clicks', 'total_conversions', 'cpa', 'cvr', 'ctr'],
            format_func=lambda x: x.replace('_', ' ').title(),
            index=0  # default to total_cost
        )

        sort_ascending = st.checkbox("Sort ascending", value=defaults.SORT_ASCENDING)

        # Stop Words
        st.markdown("---")
        st.markdown("## 🚫 Stop Words")

        use_stop_words = st.checkbox("Exclude stop words", value=True)

        stop_words = None
        if use_stop_words:
            custom_stop_words = st.text_area(
                "Custom stop words (one per line)",
                value='\n'.join(sorted(DEFAULT_STOP_WORDS)),
                height=150
            )
            stop_words = set(custom_stop_words.lower().split())

        # Money Waster Detection
        st.markdown("---")
        st.markdown("## 🎯 Money Waster Detection")

        enable_money_waster = st.checkbox("Enable money waster analysis", value=True)

        cost_percentile = defaults.COST_PERCENTILE
        cvr_percentile = defaults.CVR_PERCENTILE

        if enable_money_waster:
            cost_percentile = st.slider(
                "High cost threshold (percentile)",
                min_value=50,
                max_value=95,
                value=defaults.COST_PERCENTILE,
                help="N-grams above this cost percentile are flagged"
            )

            cvr_percentile = st.slider(
                "Low CVR threshold (percentile)",
                min_value=5,
                max_value=50,
                value=defaults.CVR_PERCENTILE,
                help="N-grams below this CVR percentile are flagged"
            )

        # Advanced Filters
        st.markdown("---")
        st.markdown("## 🔍 Advanced Filters")

        col1, col2 = st.columns(2)
        with col1:
            min_cost = st.number_input("Min cost (£)", value=0.0, min_value=0.0)
            min_clicks = st.number_input("Min clicks", value=0, min_value=0)
        with col2:
            max_cpa = st.number_input("Max CPA (£, 0=no limit)", value=0.0, min_value=0.0)
            min_cvr = st.number_input("Min CVR %", value=0.0, min_value=0.0, max_value=100.0)

    # Compile settings dictionary
    settings = {
        'ngram_sizes': ngram_sizes,
        'min_occurrences': min_occurrences,
        'sort_metric': sort_metric,
        'sort_ascending': sort_ascending,
        'stop_words': stop_words,
        'enable_money_waster': enable_money_waster,
        'cost_percentile': cost_percentile,
        'cvr_percentile': cvr_percentile,
        'filters': {
            'min_cost': min_cost,
            'min_clicks': min_clicks,
            'max_cpa': max_cpa,
            'min_cvr': min_cvr
        }
    }

    return df_input, settings
