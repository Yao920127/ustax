import streamlit as st
import pandas as pd
from typing import List
from models.filing_status import FilingStatus, FILING_STATUS_VALUES
from components.charts import plot_comparison_bar, plot_effective_rate_curve
from utils.formatter import format_currency, format_percent
from utils.i18n import t, filing_status_label

def render_comparison_sidebar(state_names: List[str]) -> dict:
    st.subheader(t('comparison_settings'))
    
    default_states = ['California', 'Texas', 'New York', 'Florida']
    valid_defaults = [s for s in default_states if s in state_names]
    if not valid_defaults and state_names:
        valid_defaults = [state_names[0]]
        
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_col, clear_col = st.columns(2)
        with sel_col:
            if st.button(t('select_all'), key='comp_select_all', width='stretch'):
                st.session_state['comp_states'] = list(state_names)
        with clear_col:
            if st.button(t('clear_all'), key='comp_clear_all', width='stretch'):
                st.session_state['comp_states'] = []
        
        selected_states = st.multiselect(
            t('select_states'),
            options=state_names,
            default=valid_defaults,
            key='comp_states'
        )
    with col2:
        filing_status = st.radio(
            t('filing_status'),
            options=FILING_STATUS_VALUES,
            format_func=filing_status_label
        )
    with col3:
        num_dependents = st.number_input(
            t('num_dependents'),
            min_value=0, max_value=10, value=0, step=1, key="comp_deps"
        )
    
    col4, col5 = st.columns(2)
    with col4:
        gross_income = st.number_input(
            t('gross_income'),
            min_value=0, max_value=100_000_000, value=100_000,
            step=5000, format="%d", key="comp_income"
        )
    with col5:
        capital_gains = st.number_input(
            t('capital_gains'),
            min_value=0, max_value=100_000_000, value=0,
            step=5000, format="%d", key="comp_cg",
            help=t('cg_note')
        )
        
    return {
        'selected_states': selected_states,
        'filing_status': FilingStatus.from_value(filing_status),
        'num_dependents': num_dependents,
        'gross_income': gross_income,
        'capital_gains': capital_gains
    }

def render_comparison(comparison_df: pd.DataFrame, curve_data: pd.DataFrame):
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = plot_comparison_bar(comparison_df)
        st.plotly_chart(fig_bar, width="stretch")
        
    with col2:
        fig_curve = plot_effective_rate_curve(curve_data)
        st.plotly_chart(fig_curve, width="stretch")
        
    st.markdown(f"### {t('detailed_table')}")
    
    # Format the dataframe for display
    display_df = comparison_df.rename(columns={'State': t('state_col')}).copy()
    display_df[t('total_tax_col')] = display_df['Total Tax'].apply(format_currency)
    display_df[t('effective_rate_col')] = display_df['Effective Rate'].apply(format_percent)
    display_df[t('marginal_rate_col')] = display_df['Marginal Rate'].apply(format_percent)
    display_df[t('after_tax_col')] = display_df['After-Tax Income'].apply(format_currency)
    
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )