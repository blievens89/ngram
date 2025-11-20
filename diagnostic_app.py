"""
DIAGNOSTIC VERSION - Shows exactly what's happening
Run: streamlit run diagnostic_app.py
"""
import streamlit as st
import pandas as pd
import os
import sys

st.title("🔍 Example Data Diagnostic")

# Show environment info
st.markdown("## Environment Info")
st.write(f"**Current working directory:** `{os.getcwd()}`")
st.write(f"**Python path:** `{sys.executable}`")
st.write(f"**This file location:** `{__file__}`")

# Check if example_data.csv exists
st.markdown("## File Check")
possible_paths = [
    'example_data.csv',
    os.path.join(os.getcwd(), 'example_data.csv'),
    '/home/user/ngram/example_data.csv',
    os.path.join(os.path.dirname(__file__), 'example_data.csv')
]

for path in possible_paths:
    exists = os.path.exists(path)
    abs_path = os.path.abspath(path) if exists else "N/A"
    st.write(f"- `{path}`: {'✅ EXISTS' if exists else '❌ NOT FOUND'} (abs: `{abs_path}`)")

# Try to load the file
st.markdown("## Load Test")
for path in possible_paths:
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            st.success(f"✅ Successfully loaded from `{path}`")
            st.write(f"Shape: {df.shape}")
            st.write(f"Columns: {list(df.columns)}")
            st.dataframe(df.head(3))
            break
        except Exception as e:
            st.error(f"❌ Error loading from `{path}`: {e}")
else:
    st.error("❌ Could not load from any path")

# Test session state
st.markdown("## Session State Test")
if 'test_loaded' not in st.session_state:
    st.session_state.test_loaded = False

st.write(f"Session state: `test_loaded = {st.session_state.test_loaded}`")

if not st.session_state.test_loaded:
    if st.button("Set to True"):
        st.session_state.test_loaded = True
        st.rerun()
else:
    st.success("✅ Session state is True")
    if st.button("Reset to False"):
        st.session_state.test_loaded = False
        st.rerun()
