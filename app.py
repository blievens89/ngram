"""
N-Gram Query Analyser - Main Application
A powerful tool for analyzing search query data to discover high-impact keyword patterns
"""

import streamlit as st
import pandas as pd
import logging
from typing import Dict, Optional

# Import configuration
from config import APP_TITLE, APP_ICON, APP_LAYOUT

# Import core modules
from core import analyze_ngrams
from data import validate_and_map_columns, validate_data_quality
from ui import (
    apply_custom_styles,
    render_sidebar,
    display_overview_metrics,
    display_results,
    create_scatter_plot,
    create_top_performers_chart,
    create_cost_distribution_chart,
    create_cvr_vs_cpa_chart
)
from utils import setup_logging, save_analysis, load_analysis, get_saved_analyses

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT
)

# Apply custom styling
apply_custom_styles()

# Initialize session state
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None
if 'validated_data' not in st.session_state:
    st.session_state.validated_data = None


def main():
    """Main application logic"""

    # Header
    st.markdown(f'<h1>{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Discover high-impact keyword patterns in your search query data</p>',
        unsafe_allow_html=True
    )

    # Render sidebar and get data + settings
    df_input, settings = render_sidebar()

    # Show welcome message if no data
    if df_input is None:
        show_welcome_message()
        return

    # Validate and process data
    try:
        df_clean = validate_and_map_columns(df_input)
        st.session_state.validated_data = df_clean

        # Show data quality stats
        quality_stats = validate_data_quality(df_clean)
        logger.info(f"Data loaded: {quality_stats}")

    except ValueError as e:
        st.markdown(f"""
        <div class="warning-box">
        ⚠️ {str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Analysis controls
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        analyze_button = st.button("🚀 Analyse N-Grams", type="primary")

    with col2:
        if st.session_state.analyzed_data:
            show_viz = st.checkbox("📊 Show Visualizations", value=False)
        else:
            show_viz = False

    with col3:
        if st.session_state.analyzed_data:
            if st.button("💾 Save"):
                show_save_dialog()

    # Saved analyses loader
    if st.session_state.analyzed_data is None:
        saved_files = get_saved_analyses()
        if saved_files:
            st.markdown("### 📂 Load Previous Analysis")
            selected_file = st.selectbox(
                "Select saved analysis",
                options=[''] + saved_files,
                format_func=lambda x: x.replace('analysis_', '').replace('.json', '') if x else 'Select...'
            )
            if selected_file:
                st.session_state.analyzed_data = load_analysis(selected_file)
                st.success(f"✅ Loaded: {selected_file}")
                st.rerun()

    # Run analysis
    if analyze_button:
        run_analysis(df_clean, settings)

    # Display results
    if st.session_state.analyzed_data:
        results = st.session_state.analyzed_data

        # Overview metrics
        display_overview_metrics(df_clean)

        # Visualizations (if enabled)
        if show_viz:
            display_visualizations(results, settings['ngram_sizes'])

        # Tabbed results
        display_results(results, settings['ngram_sizes'], settings)

    # Footer
    show_footer()


@st.cache_data(ttl=3600)
def run_analysis_cached(
    df: pd.DataFrame,
    n: int,
    min_occurrences: int,
    stop_words_tuple: Optional[tuple],
    sort_metric: str,
    sort_ascending: bool
) -> pd.DataFrame:
    """
    Cached analysis function

    Args:
        df: Input DataFrame
        n: N-gram size
        min_occurrences: Minimum occurrences threshold
        stop_words_tuple: Tuple of stop words (tuple for caching)
        sort_metric: Metric to sort by
        sort_ascending: Sort direction

    Returns:
        Analyzed and sorted DataFrame
    """
    # Convert tuple back to set
    stop_words = set(stop_words_tuple) if stop_words_tuple else None

    logger.info(f"Running analysis for {n}-grams (cached)")

    result = analyze_ngrams(df, n, min_occurrences, stop_words)

    if not result.empty:
        result = result.sort_values(sort_metric, ascending=sort_ascending)

    return result


def run_analysis(df: pd.DataFrame, settings: dict):
    """
    Run n-gram analysis with current settings

    Args:
        df: Validated DataFrame
        settings: Analysis settings dictionary
    """
    with st.spinner("Analysing your data..."):
        results = {}

        # Convert stop words to tuple for caching
        stop_words_tuple = tuple(sorted(settings['stop_words'])) if settings['stop_words'] else None

        for n in settings['ngram_sizes']:
            try:
                results[n] = run_analysis_cached(
                    df,
                    n,
                    settings['min_occurrences'],
                    stop_words_tuple,
                    settings['sort_metric'],
                    settings['sort_ascending']
                )
                logger.info(f"Completed {n}-gram analysis: {len(results[n])} results")
            except Exception as e:
                logger.error(f"Error analyzing {n}-grams: {e}", exc_info=True)
                st.error(f"Error analyzing {n}-grams: {str(e)}")

        st.session_state.analyzed_data = results

    st.success("✅ Analysis complete!")


def display_visualizations(results: Dict[int, pd.DataFrame], ngram_sizes: list):
    """
    Display visualization charts

    Args:
        results: Analysis results dictionary
        ngram_sizes: List of n-gram sizes
    """
    st.markdown("## 📊 Visualizations")

    # Chart selection
    chart_type = st.selectbox(
        "Select visualization",
        options=[
            "Cost vs CVR Scatter",
            "Top Performers Bar Chart",
            "Cost Distribution",
            "CVR vs CPA Efficiency"
        ]
    )

    # N-gram size selector for charts
    n_for_chart = st.selectbox(
        "N-gram size",
        options=ngram_sizes,
        key="viz_ngram_size"
    )

    df_for_chart = results.get(n_for_chart)

    if df_for_chart is not None and not df_for_chart.empty:
        try:
            if chart_type == "Cost vs CVR Scatter":
                fig = create_scatter_plot(df_for_chart, n_for_chart)
            elif chart_type == "Top Performers Bar Chart":
                metric = st.selectbox(
                    "Metric to display",
                    options=['total_cost', 'total_conversions', 'total_clicks', 'cvr'],
                    key="bar_metric"
                )
                fig = create_top_performers_chart(df_for_chart, n_for_chart, metric)
            elif chart_type == "Cost Distribution":
                fig = create_cost_distribution_chart(df_for_chart, n_for_chart)
            elif chart_type == "CVR vs CPA Efficiency":
                fig = create_cvr_vs_cpa_chart(df_for_chart, n_for_chart)

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.error(f"Error creating visualization: {e}", exc_info=True)
            st.error(f"Error creating chart: {str(e)}")


def show_save_dialog():
    """Show dialog for saving analysis"""
    with st.form("save_form"):
        st.markdown("### 💾 Save Analysis")
        name = st.text_input(
            "Analysis name",
            value=f"analysis_{pd.Timestamp.now().strftime('%Y%m%d')}"
        )
        submitted = st.form_submit_button("Save")

        if submitted and name:
            # Get current settings from session (simplified)
            settings = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'name': name
            }
            filename = save_analysis(st.session_state.analyzed_data, settings, name)
            st.success(f"✅ Saved as: {filename}")


def show_welcome_message():
    """Display welcome message when no data is loaded"""
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
        <li><strong>Input your data</strong> - Either paste CSV data, upload a file, or use example data</li>
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
        <li>📉 <strong>Visual analytics</strong> - interactive charts to understand your data</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def show_footer():
    """Display footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #98c1d9; padding: 2rem;">
        <p>Built with ❤️ for performance marketers | Platform81 Brand</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
