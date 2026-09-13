from dataclasses import dataclass, field
from typing import List
import math

from models.tax_bracket import TaxBracket, BracketDetail
from models.filing_status import FilingStatus


@dataclass
class StateTaxConfig:
    """Complete tax configuration for a single state."""
    state_name: str                         # Full name, e.g. "California"
    state_abbr: str                         # Abbreviation from data, e.g. "Calif."
    has_income_tax: bool                    # False for AK, FL, NV, NH, SD, TN, TX, WY
    is_capital_gains_only: bool             # True for Washington (TY 2022+)
    is_interest_dividends_only: bool = False  # NH (2015-2024), TN (2015-2020)
    brackets_single: List[TaxBracket] = field(default_factory=list)
    brackets_married: List[TaxBracket] = field(default_factory=list)
    standard_deduction_single: float = 0.0
    standard_deduction_married: float = 0.0
    standard_deduction_is_credit: bool = False   # Utah: standard deduction is a nonrefundable credit
    personal_exemption_single: float = 0.0
    personal_exemption_married: float = 0.0
    personal_exemption_dependent: float = 0.0
    exemption_is_credit: bool = False       # True if exemption is a tax credit
    dependent_exemption_is_credit: bool = False
    footnotes: List[str] = field(default_factory=list)
    notes: str = ""
    
    def get_brackets(self, filing_status: FilingStatus) -> List[TaxBracket]:
        """Get tax brackets for the given filing status."""
        if filing_status == FilingStatus.SINGLE:
            return self.brackets_single
        return self.brackets_married
    
    def get_standard_deduction(self, filing_status: FilingStatus) -> float:
        """Get standard deduction for the given filing status."""
        if filing_status == FilingStatus.SINGLE:
            return self.standard_deduction_single
        return self.standard_deduction_married
    
    def get_personal_exemption(self, filing_status: FilingStatus) -> float:
        """Get personal exemption for the given filing status."""
        if filing_status == FilingStatus.SINGLE:
            return self.personal_exemption_single
        return self.personal_exemption_married
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StateTaxConfig':
        """Create StateTaxConfig from a dictionary (loaded from JSON)."""
        brackets_single = [TaxBracket.from_dict(b) for b in data.get('brackets_single', [])]
        brackets_married = [TaxBracket.from_dict(b) for b in data.get('brackets_married', [])]
        return cls(
            state_name=data['state_name'],
            state_abbr=data.get('state_abbr', ''),
            has_income_tax=data.get('has_income_tax', True),
            is_capital_gains_only=data.get('is_capital_gains_only', False),
            is_interest_dividends_only=data.get('is_interest_dividends_only', False),
            brackets_single=brackets_single,
            brackets_married=brackets_married,
            standard_deduction_single=data.get('standard_deduction_single', 0.0),
            standard_deduction_married=data.get('standard_deduction_married', 0.0),
            standard_deduction_is_credit=data.get('standard_deduction_is_credit', False),
            personal_exemption_single=data.get('personal_exemption_single', 0.0),
            personal_exemption_married=data.get('personal_exemption_married', 0.0),
            personal_exemption_dependent=data.get('personal_exemption_dependent', 0.0),
            exemption_is_credit=data.get('exemption_is_credit', False),
            dependent_exemption_is_credit=data.get('dependent_exemption_is_credit', False),
            footnotes=data.get('footnotes', []),
            notes=data.get('notes', '')
        )


@dataclass
class TaxResult:
    """Result of a tax calculation for a single state."""
    state_name: str
    gross_income: float
    filing_status: str
    standard_deduction: float
    personal_exemption: float
    dependent_exemption: float
    taxable_income: float
    bracket_details: List[BracketDetail] = field(default_factory=list)
    total_tax: float = 0.0
    effective_rate: float = 0.0       # total_tax / gross_income
    marginal_rate: float = 0.0        # Highest bracket rate applied
    is_capital_gains_only: bool = False
    is_interest_dividends_only: bool = False
    has_income_tax: bool = True
    capital_gains: float = 0.0
    applied_rules: List[dict] = field(default_factory=list)
