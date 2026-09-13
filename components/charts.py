import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math
from models.state_tax_config import TaxResult
from utils.formatter import format_percent, format_currency
from utils.i18n import t

def plot_bracket_chart(result: TaxResult) -> go.Figure:
    fig = go.Figure()
    
    for detail in result.bracket_details:
        start_val = detail.bracket_min
        end_val = detail.bracket_max if detail.bracket_max != math.inf else start_val + (start_val * 0.5 + 50000)
        
        # We can just plot step lines or rectangles
        fig.add_trace(go.Scatter(
            x=[start_val, end_val],
            y=[detail.rate, detail.rate],
            mode='lines',
            line=dict(color='royalblue', width=4),
            name=format_percent(detail.rate),
            hovertemplate=f"Income: {format_currency(start_val)} - {format_currency(end_val)}<br>Rate: {format_percent(detail.rate)}<extra></extra>"
        ))
        
        # Fill to zero
        fig.add_trace(go.Scatter(
            x=[start_val, end_val, end_val, start_val],
            y=[detail.rate, detail.rate, 0, 0],
            fill='toself',
            fillcolor='rgba(65, 105, 225, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo='skip',
            showlegend=False
        ))
        
    fig.update_layout(
        title=t('chart_brackets', state=result.state_name),
        xaxis_title=t('axis_income'),
        yaxis_title=t('axis_tax_rate'),
        yaxis_tickformat='.1%',
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def plot_comparison_bar(comparison_df: pd.DataFrame) -> go.Figure:
    df_sorted = comparison_df.sort_values('Total Tax', ascending=False)
    
    fig = px.bar(
        df_sorted,
        x='Total Tax',
        y='State',
        orientation='h',
        color='Total Tax',
        color_continuous_scale='RdYlGn_r',
        text=df_sorted['Effective Rate'].apply(format_percent)
    )
    
    fig.update_layout(
        title=t('chart_comparison'),
        xaxis_title=t('axis_total_tax'),
        yaxis_title="",
        coloraxis_showscale=False
    )
    
    fig.update_traces(textposition='outside')
    
    return fig

def plot_effective_rate_curve(curve_data: pd.DataFrame) -> go.Figure:
    fig = px.line(
        curve_data,
        x='Income',
        y='Effective Rate',
        color='State',
        title=t('chart_curve')
    )
    
    fig.update_layout(
        xaxis_title=t('axis_gross_income'),
        yaxis_title=t('axis_effective_rate'),
        yaxis_tickformat='.1%',
        hovermode='x unified'
    )
    
    return fig

def plot_us_map(map_data: pd.DataFrame) -> go.Figure:
    fig = px.choropleth(
        map_data,
        locationmode='USA-states',
        locations='Postal',
        color='Effective Rate',
        color_continuous_scale='RdYlGn_r',
        scope='usa',
        hover_name='State',
        hover_data={
            'Postal': False,
            'Effective Rate': ':.2%',
            'Total Tax': ':$,.0f',
            'Marginal Rate': ':.2%'
        },
        title=t('chart_map')
    )
    
    fig.update_layout(
        geo=dict(
            lakecolor='rgb(255, 255, 255)',
            projection_type='albers usa'
        )
    )
    
    return fig
