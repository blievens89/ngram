import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import defaultdict
import io

# Page config
st.set_page_config(
    page_title="N-Gram Query Analyser",
    page_icon="🔍",
    layout="wide"
)

# Platform81 Brand Styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
    }
    
    h1 {
        color: #47d495 !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 20px rgba(71, 212, 149, 0.3);
    }
    
    .subtitle {
        text-align: center;
        color: #98c1d9;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #222222);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #47d495;
        box-shadow: 0 4px 20px rgba(71, 212, 149, 0.1);
        margin: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1a1a;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #222222;
        color: #98c1d9;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #47d495, #6f58c9) !important;
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #47d495, #6f58c9) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(71, 212, 149, 0.3) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 25px rgba(71, 212, 149, 0.5) !important;
        transform: translateY(-2px);
    }
    
    .dataframe {
        background-color: #1a1a1a !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #47d495 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #98c1d9 !important;
    }
    
    .warning-box {
        background-color: #ee6c4d;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .info-box {
        background-color: #6f58c9;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# Header
st.markdown('<h1>🔍 N-Gram Query Analyser</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover high-impact keyword patterns in your search query data</p>', unsafe_allow_html=True)

# Default stop words
DEFAULT_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 
    'with', 'www', 'com', 'co', 'uk', 'org', 'net'
}

def clean_query(query, stop_words=None):
    """Clean and prepare query for n-gram extraction"""
    # Convert to lowercase and remove special characters
    cleaned = re.sub(r'[^\w\s]', ' ', str(query).lower())
    # Split into words
    words = cleaned.split()
    # Remove stop words if provided
    if stop_words:
        words = [w for w in words if w not in stop_words]
    return words

def extract_ngrams(query, n, stop_words=None):
    """Extract n-grams from a query"""
    words = clean_query(query, stop_words)
    if len(words) < n:
        return []
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

def analyze_ngrams(df, n, min_occurrences=2, stop_words=None):
    """Aggregate metrics for n-grams"""
    ngram_data = defaultdict(lambda: {
        'clicks': 0,
        'cost': 0,
        'conversions': 0,
        'impressions': 0,
        'query_count': 0,
        'queries': []
    })
    
    for _, row in df.iterrows():
        ngrams = extract_ngrams(row['query'], n, stop_words)
        for ngram in ngrams:
            ngram_data[ngram]['clicks'] += row['clicks']
            ngram_data[ngram]['cost'] += row['cost']
            ngram_data[ngram]['conversions'] += row['conversions']
            ngram_data[ngram]['impressions'] += row.get('impressions', row['clicks'])
            ngram_data[ngram]['query_count'] += 1
            ngram_data[ngram]['queries'].append(row['query'])
    
    # Convert to DataFrame
    result = []
    for ngram, data in ngram_data.items():
        if data['query_count'] >= min_occurrences:
            ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
            cvr = (data['conversions'] / data['clicks'] * 100) if data['clicks'] > 0 else 0
            cpa = (data['cost'] / data['conversions']) if data['conversions'] > 0 else 0
            
            result.append({
                'ngram': ngram,
                'query_count': data['query_count'],
                'total_clicks': data['clicks'],
                'total_cost': data['cost'],
                'total_conversions': data['conversions'],
                'total_impressions': data['impressions'],
                'ctr': ctr,
                'cvr': cvr,
                'cpa': cpa,
                'queries': data['queries']
            })
    
    return pd.DataFrame(result)

def identify_money_wasters(df, cost_threshold_percentile=75, cvr_threshold_percentile=25):
    """Identify high-cost, low-conversion n-grams"""
    if df.empty:
        return df
    
    cost_threshold = df['total_cost'].quantile(cost_threshold_percentile / 100)
    cvr_threshold = df['cvr'].quantile(cvr_threshold_percentile / 100)
    
    money_wasters = df[
        (df['total_cost'] >= cost_threshold) & 
        (df['cvr'] <= cvr_threshold)
    ].copy()
    
    money_wasters['waste_score'] = (
        (money_wasters['total_cost'] / money_wasters['total_cost'].max()) * 
        (1 - money_wasters['cvr'] / 100)
    )
    
    return money_wasters.sort_values('waste_score', ascending=False)

# Sidebar - Data Input
with st.sidebar:
    st.markdown("## 📊 Data Input")
    
    st.markdown("""
    <div class="info-box">
    <strong>Required Columns:</strong><br>
    • query (or keyword)<br>
    • clicks<br>
    • cost (or spend)<br>
    • conversions (or conv.)<br>
    <br>
    <strong>Optional:</strong><br>
    • impressions (will calculate from clicks if missing)
    </div>
    """, unsafe_allow_html=True)
    
    input_method = st.radio("Input Method", ["Paste Data", "Upload File"])
    
    df_input = None
    
    if input_method == "Paste Data":
        pasted_data = st.text_area(
            "Paste your CSV data here",
            height=200,
            placeholder="query,clicks,cost,conversions\nremortgage rates,150,245.50,12\ncheap remortgage,89,156.20,7"
        )
        if pasted_data:
            try:
                df_input = pd.read_csv(io.StringIO(pasted_data))
            except Exception as e:
                st.error(f"Error parsing data: {e}")
    else:
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file:
            try:
                df_input = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    st.markdown("---")
    st.markdown("## ⚙️ Analysis Settings")
    
    ngram_sizes = st.multiselect(
        "N-gram sizes to analyse",
        options=[1, 2, 3, 4],
        default=[1, 2, 3]
    )
    
    min_occurrences = st.slider(
        "Minimum query occurrences",
        min_value=1,
        max_value=10,
        value=2,
        help="N-grams must appear in at least this many queries"
    )
    
    sort_metric = st.selectbox(
        "Sort results by",
        options=['total_cost', 'total_clicks', 'total_conversions', 'cpa', 'cvr'],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    sort_ascending = st.checkbox("Sort ascending", value=False)
    
    st.markdown("---")
    st.markdown("## 🚫 Stop Words")
    
    use_stop_words = st.checkbox("Exclude stop words", value=True)
    
    if use_stop_words:
        custom_stop_words = st.text_area(
            "Custom stop words (one per line)",
            value='\n'.join(sorted(DEFAULT_STOP_WORDS)),
            height=150
        )
        stop_words = set(custom_stop_words.lower().split())
    else:
        stop_words = None
    
    st.markdown("---")
    st.markdown("## 🎯 Money Waster Detection")
    
    enable_money_waster = st.checkbox("Enable money waster analysis", value=True)
    
    if enable_money_waster:
        cost_percentile = st.slider(
            "High cost threshold (percentile)",
            min_value=50,
            max_value=95,
            value=75,
            help="N-grams above this cost percentile are flagged"
        )
        
        cvr_percentile = st.slider(
            "Low CVR threshold (percentile)",
            min_value=5,
            max_value=50,
            value=25,
            help="N-grams below this CVR percentile are flagged"
        )

# Main Content
if df_input is not None:
    # Validate and normalize column names
    df_input.columns = df_input.columns.str.lower().str.strip()
    
    # Map common column name variations
    column_mapping = {
        'keyword': 'query',
        'search term': 'query',
        'search_term': 'query',
        'spend': 'cost',
        'cost_gbp': 'cost',
        'conv.': 'conversions',
        'conv': 'conversions',
        'impr': 'impressions',
        'impr.': 'impressions'
    }
    
    df_input = df_input.rename(columns=column_mapping)
    
    # Check for required columns
    required_cols = {'query', 'clicks', 'cost', 'conversions'}
    missing_cols = required_cols - set(df_input.columns)
    
    if missing_cols:
        st.markdown(f"""
        <div class="warning-box">
        ⚠️ Missing required columns: {', '.join(missing_cols)}<br>
        Please ensure your data includes: query, clicks, cost, conversions
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Add impressions if missing
    if 'impressions' not in df_input.columns:
        df_input['impressions'] = df_input['clicks']
        st.info("ℹ️ Impressions column not found - using clicks as proxy")
    
    # Convert to numeric and clean
    numeric_cols = ['clicks', 'cost', 'conversions', 'impressions']
    for col in numeric_cols:
        df_input[col] = pd.to_numeric(df_input[col], errors='coerce').fillna(0)
    
    # Remove rows with no query
    df_input = df_input[df_input['query'].notna() & (df_input['query'] != '')]
    
    if st.button("🚀 Analyse N-Grams", type="primary"):
        with st.spinner("Analysing your data..."):
            results = {}
            for n in ngram_sizes:
                results[n] = analyze_ngrams(
                    df_input, 
                    n, 
                    min_occurrences, 
                    stop_words
                ).sort_values(sort_metric, ascending=sort_ascending)
            
            st.session_state.analyzed_data = results
        
        st.success("✅ Analysis complete!")
    
    if st.session_state.analyzed_data:
        results = st.session_state.analyzed_data
        
        # Summary metrics
        st.markdown("## 📈 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_queries = len(df_input)
        total_clicks = df_input['clicks'].sum()
        total_cost = df_input['cost'].sum()
        total_conversions = df_input['conversions'].sum()
        
        with col1:
            st.metric("Total Queries", f"{total_queries:,}")
        with col2:
            st.metric("Total Clicks", f"{int(total_clicks):,}")
        with col3:
            st.metric("Total Cost", f"£{total_cost:,.2f}")
        with col4:
            st.metric("Total Conversions", f"{int(total_conversions):,}")
        
        # N-gram tabs
        tabs = st.tabs([f"{n}-gram" for n in ngram_sizes])
        
        for tab, n in zip(tabs, ngram_sizes):
            with tab:
                df_ngram = results[n]
                
                if df_ngram.empty:
                    st.warning(f"No {n}-grams found with minimum {min_occurrences} occurrences")
                    continue
                
                # Summary for this n-gram size
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"Unique {n}-grams", f"{len(df_ngram):,}")
                with col2:
                    avg_cpa = df_ngram['cpa'].mean()
                    st.metric("Average CPA", f"£{avg_cpa:.2f}")
                with col3:
                    avg_cvr = df_ngram['cvr'].mean()
                    st.metric("Average CVR", f"{avg_cvr:.2f}%")
                
                # Money wasters section
                if enable_money_waster:
                    money_wasters = identify_money_wasters(
                        df_ngram, 
                        cost_percentile, 
                        cvr_percentile
                    )
                    
                    if not money_wasters.empty:
                        st.markdown("### 🚨 Money Wasters")
                        st.markdown(f"""
                        <div class="warning-box">
                        Found {len(money_wasters)} {n}-grams with high cost (>{cost_percentile}th percentile) 
                        and low CVR (<{cvr_percentile}th percentile)
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display top money wasters
                        display_cols = ['ngram', 'query_count', 'total_cost', 'total_conversions', 'cvr', 'cpa', 'waste_score']
                        st.dataframe(
                            money_wasters[display_cols].head(10).style.format({
                                'total_cost': '£{:.2f}',
                                'cvr': '{:.2f}%',
                                'cpa': '£{:.2f}',
                                'waste_score': '{:.3f}'
                            }).background_gradient(cmap='Reds', subset=['waste_score']),
                            use_container_width=True
                        )
                
                # Full results table
                st.markdown(f"### All {n}-grams")
                
                display_cols = ['ngram', 'query_count', 'total_clicks', 'total_cost', 
                               'total_conversions', 'ctr', 'cvr', 'cpa']
                
                # Format and display
                styled_df = df_ngram[display_cols].style.format({
                    'total_clicks': '{:,.0f}',
                    'total_cost': '£{:,.2f}',
                    'total_conversions': '{:,.0f}',
                    'ctr': '{:.2f}%',
                    'cvr': '{:.2f}%',
                    'cpa': '£{:.2f}'
                }).background_gradient(cmap='Greens', subset=['total_conversions'])
                
                st.dataframe(styled_df, use_container_width=True, height=400)
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df_ngram[display_cols].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {n}-gram Summary",
                        data=csv,
                        file_name=f'ngram_{n}_summary.csv',
                        mime='text/csv',
                        key=f'download_summary_{n}'
                    )
                
                with col2:
                    # Detailed export with queries
                    csv_detailed = df_ngram.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {n}-gram with Queries",
                        data=csv_detailed,
                        file_name=f'ngram_{n}_detailed.csv',
                        mime='text/csv',
                        key=f'download_detailed_{n}'
                    )

else:
    # Show instructions when no data
    st.markdown("""
    <div class="metric-card">
    <h2>👋 Welcome to the N-Gram Query Analyser</h2>
    <p style="color: #98c1d9; font-size: 1.1rem;">
    This tool helps you discover high-impact keyword patterns in your search query data.
    </p>
    
    <h3 style="color: #47d495; margin-top: 2rem;">How to use:</h3>
    <ol style="color: #98c1d9; font-size: 1rem; line-height: 1.8;">
        <li><strong>Prepare your data</strong> - Export search query data from Google Ads including: 
        query, clicks, cost, conversions (and optionally impressions)</li>
        <li><strong>Input your data</strong> - Either paste CSV data or upload a file using the sidebar</li>
        <li><strong>Configure settings</strong> - Choose n-gram sizes, minimum occurrences, and stop words</li>
        <li><strong>Analyse</strong> - Click the analyse button to process your data</li>
        <li><strong>Review results</strong> - Explore n-grams, identify money wasters, and download reports</li>
    </ol>
    
    <h3 style="color: #6f58c9; margin-top: 2rem;">What you'll discover:</h3>
    <ul style="color: #98c1d9; font-size: 1rem; line-height: 1.8;">
        <li>📊 <strong>High-performing keyword patterns</strong> across your campaigns</li>
        <li>💰 <strong>Money wasters</strong> - expensive n-grams with poor conversion rates</li>
        <li>🎯 <strong>Aggregated metrics</strong> - see total performance by n-gram across all queries</li>
        <li>📈 <strong>Actionable insights</strong> - identify opportunities for bid adjustments and negative keywords</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #98c1d9; padding: 2rem;">
    <p>Built with ❤️ for performance marketers | Platform81 Brand</p>
</div>
""", unsafe_allow_html=True)
