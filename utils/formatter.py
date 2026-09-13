"""Formatting utilities for currency and percentage display."""
import math

def format_currency(amount: float) -> str:
    """Format a number as US currency. e.g. 1234.5 -> '$1,234.50'"""
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"

def format_currency_short(amount: float) -> str:
    """Format currency in compact form. e.g. 1500000 -> '$1.5M'"""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:,.0f}"

def format_percent(rate: float, decimals: int = 2) -> str:
    """Format a decimal rate as percentage. e.g. 0.0525 -> '5.25%'"""
    return f"{rate * 100:.{decimals}f}%"

def format_income_range(min_val: float, max_val: float) -> str:
    """Format an income range. e.g. (10000, 50000) -> '$10,000 – $50,000'"""
    if max_val == math.inf or max_val == float('inf'):
        return f"${min_val:,.0f} +"
    return f"${min_val:,.0f} – ${max_val:,.0f}"
