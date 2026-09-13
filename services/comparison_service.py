"""Multi-state tax comparison service."""
from typing import List
import pandas as pd

from models.filing_status import FilingStatus
from services.data_loader import DataLoader
from services.tax_calculator import TaxCalculator


class ComparisonService:
    """Service for comparing tax across multiple states."""

    def __init__(self, data_loader: DataLoader, calculator: TaxCalculator, rules=None, year: int = 2026):
        self.data_loader = data_loader
        self.calculator = calculator
        self.rules = rules
        self.year = year

    def compare_states(
        self,
        state_names: List[str],
        gross_income: float,
        filing_status: FilingStatus,
        num_dependents: int = 0,
        capital_gains: float = 0.0
    ) -> pd.DataFrame:
        """Compare tax across multiple states at a single income level.
        
        Returns DataFrame with columns:
            State, Total Tax, Effective Rate, Marginal Rate, After-Tax Income
        """
        results = []
        for state_name in state_names:
            config = self.data_loader.get_state(state_name)
            tax_result = self.calculator.calculate(
                gross_income, config, filing_status, num_dependents,
                capital_gains=capital_gains, rules=self.rules, year=self.year
            )
            results.append({
                "State": state_name,
                "Total Tax": tax_result.total_tax,
                "Effective Rate": tax_result.effective_rate,
                "Marginal Rate": tax_result.marginal_rate,
                "After-Tax Income": gross_income - tax_result.total_tax
            })

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values("Total Tax").reset_index(drop=True)
        return df

    def all_states_comparison(
        self,
        gross_income: float,
        filing_status: FilingStatus,
        num_dependents: int = 0,
        capital_gains: float = 0.0
    ) -> pd.DataFrame:
        """Calculate tax for ALL states. Used for the US map view."""
        all_states = self.data_loader.get_all_state_names()
        return self.compare_states(
            all_states, gross_income, filing_status, num_dependents, capital_gains
        )

    def income_curve(
        self,
        state_names: List[str],
        income_range: List[float],
        filing_status: FilingStatus,
        num_dependents: int = 0,
        capital_gains: float = 0.0
    ) -> pd.DataFrame:
        """Calculate effective rate at each income level for multiple states.
        
        Returns DataFrame in long format with columns:
            Income, State, Effective Rate
        """
        rows = []
        for state_name in state_names:
            config = self.data_loader.get_state(state_name)
            for income in income_range:
                tax_result = self.calculator.calculate(
                    income, config, filing_status, num_dependents,
                    capital_gains=capital_gains, rules=self.rules, year=self.year
                )
                rows.append({
                    "Income": income,
                    "State": state_name,
                    "Effective Rate": tax_result.effective_rate
                })

        return pd.DataFrame(rows)
