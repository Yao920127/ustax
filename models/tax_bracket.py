from dataclasses import dataclass
import math

@dataclass
class TaxBracket:
    """Represents a single tax bracket with rate and income range."""
    rate: float          # Tax rate, e.g. 0.02 for 2%
    min_income: float    # Bracket floor
    max_income: float    # Bracket ceiling (math.inf for top bracket)
    
    def __post_init__(self):
        if self.rate < 0 or self.rate > 1:
            raise ValueError(f"Rate must be between 0 and 1, got {self.rate}")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaxBracket':
        max_income = data.get('max_income')
        if max_income is None or max_income == float('inf'):
            max_income = math.inf
        return cls(
            rate=data['rate'],
            min_income=data['min_income'],
            max_income=max_income
        )

@dataclass
class BracketDetail:
    """Detail of tax calculation within a single bracket."""
    rate: float
    bracket_min: float
    bracket_max: float
    taxable_amount: float   # Amount of income taxed in this bracket
    tax_amount: float       # Tax generated in this bracket
