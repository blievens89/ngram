"""
Results display components
"""

import streamlit as st
import pandas as pd
from typing import Dict

from config import METRIC_FORMATS
from core import identify_money_wasters, generate_negative_keywords


def format_dataframe_for_display(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Format DataFrame values for display

    Args:
        df: DataFrame to format
        columns: List of columns to include

    Returns:
        Formatted DataFrame
    """
    display_df = df[columns].copy()

    for col in columns:
        if col in METRIC_FORMATS:
            fmt = METRIC_FORMATS[col]
            if col in ['total_cost', 'cpa']:
                display_df[col] = display_df[col].apply(lambda x: fmt.format(x))
            elif col in ['ctr', 'cvr']:
                display_df[col] = display_df[col].apply(lambda x: fmt.format(x))
            elif col in ['waste_score']:
                display_df[col] = display_df[col].apply(lambda x: fmt.format(x))
            else:
                display_df[col] = display_df[col].apply(lambda x: fmt.format(x))

    return display_df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply user-defined filters to DataFrame

    Args:
        df: DataFrame to filter
        filters: Dictionary with filter criteria

    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()

    if filters['min_cost'] > 0:
        filtered = filtered[filtered['total_cost'] >= filters['min_cost']]

    if filters['min_clicks'] > 0:
        filtered = filtered[filtered['total_clicks'] >= filters['min_clicks']]

    if filters['max_cpa'] > 0:
        filtered = filtered[filtered['cpa'] <= filters['max_cpa']]

    if filters['min_cvr'] > 0:
        filtered = filtered[filtered['cvr'] >= filters['min_cvr']]

    return filtered


def display_overview_metrics(df: pd.DataFrame):
    """Display overview metrics from the input data"""

    st.markdown("## 📈 Overview")

    col1, col2, col3, col4 = st.columns(4)

    total_queries = len(df)
    total_clicks = df['clicks'].sum()
    total_cost = df['cost'].sum()
    total_conversions = df['conversions'].sum()

    with col1:
        st.metric("Total Queries", f"{total_queries:,}")
    with col2:
        st.metric("Total Clicks", f"{int(total_clicks):,}")
    with col3:
        st.metric("Total Cost", f"£{total_cost:,.2f}")
    with col4:
        st.metric("Total Conversions", f"{int(total_conversions):,}")


def display_money_wasters(
    df_ngram: pd.DataFrame,
    n: int,
    cost_percentile: int,
    cvr_percentile: int
):
    """
    Display money wasters section

    Args:
        df_ngram: N-gram analysis results
        n: N-gram size
        cost_percentile: Cost threshold percentile
        cvr_percentile: CVR threshold percentile
    """
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

        display_df = format_dataframe_for_display(money_wasters.head(10), display_cols)
        st.dataframe(display_df, use_container_width=True)

        # Negative keyword generator
        st.markdown("### 🚫 Suggested Negative Keywords")

        waste_threshold = st.slider(
            "Min waste score for negatives",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key=f"waste_threshold_{n}"
        )

        negatives = generate_negative_keywords(money_wasters, waste_threshold)

        if negatives:
            st.text_area(
                f"Copy these {len(negatives)} negative keywords to your ad platform:",
                value='\n'.join(negatives),
                height=150,
                key=f"negatives_{n}"
            )

            # Download button
            csv = '\n'.join(negatives)
            st.download_button(
                "📥 Download Negative Keywords",
                data=csv,
                file_name=f'negative_keywords_{n}gram.txt',
                mime='text/plain',
                key=f'download_negatives_{n}'
            )


def display_ngram_tab(
    df_ngram: pd.DataFrame,
    n: int,
    min_occurrences: int,
    enable_money_waster: bool,
    cost_percentile: int,
    cvr_percentile: int,
    filters: dict
):
    """
    Display content for a single n-gram tab

    Args:
        df_ngram: N-gram analysis results
        n: N-gram size
        min_occurrences: Minimum occurrences filter
        enable_money_waster: Whether to show money waster analysis
        cost_percentile: Cost threshold percentile
        cvr_percentile: CVR threshold percentile
        filters: Advanced filter settings
    """
    if df_ngram.empty:
        st.warning(f"No {n}-grams found with minimum {min_occurrences} occurrences")
        return

    # Apply filters
    df_ngram = apply_filters(df_ngram, filters)

    if df_ngram.empty:
        st.warning(f"No {n}-grams match the current filters")
        return

    # Summary metrics
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
        display_money_wasters(df_ngram, n, cost_percentile, cvr_percentile)

    # Full results table
    st.markdown(f"### All {n}-grams")

    display_cols = ['ngram', 'query_count', 'total_clicks', 'total_cost',
                   'total_conversions', 'ctr', 'cvr', 'cpa']

    display_df = format_dataframe_for_display(df_ngram, display_cols)
    st.dataframe(display_df, use_container_width=True, height=400)

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


def display_results(
    results: Dict[int, pd.DataFrame],
    ngram_sizes: list,
    settings: dict
):
    """
    Display all analysis results in tabs

    Args:
        results: Dictionary mapping n-gram size to DataFrame
        ngram_sizes: List of n-gram sizes to display
        settings: Analysis settings dictionary
    """
    tabs = st.tabs([f"{n}-gram" for n in ngram_sizes])

    for tab, n in zip(tabs, ngram_sizes):
        with tab:
            df_ngram = results.get(n)
            if df_ngram is not None:
                display_ngram_tab(
                    df_ngram,
                    n,
                    settings['min_occurrences'],
                    settings['enable_money_waster'],
                    settings['cost_percentile'],
                    settings['cvr_percentile'],
                    settings['filters']
                )
