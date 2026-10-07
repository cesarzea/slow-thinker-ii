"""Exact USD accounting in billionths of a dollar."""

from decimal import Decimal, InvalidOperation
from fractions import Fraction

QUANTA_PER_USD = 1_000_000_000
MAX_QUANTA = (1 << 63) - 1
MAX_USD = Decimal(f"{MAX_QUANTA // QUANTA_PER_USD}.{MAX_QUANTA % QUANTA_PER_USD:09d}")


def _exact_quanta(amount: Decimal) -> tuple[int, int]:
    if not amount.is_finite() or amount < 0 or amount > MAX_USD:
        raise ValueError("An amount must be finite, nonnegative and within the ledger range")
    if 0 < amount < Decimal("0.000000001"):
        return 0, 1
    numerator, denominator = amount.as_integer_ratio()
    return divmod(numerator * QUANTA_PER_USD, denominator)


def parse_usd(text: str) -> int:
    try:
        amount = Decimal(text)
    except InvalidOperation as error:
        raise ValueError("A budget must be a decimal amount") from error
    quanta, remainder = _exact_quanta(amount)
    if remainder:
        raise ValueError("A budget exceeds supported precision or range")
    return quanta


def format_usd(quanta: int) -> str:
    if quanta < 0 or quanta > MAX_QUANTA:
        raise ValueError("Invalid ledger amount")
    return f"{quanta // QUANTA_PER_USD}.{quanta % QUANTA_PER_USD:09d}"


def account_fraction(amount: Fraction) -> int:
    scaled = amount * QUANTA_PER_USD
    accounted = -(-scaled.numerator // scaled.denominator)
    if amount < 0 or accounted > MAX_QUANTA:
        raise ValueError("Charge exceeds ledger range")
    return accounted
