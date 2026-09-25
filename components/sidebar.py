import streamlit as st
from typing import List
from models.filing_status import FilingStatus, FILING_STATUS_VALUES
from utils.i18n import t, filing_status_label

def render_sidebar(state_names: List[str]) -> dict:
    st.sidebar.header(t('params_header'))
    
    state_name = st.sidebar.selectbox(
        t('state'),
        options=state_names,
        index=state_names.index("California") if "California" in state_names else 0
    )
    
    filing_status = st.sidebar.radio(
        t('filing_status'),
        options=FILING_STATUS_VALUES,
        format_func=filing_status_label
    )
    
    num_dependents = st.sidebar.number_input(
        t('num_dependents'),
        min_value=0, max_value=10, value=0, step=1
    )
    
    # Sync slider and number input
    if 'gross_income' not in st.session_state:
        st.session_state.gross_income = 100_000
        
    def update_income_from_number():
        st.session_state.gross_income = st.session_state.income_num
        st.session_state.income_slider = min(st.session_state.income_num, 1_000_000)

    def update_income_from_slider():
        st.session_state.gross_income = st.session_state.income_slider
        st.session_state.income_num = st.session_state.income_slider

    gross_income_num = st.sidebar.number_input(
        t('gross_income'),
        min_value=0, max_value=100_000_000, value=st.session_state.gross_income,
        step=1000, format="%d", key="income_num", on_change=update_income_from_number
    )
    
    gross_income_slider = st.sidebar.slider(
        t('quick_adjust'),
        min_value=0, max_value=1_000_000, value=st.session_state.gross_income if st.session_state.gross_income <= 1_000_000 else 1_000_000,
        step=5000, key="income_slider", on_change=update_income_from_slider
    )
    
    capital_gains = st.sidebar.number_input(
        t('capital_gains'),
        min_value=0, max_value=100_000_000, value=0,
        step=1000, format="%d", key="capital_gains_tab1",
        help=t('cg_note')
    )
    
    return {
        'state_name': state_name,
        'filing_status': FilingStatus.from_value(filing_status),
        'num_dependents': num_dependents,
        'gross_income': st.session_state.gross_income,
        'capital_gains': capital_gains
    }