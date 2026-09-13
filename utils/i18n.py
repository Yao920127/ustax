"""Bilingual UI support: Traditional Chinese and English."""
import streamlit as st

LANGUAGES = {'zh-TW': '繁體中文', 'en': 'English'}
DEFAULT_LANG = 'zh-TW'

TEXT = {
    'zh-TW': {
        'app_title': '美國各州所得稅計算器',
        'error_loading': '載入資料時發生錯誤：',
        'tab_calculator': '🏠 稅額計算',
        'tab_comparison': '📊 多州比較',
        'tab_map': '🗺️ 全美稅率地圖',
        'header_calculator': '各州所得稅計算器',
        'header_comparison': '多州稅負比較',
        'header_map': '美國各州所得稅地圖',
        'data_source': '資料來源：Tax Foundation, 2026 State Individual Income Tax Rates and Brackets',
        'need_two_states': '請至少選擇 2 個州進行比較。',
        'params_header': '⚙️ 稅務參數',
        'state': '州別',
        'filing_status': '報稅身分',
        'filing_single': '單身',
        'filing_mfj': '已婚合併申報',
        'num_dependents': '扶養人數',
        'gross_income': '年收入',
        'quick_adjust': '快速調整',
        'capital_gains': '資本利得',
        'tax_year': '課稅年度',
        'language': '語言 / Language',
        'special_rules_note': '詳細特殊規則（phaseout 等）僅適用於 2026 年；其他年度以基本計算＋註腳提醒。',
        'summary_title': '{state} 稅額摘要',
        'total_tax': '總稅額',
        'effective_rate': '有效稅率',
        'marginal_rate': '邊際稅率',
        'after_tax_income': '稅後所得',
        'calculation_details': '計算明細',
        'standard_deduction': '標準扣除額',
        'personal_exemption': '個人免稅額',
        'taxable_income': '應稅所得',
        'no_income_tax_msg': '{state} 沒有州所得稅！',
        'cg_only_msg': '{state} 僅對資本利得課稅。本計算器假設普通所得不課稅，資本利得稅另以資本利得輸入值計算。',
        'id_only_msg': '{state} 僅對利息與股利課稅（普通薪資所得不課稅）。',
        'refund_msg': '退稅金額',
        'tax_brackets': '稅率級距',
        'tax_rate': '稅率',
        'income_range': '所得區間',
        'taxable_amount': '應稅金額',
        'tax_amount': '稅額',
        'state_notes': '州特殊規定與註腳',
        'note_label': '註記',
        'applied_rules': '已套用的特殊規則',
        'comparison_settings': '比較設定',
        'select_states': '選擇要比較的州',
        'select_all': '全選',
        'clear_all': '清空',
        'detailed_table': '詳細比較表',
        'all_states_data': '全美各州資料',
        'income_for_map': '地圖收入水準',
        'dependents': '扶養人數',
        'chart_brackets': '{state} 稅率級距',
        'chart_comparison': '各州稅額比較',
        'chart_curve': '不同收入水準之有效稅率',
        'chart_map': '美國各州所得稅地圖',
        'axis_income': '收入',
        'axis_tax_rate': '稅率',
        'axis_gross_income': '年收入',
        'axis_effective_rate': '有效稅率',
        'axis_total_tax': '總稅額',
        'state_col': '州',
        'total_tax_col': '總稅額',
        'effective_rate_col': '有效稅率',
        'marginal_rate_col': '邊際稅率',
        'after_tax_col': '稅後所得',
        'year': '年度',
        'cg_note': '資本利得輸入值會用於華盛頓州資本利得稅、馬里蘭州資本利得附加稅等規則。',
    },
    'en': {
        'app_title': 'US State Income Tax Calculator',
        'error_loading': 'Error loading data: ',
        'tab_calculator': '🏠 Tax Calculator',
        'tab_comparison': '📊 State Comparison',
        'tab_map': '🗺️ US Tax Map',
        'header_calculator': 'State Income Tax Calculator',
        'header_comparison': 'Multi-State Tax Comparison',
        'header_map': 'US State Income Tax Map',
        'data_source': 'Data source: Tax Foundation, 2026 State Individual Income Tax Rates and Brackets',
        'need_two_states': 'Please select at least 2 states to compare.',
        'params_header': '⚙️ Tax Parameters',
        'state': 'State',
        'filing_status': 'Filing Status',
        'filing_single': 'Single',
        'filing_mfj': 'Married Filing Jointly',
        'num_dependents': 'Number of Dependents',
        'gross_income': 'Gross Income',
        'quick_adjust': 'Quick Adjustment',
        'capital_gains': 'Capital Gains',
        'tax_year': 'Tax Year',
        'language': '語言 / Language',
        'special_rules_note': 'Detailed special rules (phaseouts, etc.) apply to 2026 only; other years use the basic calculation plus footnote reminders.',
        'summary_title': 'Tax Summary for {state}',
        'total_tax': 'Total Tax',
        'effective_rate': 'Effective Rate',
        'marginal_rate': 'Marginal Rate',
        'after_tax_income': 'After-Tax Income',
        'calculation_details': 'Calculation Details',
        'standard_deduction': 'Standard Deduction',
        'personal_exemption': 'Personal Exemption',
        'taxable_income': 'Taxable Income',
        'no_income_tax_msg': '{state} has no state income tax!',
        'cg_only_msg': '{state} only taxes capital gains. Ordinary income is not taxed; capital gains tax is computed from the capital gains input.',
        'id_only_msg': '{state} only taxes interest and dividend income (wages are not taxed).',
        'refund_msg': 'Refund',
        'tax_brackets': 'Tax Brackets',
        'tax_rate': 'Tax Rate',
        'income_range': 'Income Range',
        'taxable_amount': 'Taxable Amount',
        'tax_amount': 'Tax Amount',
        'state_notes': 'State Specific Notes & Footnotes',
        'note_label': 'Note',
        'applied_rules': 'Applied Special Rules',
        'comparison_settings': 'Comparison Settings',
        'select_states': 'Select States to Compare',
        'select_all': 'Select All',
        'clear_all': 'Clear',
        'detailed_table': 'Detailed Comparison Table',
        'all_states_data': 'All States Data',
        'income_for_map': 'Income for map',
        'dependents': 'Dependents',
        'chart_brackets': 'Tax Brackets - {state}',
        'chart_comparison': 'State Tax Comparison',
        'chart_curve': 'Effective Tax Rate by Income Level',
        'chart_map': 'US State Income Tax Map',
        'axis_income': 'Income',
        'axis_tax_rate': 'Tax Rate',
        'axis_gross_income': 'Gross Income',
        'axis_effective_rate': 'Effective Rate',
        'axis_total_tax': 'Total Tax',
        'state_col': 'State',
        'total_tax_col': 'Total Tax',
        'effective_rate_col': 'Effective Rate',
        'marginal_rate_col': 'Marginal Rate',
        'after_tax_col': 'After-Tax Income',
        'year': 'Year',
        'cg_note': 'The capital gains input drives Washington capital gains tax, Maryland surtax and other rules.',
    },
}


def lang() -> str:
    try:
        return st.session_state.get('lang', DEFAULT_LANG)
    except Exception:
        return DEFAULT_LANG


def t(key: str, **kwargs) -> str:
    """Translate a UI key. Falls back to English, then to the key itself."""
    table = TEXT.get(lang(), TEXT['en'])
    text = table.get(key, TEXT['en'].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def filing_status_label(filing_status) -> str:
    from models.filing_status import FilingStatus
    fs = FilingStatus.from_value(filing_status)
    if fs == FilingStatus.MARRIED_FILING_JOINTLY:
        return t('filing_mfj')
    return t('filing_single')