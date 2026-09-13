import json
from pathlib import Path
from typing import Dict, List

import streamlit as st

from models.state_tax_config import StateTaxConfig

AVAILABLE_YEARS = list(range(2015, 2027))  # 2015-2026


@st.cache_data
def _load_tax_data(year: int) -> Dict[str, dict]:
    data_path = Path(__file__).parent.parent / 'data' / f'tax_data_{year}.json'
    with open(data_path, 'r') as f:
        return json.load(f)


@st.cache_data
def _load_footnotes(year: int) -> Dict[str, str]:
    data_path = Path(__file__).parent.parent / 'data' / f'footnotes_{year}.json'
    with open(data_path, 'r') as f:
        return json.load(f)


@st.cache_data
def _load_footnotes_zh() -> Dict[str, str]:
    data_path = Path(__file__).parent.parent / 'data' / 'footnotes_zh.json'
    with open(data_path, 'r') as f:
        return json.load(f)


class DataLoader:
    def __init__(self, year: int = 2026):
        self.year = year
        self._states_cache: Dict[str, StateTaxConfig] = {}
        
    def load(self) -> Dict[str, StateTaxConfig]:
        if not self._states_cache:
            raw_data = _load_tax_data(self.year)
            for abbr, state_dict in raw_data.items():
                config = StateTaxConfig.from_dict(state_dict)
                self._states_cache[config.state_name] = config
        return self._states_cache

    def get_state(self, name: str) -> StateTaxConfig:
        states = self.load()
        if name not in states:
            raise KeyError(f"State {name} not found")
        return states[name]

    def get_all_state_names(self) -> List[str]:
        states = self.load()
        return sorted(list(states.keys()))

    def get_footnote(self, code: str, lang_code: str = 'en') -> str:
        footnotes = self.get_all_footnotes(lang_code)
        return footnotes.get(code, "")

    def get_all_footnotes(self, lang_code: str = 'en') -> Dict[str, str]:
        footnotes = _load_footnotes(self.year)
        if lang_code != 'zh-TW':
            return footnotes
        zh = _load_footnotes_zh()
        return {code: zh.get(text, text) for code, text in footnotes.items()}
