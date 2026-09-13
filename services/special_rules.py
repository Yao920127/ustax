"""Special rule engine: phaseouts, recapture, refundable credits, surtaxes.

Rules are curated per tax year in data/special_rules.json. For years without
curated rules the calculator falls back to the base progressive calculation
and the applicable footnotes are still shown.
"""
import math
from typing import Dict, List, Optional, Tuple

from models.filing_status import FilingStatus
from models.tax_bracket import BracketDetail


class RuleEngine:
    def __init__(self, rules_by_year: Dict[str, Dict[str, dict]]):
        self.rules_by_year = rules_by_year

    # ---- accessors -------------------------------------------------------
    def year_has_rules(self, year: int) -> bool:
        return str(year) in self.rules_by_year

    def state_rules(self, year: int, state_name: str) -> Dict[str, dict]:
        return self.rules_by_year.get(str(year), {}).get(state_name, {})

    # ---- rule applications ------------------------------------------------
    def adjust_standard_deduction(
        self, year: int, state_name: str, agi: float,
        filing_status: FilingStatus, sd: float
    ) -> Tuple[float, List[dict]]:
        """Apply rules that modify the standard deduction. Returns (new_sd, notes)."""
        rules = self.state_rules(year, state_name)
        notes: List[dict] = []

        # Vermont: extra deduction per federal standard deduction box
        r = rules.get('extra_standard_deduction')
        if r:
            extra = r['married'] if filing_status == FilingStatus.MARRIED_FILING_JOINTLY else r['single']
            sd += extra
            notes.append({'rule': 'vt_extra_standard_deduction', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # Minnesota: standard deduction phaseout
        r = rules.get('standard_deduction_phaseout')
        if r and agi > r['t1']:
            t1, t2 = r['t1'], r['t2']
            pct1, pct2 = r['pct1'], r['pct2']
            reduction = pct1 * max(0.0, min(agi, t2) - t1) + pct2 * max(0.0, agi - t2)
            reduction = min(reduction, r['max_reduction_pct'] * sd)
            sd = max(0.0, sd - reduction)
            notes.append({'rule': 'mn_standard_deduction_phaseout', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        return sd, notes

    def adjust_exemptions(
        self, year: int, state_name: str, agi: float,
        filing_status: FilingStatus, num_dependents: int,
        personal_exemption: float, dependent_exemption: float,
        personal_is_credit: bool, dependent_is_credit: bool
    ) -> Tuple[float, float, List[dict]]:
        """Apply rules that modify personal/dependent exemptions (deduction or credit form).
        Returns (new_personal, new_dependent, notes)."""
        rules = self.state_rules(year, state_name)
        notes: List[dict] = []
        is_mfj = filing_status == FilingStatus.MARRIED_FILING_JOINTLY

        # Connecticut: personal exemption phaseout in $1,000 steps
        r = rules.get('exemption_phaseout_step')
        if r and personal_exemption > 0:
            threshold = r['thresholds']['married' if is_mfj else 'single']
            if agi > threshold:
                steps = math.ceil((agi - threshold) / r['step_size'])
                reduction = steps * r['reduction_per_step']
                personal_exemption = max(0.0, personal_exemption - reduction)
                notes.append({'rule': 'ct_exemption_phaseout_step', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # Ohio: tiered personal/dependent exemption by AGI
        r = rules.get('exemption_tiers')
        if r:
            tier_amount = r['tiers'][0]['amount']
            for tier in r['tiers']:
                if tier['max_agi'] is None or agi <= tier['max_agi']:
                    tier_amount = tier['amount']
                    break
            multiplier = 2 if is_mfj else 1
            personal_exemption = tier_amount * multiplier
            dependent_exemption = tier_amount * num_dependents
            notes.append({'rule': 'oh_exemption_tiers', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # Maryland: linear phaseout of the exemption
        r = rules.get('exemption_phaseout_range')
        if r:
            rng = r['married' if is_mfj else 'single']
            start, end = rng['start'], rng['end']
            if agi > start:
                ratio = max(0.0, min(1.0, (end - agi) / (end - start)))
                personal_exemption *= ratio
                dependent_exemption *= ratio
                notes.append({'rule': 'md_exemption_phaseout_range', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # New Mexico: $4,000 deduction for all but one dependent
        r = rules.get('dependent_deduction_all_but_one')
        if r:
            dependent_exemption = r['per_dependent'] * max(0, num_dependents - 1)
            notes.append({'rule': 'nm_dependent_deduction_all_but_one', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # California: exemption credit phaseout (credits, not below zero)
        r = rules.get('exemption_credit_phaseout')
        if r:
            threshold = r['thresholds']['married' if is_mfj else 'single']
            per_step = r['reduction_per_step']['married' if is_mfj else 'single']
            if agi > threshold:
                steps = math.ceil((agi - threshold) / r['step_size'])
                reduction = steps * per_step
                if personal_is_credit:
                    personal_exemption = max(0.0, personal_exemption - reduction)
                if dependent_is_credit:
                    dependent_exemption = max(0.0, dependent_exemption - reduction)
                notes.append({'rule': 'ca_exemption_credit_phaseout', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # Oregon: personal exemption credit disallowed above AGI threshold
        r = rules.get('exemption_credit_limit')
        if r:
            threshold = r['thresholds']['married' if is_mfj else 'single']
            if agi > threshold and personal_is_credit:
                personal_exemption = 0.0
                notes.append({'rule': 'or_exemption_credit_limit', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        return personal_exemption, dependent_exemption, notes

    def adjust_tax(
        self, year: int, state_name: str, agi: float, capital_gains: float,
        filing_status: FilingStatus, taxable_income: float,
        bracket_details: List[BracketDetail], tax_before_credits: float,
        top_rate: float
    ) -> Tuple[float, List[dict]]:
        """Post-bracket additions: recapture payments and surtaxes.
        Returns (added_tax, notes)."""
        rules = self.state_rules(year, state_name)
        notes: List[dict] = []
        added = 0.0
        is_mfj = filing_status == FilingStatus.MARRIED_FILING_JOINTLY

        # Connecticut recapture
        r = rules.get('recapture')
        if r:
            # 2% bracket shifted to 4.5%
            shift = r['bracket_shift']['married' if is_mfj else 'single']
            if agi > shift['threshold']:
                steps = math.ceil((agi - shift['threshold']) / shift['step_size'])
                shift_amount = steps * shift['reduction_per_step']
                two_pct_taxable = 0.0
                for d in bracket_details:
                    if abs(d.rate - 0.02) < 1e-9:
                        two_pct_taxable = d.taxable_amount
                        break
                shift_amount = min(shift_amount, two_pct_taxable)
                added += shift_amount * r['shift_rate_delta']
            # recapture payments
            key = 'married' if is_mfj else 'single'
            pay = r['payments'][key]
            items = pay['items']
            combined_from = pay.get('combined_from_index', len(items))
            combined_max = pay.get('combined_max')
            payments_total = 0.0
            combined_sum = 0.0
            for i, p in enumerate(items):
                if agi <= p['threshold']:
                    continue
                excess = agi - p['threshold']
                if 'upper_bound' in p:
                    excess = min(excess, p['upper_bound'] - p['threshold'])
                amount = math.ceil(excess / p['step_size']) * p['per_step']
                if 'max' in p:
                    amount = min(amount, p['max'])
                if i >= combined_from:
                    combined_sum += amount
                payments_total += amount
            if combined_max is not None and combined_sum > combined_max:
                payments_total -= (combined_sum - combined_max)
            added += payments_total
            notes.append({'rule': 'ct_recapture', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # New York recapture: top rate on all taxable income
        r = rules.get('top_rate_recapture')
        if r:
            threshold = r['thresholds']['married' if is_mfj else 'single']
            if agi > threshold:
                recaptured = top_rate * taxable_income - tax_before_credits
                if recaptured > 0:
                    added += recaptured
                    notes.append({'rule': 'ny_recapture', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # Maryland: 2% surtax on capital gains when AGI exceeds threshold
        r = rules.get('capital_gains_surtax')
        if r and capital_gains > 0 and agi > r['agi_threshold']:
            added += r['rate'] * capital_gains
            notes.append({'rule': 'md_capital_gains_surtax', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        # Minnesota: 1% surtax on investment income over $1M (approximated by capital gains)
        r = rules.get('investment_surtax')
        if r and capital_gains > r['threshold']:
            added += r['rate'] * (capital_gains - r['threshold'])
            notes.append({'rule': 'mn_investment_surtax', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})

        return added, notes

    def final_floor(
        self, year: int, state_name: str, agi: float,
        filing_status: FilingStatus
    ) -> Tuple[Optional[float], List[dict]]:
        """Minimum-tax floors applied after credits (e.g. Vermont 3% of AGI)."""
        rules = self.state_rules(year, state_name)
        notes: List[dict] = []

        r = rules.get('agi_floor')
        if r and agi > r['threshold']:
            notes.append({'rule': 'vt_agi_floor', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])})
            return r['rate'] * agi, notes

        return None, notes

    def is_dependent_credit_refundable(self, year: int, state_name: str) -> bool:
        rules = self.state_rules(year, state_name)
        return 'refundable_dependent_credit' in rules

    def refundable_note(self, year: int, state_name: str) -> Optional[dict]:
        rules = self.state_rules(year, state_name)
        r = rules.get('refundable_dependent_credit')
        if r:
            return {'rule': 'me_refundable_dependent_credit', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])}
        return None

    def washington_capital_gains_tax(self, year: int, state_name: str, capital_gains: float) -> Tuple[float, List[dict]]:
        """WA excise on capital gains: 7% on taxable gains up to $1M, 9% above."""
        rules = self.state_rules(year, state_name)
        r = rules.get('capital_gains_tax')
        if not r or capital_gains <= 0:
            return 0.0, []
        taxable = max(0.0, capital_gains - r['standard_deduction'])
        tax = 0.07 * min(taxable, 1_000_000.0) + 0.09 * max(0.0, taxable - 1_000_000.0)
        notes = [{'rule': 'wa_capital_gains_tax', 'note': r['note'], 'note_zh': r.get('note_zh', r['note'])}]
        return tax, notes
