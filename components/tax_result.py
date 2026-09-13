import streamlit as st
import pandas as pd
from typing import Dict
from models.state_tax_config import StateTaxConfig, TaxResult
from utils.formatter import format_currency, format_percent, format_income_range
from utils.i18n import t, lang

NOTES_ZH = {
    'Standard deduction is a credit.': '標準扣除額以抵稅額形式提供。',
}

def render_tax_result(result: TaxResult, config: StateTaxConfig, footnotes: Dict[str, str]):
    st.subheader(t('summary_title', state=result.state_name))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if result.total_tax < 0:
            st.metric(t('refund_msg'), format_currency(-result.total_tax))
        else:
            st.metric(t('total_tax'), format_currency(result.total_tax))
    with col2:
        st.metric(t('effective_rate'), format_percent(max(0.0, result.effective_rate)))
    with col3:
        st.metric(t('marginal_rate'), format_percent(result.marginal_rate))
        
    st.divider()
    
    st.markdown(f"### {t('calculation_details')}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**{t('gross_income')}:** {format_currency(result.gross_income)}")
    with col2:
        st.markdown(f"**{t('standard_deduction')}:** {format_currency(result.standard_deduction)}")
    with col3:
        exemption = result.personal_exemption + result.dependent_exemption
        st.markdown(f"**{t('personal_exemption')}:** {format_currency(exemption)}")
    with col4:
        st.markdown(f"**{t('taxable_income')}:** {format_currency(result.taxable_income)}")
    
    if result.capital_gains > 0:
        st.markdown(f"**{t('capital_gains')}:** {format_currency(result.capital_gains)}")
        
    st.divider()
    
    if not result.has_income_tax:
        st.success(t('no_income_tax_msg', state=result.state_name))
    elif result.is_capital_gains_only:
        st.info(t('cg_only_msg', state=result.state_name))
    elif result.is_interest_dividends_only:
        st.info(t('id_only_msg', state=result.state_name))
    
    # Applied special rules
    if result.applied_rules:
        st.markdown(f"### {t('applied_rules')}")
        seen = set()
        for rule in result.applied_rules:
            if rule['rule'] in seen:
                continue
            seen.add(rule['rule'])
            note = rule.get('note_zh') if lang() == 'zh-TW' else rule.get('note')
            st.markdown(f"- {note}")
    
    if result.has_income_tax and result.bracket_details:
        st.markdown(f"### {t('tax_brackets')}")
        
        bracket_data = []
        for detail in result.bracket_details:
            bracket_data.append({
                t('tax_rate'): format_percent(detail.rate),
                t('income_range'): format_income_range(detail.bracket_min, detail.bracket_max),
                t('taxable_amount'): format_currency(detail.taxable_amount),
                t('tax_amount'): format_currency(detail.tax_amount)
            })
            
        st.dataframe(pd.DataFrame(bracket_data), width="stretch", hide_index=True)
        
    if config.footnotes:
        with st.expander(t('state_notes')):
            for ref in config.footnotes:
                if ref in footnotes:
                    st.markdown(f"- **{ref}**: {footnotes[ref]}")
            if config.notes:
                note_text = config.notes.strip()
                if lang() == 'zh-TW':
                    note_text = NOTES_ZH.get(note_text, note_text)
                st.markdown(f"- **{t('note_label')}**: {note_text}")
