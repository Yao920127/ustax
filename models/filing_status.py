from enum import Enum


class FilingStatus(Enum):
    """Tax filing status options."""
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"

    @classmethod
    def from_value(cls, value) -> "FilingStatus":
        """Normalize a value (enum member or string) into a FilingStatus.

        Streamlit serializes widget values to strings on the round-trip
        through the browser, so radio returns may arrive as e.g.
        "single", "married_filing_jointly", or "FilingStatus.SINGLE".
        This handles all of those, plus the enum itself.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, Enum):
            # Enum member from a possibly-reloaded module (e.g. Streamlit
            # hot-reload): it may belong to a different FilingStatus class
            # than `cls`, so the isinstance check above misses it. Normalize
            # by the member's `.value` instead.
            try:
                return cls(value.value)
            except ValueError:
                pass
        if isinstance(value, str):
            v = value.strip()
            if v.startswith("FilingStatus."):
                v = v.split(".", 1)[1]
            try:
                return cls(v)
            except ValueError:
                pass
            for member in cls:
                if member.name == v:
                    return member
                if member.display_name.lower() == value.strip().lower():
                    return member
        raise ValueError(f"Cannot convert {value!r} to FilingStatus")

    @property
    def display_name(self) -> str:
        if self == FilingStatus.SINGLE:
            return "Single"
        return "Married Filing Jointly"


# String values that are safe for Streamlit widget serialization.
FILING_STATUS_VALUES = [fs.value for fs in FilingStatus]
