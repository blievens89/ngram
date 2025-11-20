"""
Minimal test app to verify example data loading works
Run with: streamlit run test_example_data.py
"""

import streamlit as st
import sys
sys.path.insert(0, '/home/user/ngram')

from data.loader import load_example_data

st.title("Example Data Test")

# Initialize session state
if 'example_data_loaded' not in st.session_state:
    st.session_state.example_data_loaded = False

st.write(f"Session state: {st.session_state.example_data_loaded}")

# Method selection
method = st.radio("Choose method:", ["Button Method", "Direct Load"])

if method == "Button Method":
    st.markdown("### Button Method (same as sidebar)")

    if not st.session_state.example_data_loaded:
        if st.button("Load Example Data"):
            st.session_state.example_data_loaded = True
            st.rerun()
    else:
        df = load_example_data()

        if df is not None and not df.empty:
            st.success(f"✅ Loaded {len(df)} rows")
            st.dataframe(df.head())

            if st.button("Reset"):
                st.session_state.example_data_loaded = False
                st.rerun()
        else:
            st.error("Failed to load")

else:
    st.markdown("### Direct Load Method")
    if st.button("Load Now"):
        df = load_example_data()
        if df is not None and not df.empty:
            st.success(f"✅ Loaded {len(df)} rows")
            st.dataframe(df.head())
        else:
            st.error("Failed to load")
