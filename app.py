import json
import streamlit as st
from services.data_loader import DataLoader, AVAILABLE_YEARS
from services.tax_calculator import TaxCalculator
from services.comparison_service import ComparisonService
from services.special_rules import RuleEngine
from models.filing_status import FilingStatus, FILING_STATUS_VALUES
from components.sidebar import render_sidebar
from components.tax_result import render_tax_result
from components.comparison_view import render_comparison, render_comparison_sidebar
from components.charts import plot_bracket_chart
from utils.formatter import format_currency, format_percent
from utils.constants import STATE_FULL_TO_POSTAL
from utils.i18n import t, lang, filing_status_label, LANGUAGES, DEFAULT_LANG
import numpy as np
from pathlib import Path

# Page config
st.set_page_config(
    page_title=t('app_title'),
    page_icon="🏛️",
    layout="wide"
)

# ---- Global settings (visible across tabs) ----
with st.sidebar:
    st.header("🌐")
    language_label = st.selectbox(
        t('language'),
        options=list(LANGUAGES.keys()),
        format_func=lambda k: LANGUAGES[k],
        index=list(LANGUAGES.keys()).index(st.session_state.get('lang', DEFAULT_LANG)),
        key='lang_selector'
    )
    st.session_state['lang'] = language_label

    tax_year = st.selectbox(
        t('tax_year'),
        options=AVAILABLE_YEARS[::-1],  # newest first
        index=0,
        key='year_selector'
    )


@st.cache_data
def _load_special_rules() -> dict:
    rules_path = Path(__file__).parent / 'data' / 'special_rules.json'
    with open(rules_path, 'r') as f:
        return json.load(f)


@st.cache_resource
def init_services(year: int):
    loader = DataLoader(year)
    calculator = TaxCalculator()
    rule_engine = RuleEngine(_load_special_rules())
    comparison = ComparisonService(loader, calculator, rule_engine, year)
    return loader, calculator, rule_engine, comparison

try:
    loader, calculator, rule_engine, comparison = init_services(tax_year)
    state_names = loader.get_all_state_names()
except Exception as e:
    st.error(f"{t('error_loading')}{e}")
    st.stop()

if tax_year != 2026:
    st.info(t('special_rules_note'))

# Navigation
tab1, tab2, tab3 = st.tabs([t('tab_calculator'), t('tab_comparison'), t('tab_map')])

with tab1:
    st.header(t('header_calculator'))
    # Sidebar for single state
    with st.sidebar:
        params = render_sidebar(state_names)
    
    # Calculate
    config = loader.get_state(params['state_name'])
    result = calculator.calculate(
        params['gross_income'], config, params['filing_status'], params['num_dependents'],
        capital_gains=params['capital_gains'], rules=rule_engine, year=tax_year
    )
    
    # Display results
    render_tax_result(result, config, loader.get_all_footnotes(lang()))
    
    # Bracket chart
    if result.has_income_tax and result.bracket_details:
        fig = plot_bracket_chart(result)
        st.plotly_chart(fig, width="stretch")

with tab2:
    st.header(t('header_comparison'))
    comp_params = render_comparison_sidebar(state_names)
    
    if len(comp_params['selected_states']) >= 2:
        comp_df = comparison.compare_states(
            comp_params['selected_states'],
            comp_params['gross_income'],
            comp_params['filing_status'],
            comp_params['num_dependents'],
            comp_params['capital_gains']
        )
        
        income_points = list(range(10000, 510000, 10000))
        curve_data = comparison.income_curve(
            comp_params['selected_states'],
            income_points,
            comp_params['filing_status'],
            comp_params['num_dependents'],
            comp_params['capital_gains']
        )
        
        render_comparison(comp_df, curve_data)
    else:
        st.info(t('need_two_states'))

with tab3:
    st.header(t('header_map'))
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        map_income = st.number_input(t('income_for_map'), min_value=0, max_value=100_000_000, value=100_000, step=5000, format="%d", key="map_income")
    with col2:
        map_filing = st.radio(t('filing_status'), FILING_STATUS_VALUES, format_func=filing_status_label, key="map_filing", horizontal=True)
    with col3:
        map_deps = st.number_input(t('dependents'), min_value=0, max_value=10, value=0, key="map_deps")
    with col4:
        map_cg = st.number_input(t('capital_gains'), min_value=0, max_value=100_000_000, value=0, step=5000, format="%d", key="map_cg", help=t('cg_note'))
    
    map_df = comparison.all_states_comparison(map_income, FilingStatus.from_value(map_filing), map_deps, map_cg)
    # Add postal codes for the map
    map_df['Postal'] = map_df['State'].map(STATE_FULL_TO_POSTAL)
    
    from components.charts import plot_us_map
    fig = plot_us_map(map_df)
    st.plotly_chart(fig, width="stretch")
    
    # Show the full table below the map
    st.subheader(t('all_states_data'))
    display_df = map_df[['State', 'Total Tax', 'Effective Rate', 'Marginal Rate', 'After-Tax Income']].sort_values('Total Tax').copy()
    display_df.columns = [t('state_col'), t('total_tax_col'), t('effective_rate_col'), t('marginal_rate_col'), t('after_tax_col')]
    display_df[t('total_tax_col')] = display_df[t('total_tax_col')].apply(format_currency)
    display_df[t('effective_rate_col')] = display_df[t('effective_rate_col')].apply(format_percent)
    display_df[t('marginal_rate_col')] = display_df[t('marginal_rate_col')].apply(format_percent)
    display_df[t('after_tax_col')] = display_df[t('after_tax_col')].apply(format_currency)
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )

st.divider()
st.markdown(t('data_source'))