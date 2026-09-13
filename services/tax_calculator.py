"""Tax calculation engine with progressive bracket support and special rules."""
from typing import List, Optional, Tuple

from models.filing_status import FilingStatus
from models.tax_bracket import TaxBracket, BracketDetail
from models.state_tax_config import StateTaxConfig, TaxResult
from services.special_rules import RuleEngine


class TaxCalculator:
    """Calculates state income tax using progressive bracket rates."""

    def calculate(
        self,
        gross_income: float,
        state_config: StateTaxConfig,
        filing_status: FilingStatus,
        num_dependents: int = 0,
        capital_gains: float = 0.0,
        rules: Optional[RuleEngine] = None,
        year: int = 2026,
    ) -> TaxResult:
        """Calculate state income tax for the given parameters.

        Args:
            gross_income: Gross ordinary income before deductions
            state_config: State tax configuration with brackets and deductions
            filing_status: Single or Married Filing Jointly
            num_dependents: Number of dependents claimed
            capital_gains: Capital gains income (used by WA / MD / MN rules)
            rules: RuleEngine with curated special rules (phaseouts etc.)
            year: Tax year (used to look up rules)
        """
        # Defensive: filing_status may arrive as a string after Streamlit
        # session-state serialization round-trips.
        filing_status = FilingStatus.from_value(filing_status)
        state_name = state_config.state_name
        applied_rules: List[dict] = []
        agi = gross_income + capital_gains

        # No income tax state
        if not state_config.has_income_tax:
            return self._zero_result(
                state_config, gross_income, filing_status, capital_gains,
                is_capital_gains_only=False, is_interest_dividends_only=False,
                applied_rules=applied_rules
            )

        # Washington: capital gains only
        if state_config.is_capital_gains_only:
            tax = 0.0
            if rules is not None:
                tax, notes = rules.washington_capital_gains_tax(year, state_name, capital_gains)
                applied_rules.extend(notes)
            result = self._zero_result(
                state_config, gross_income, filing_status, capital_gains,
                is_capital_gains_only=True, is_interest_dividends_only=False,
                applied_rules=applied_rules
            )
            result.total_tax = tax
            if agi > 0:
                result.effective_rate = tax / agi
            return result

        # Interest & dividends only (NH 2015-2024, TN 2015-2020)
        if state_config.is_interest_dividends_only:
            return self._zero_result(
                state_config, gross_income, filing_status, capital_gains,
                is_capital_gains_only=False, is_interest_dividends_only=True,
                applied_rules=applied_rules
            )

        # ---- Ordinary income pipeline ----
        standard_deduction = state_config.get_standard_deduction(filing_status)
        personal_exemption = state_config.get_personal_exemption(filing_status)
        dependent_exemption = state_config.personal_exemption_dependent * num_dependents

        if rules is not None:
            standard_deduction, notes = rules.adjust_standard_deduction(
                year, state_name, agi, filing_status, standard_deduction
            )
            applied_rules.extend(notes)
            personal_exemption, dependent_exemption, notes = rules.adjust_exemptions(
                year, state_name, agi, filing_status, num_dependents,
                personal_exemption, dependent_exemption,
                state_config.exemption_is_credit, state_config.dependent_exemption_is_credit
            )
            applied_rules.extend(notes)

        # Split into deductions (reduce income) and credits (reduce tax).
        deductions = 0.0
        nonrefundable_credits = 0.0
        refundable_credits = 0.0

        if state_config.standard_deduction_is_credit:
            nonrefundable_credits += standard_deduction
        else:
            deductions += standard_deduction

        if state_config.exemption_is_credit:
            nonrefundable_credits += personal_exemption
        else:
            deductions += personal_exemption

        if state_config.dependent_exemption_is_credit:
            if rules is not None and rules.is_dependent_credit_refundable(year, state_name):
                # Maine: refundable dependent credit (tax may fall below zero)
                refundable_credits += dependent_exemption
                note = rules.refundable_note(year, state_name)
                if note:
                    applied_rules.append(note)
            else:
                nonrefundable_credits += dependent_exemption
        else:
            deductions += dependent_exemption

        taxable_income = max(0.0, gross_income - deductions)

        # Apply progressive brackets
        brackets = state_config.get_brackets(filing_status)
        bracket_details, total_tax = self._apply_brackets(taxable_income, brackets)

        # Post-bracket additions: recapture payments and surtaxes
        if rules is not None and bracket_details:
            top_rate = max((d.rate for d in bracket_details), default=0.0)
            added, notes = rules.adjust_tax(
                year, state_name, agi, capital_gains, filing_status,
                taxable_income, bracket_details, total_tax, top_rate
            )
            total_tax += added
            applied_rules.extend(notes)

        # Credits: nonrefundable floor at zero; refundable may go below zero
        total_tax = max(0.0, total_tax - nonrefundable_credits)
        total_tax -= refundable_credits

        # Final minimum-tax floors (e.g. Vermont 3% of AGI)
        if rules is not None:
            floor, notes = rules.final_floor(year, state_name, agi, filing_status)
            if floor is not None:
                total_tax = max(total_tax, floor)
                applied_rules.extend(notes)

        # Rates
        effective_rate = total_tax / gross_income if gross_income > 0 else 0.0

        marginal_rate = 0.0
        if taxable_income > 0:
            for detail in reversed(bracket_details):
                if detail.taxable_amount > 0:
                    marginal_rate = detail.rate
                    break

        return TaxResult(
            state_name=state_name,
            gross_income=gross_income,
            filing_status=filing_status.display_name,
            standard_deduction=standard_deduction,
            personal_exemption=personal_exemption,
            dependent_exemption=dependent_exemption,
            taxable_income=taxable_income,
            bracket_details=bracket_details,
            total_tax=total_tax,
            effective_rate=effective_rate,
            marginal_rate=marginal_rate,
            is_capital_gains_only=False,
            is_interest_dividends_only=False,
            has_income_tax=True,
            capital_gains=capital_gains,
            applied_rules=applied_rules
        )

    def _zero_result(
        self,
        state_config: StateTaxConfig,
        gross_income: float,
        filing_status: FilingStatus,
        capital_gains: float,
        is_capital_gains_only: bool,
        is_interest_dividends_only: bool,
        applied_rules: List[dict],
    ) -> TaxResult:
        return TaxResult(
            state_name=state_config.state_name,
            gross_income=gross_income,
            filing_status=filing_status.display_name,
            standard_deduction=0.0,
            personal_exemption=0.0,
            dependent_exemption=0.0,
            taxable_income=0.0,
            bracket_details=[],
            total_tax=0.0,
            effective_rate=0.0,
            marginal_rate=0.0,
            is_capital_gains_only=is_capital_gains_only,
            is_interest_dividends_only=is_interest_dividends_only,
            has_income_tax=state_config.has_income_tax,
            capital_gains=capital_gains,
            applied_rules=applied_rules
        )

    def _apply_brackets(
        self, taxable_income: float, brackets: List[TaxBracket]
    ) -> Tuple[List[BracketDetail], float]:
        """Apply progressive tax brackets to taxable income.

        Returns:
            Tuple of (bracket details list, total tax)
        """
        bracket_details = []
        total_tax = 0.0

        for bracket in brackets:
            if taxable_income > bracket.min_income:
                max_in = min(taxable_income, bracket.max_income)
                amount_in_bracket = max(0.0, max_in - bracket.min_income)
                tax_in_bracket = amount_in_bracket * bracket.rate
                total_tax += tax_in_bracket

                bracket_details.append(BracketDetail(
                    rate=bracket.rate,
                    bracket_min=bracket.min_income,
                    bracket_max=bracket.max_income,
                    taxable_amount=amount_in_bracket,
                    tax_amount=tax_in_bracket
                ))
            else:
                bracket_details.append(BracketDetail(
                    rate=bracket.rate,
                    bracket_min=bracket.min_income,
                    bracket_max=bracket.max_income,
                    taxable_amount=0.0,
                    tax_amount=0.0
                ))

        return bracket_details, total_tax