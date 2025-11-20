"""
Visualization components using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import BrandColors


colors = BrandColors()


def create_scatter_plot(df: pd.DataFrame, n: int) -> go.Figure:
    """
    Create scatter plot of cost vs CVR

    Args:
        df: N-gram analysis DataFrame
        n: N-gram size

    Returns:
        Plotly figure
    """
    # Take top 50 by cost to avoid clutter
    plot_df = df.nlargest(50, 'total_cost')

    fig = px.scatter(
        plot_df,
        x='total_cost',
        y='cvr',
        size='total_clicks',
        color='cpa',
        hover_data=['ngram', 'query_count', 'total_conversions'],
        title=f'{n}-gram Performance: Cost vs CVR',
        labels={
            'total_cost': 'Total Cost (£)',
            'cvr': 'Conversion Rate (%)',
            'cpa': 'CPA (£)',
            'total_clicks': 'Clicks'
        },
        color_continuous_scale='RdYlGn_r'  # Red (high) to Green (low) for CPA
    )

    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor=colors.NIGHT_LIGHT,
        paper_bgcolor=colors.NIGHT,
        font=dict(color=colors.POWDER_BLUE)
    )

    return fig


def create_top_performers_chart(df: pd.DataFrame, n: int, metric: str = 'total_cost') -> go.Figure:
    """
    Create bar chart of top performers by specified metric

    Args:
        df: N-gram analysis DataFrame
        n: N-gram size
        metric: Metric to chart ('total_cost', 'total_conversions', etc.)

    Returns:
        Plotly figure
    """
    top_10 = df.nlargest(10, metric)

    metric_labels = {
        'total_cost': 'Total Cost (£)',
        'total_conversions': 'Total Conversions',
        'total_clicks': 'Total Clicks',
        'cvr': 'Conversion Rate (%)',
        'cpa': 'CPA (£)'
    }

    # Format values for display
    if metric in ['total_cost', 'cpa']:
        text_values = top_10[metric].apply(lambda x: f'£{x:.2f}')
    elif metric in ['cvr']:
        text_values = top_10[metric].apply(lambda x: f'{x:.2f}%')
    else:
        text_values = top_10[metric].apply(lambda x: f'{x:,.0f}')

    fig = go.Figure(data=[
        go.Bar(
            x=top_10['ngram'],
            y=top_10[metric],
            text=text_values,
            textposition='auto',
            marker=dict(
                color=top_10[metric],
                colorscale='Viridis',
                showscale=True
            )
        )
    ])

    fig.update_layout(
        title=f'Top 10 {n}-grams by {metric_labels.get(metric, metric)}',
        xaxis_title='N-gram',
        yaxis_title=metric_labels.get(metric, metric),
        template='plotly_dark',
        plot_bgcolor=colors.NIGHT_LIGHT,
        paper_bgcolor=colors.NIGHT,
        font=dict(color=colors.POWDER_BLUE),
        showlegend=False
    )

    return fig


def create_cost_distribution_chart(df: pd.DataFrame, n: int) -> go.Figure:
    """
    Create histogram showing cost distribution

    Args:
        df: N-gram analysis DataFrame
        n: N-gram size

    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[
        go.Histogram(
            x=df['total_cost'],
            nbinsx=30,
            marker=dict(
                color=colors.EMERALD,
                line=dict(color=colors.NIGHT, width=1)
            )
        )
    ])

    fig.update_layout(
        title=f'{n}-gram Cost Distribution',
        xaxis_title='Total Cost (£)',
        yaxis_title='Frequency',
        template='plotly_dark',
        plot_bgcolor=colors.NIGHT_LIGHT,
        paper_bgcolor=colors.NIGHT,
        font=dict(color=colors.POWDER_BLUE),
        showlegend=False
    )

    return fig


def create_cvr_vs_cpa_chart(df: pd.DataFrame, n: int) -> go.Figure:
    """
    Create scatter plot showing CVR vs CPA relationship

    Args:
        df: N-gram analysis DataFrame
        n: N-gram size

    Returns:
        Plotly figure
    """
    # Filter out extreme values for better visualization
    plot_df = df[df['cpa'] < df['cpa'].quantile(0.95)]

    fig = px.scatter(
        plot_df,
        x='cpa',
        y='cvr',
        size='total_cost',
        color='total_conversions',
        hover_data=['ngram', 'query_count'],
        title=f'{n}-gram Efficiency: CVR vs CPA',
        labels={
            'cpa': 'Cost Per Acquisition (£)',
            'cvr': 'Conversion Rate (%)',
            'total_cost': 'Total Cost',
            'total_conversions': 'Conversions'
        },
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor=colors.NIGHT_LIGHT,
        paper_bgcolor=colors.NIGHT,
        font=dict(color=colors.POWDER_BLUE)
    )

    return fig
