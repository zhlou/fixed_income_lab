"""Regular fixed-coupon payments, with time measured in years."""

from dataclasses import dataclass
from math import isclose
from typing import List

from ._validation import finite_real, positive_face_value, positive_frequency


@dataclass(frozen=True)
class CashFlow:
    """An amount received at time_years after valuation."""

    time_years: float
    amount: float


def fixed_coupon_cashflows(
    *,
    face_value: float,
    coupon_rate: float,
    maturity_years: float,
    frequency: int = 2,
) -> List[CashFlow]:
    """Generate payments starting one full coupon period after valuation.

    coupon_rate is annual and decimal (0.04 means 4%). Maturity must be a
    positive whole number of coupon periods. The final payment includes
    principal. Actual dates, stub periods, and accrued interest are excluded.
    A zero coupon rate produces zero interim amounts and principal at maturity.
    """
    face_value = positive_face_value(face_value)
    frequency = positive_frequency(frequency)
    coupon_rate = finite_real("coupon_rate", coupon_rate)
    maturity_years = finite_real("maturity_years", maturity_years)
    if coupon_rate < 0:
        raise ValueError("coupon_rate must be nonnegative.")
    if maturity_years <= 0:
        raise ValueError("maturity_years must be positive for a coupon schedule.")

    periods = maturity_years * frequency
    count = round(periods)
    if count < 1 or not isclose(periods, count, rel_tol=0, abs_tol=1e-9):
        raise ValueError("maturity_years must contain a whole number of coupon periods.")

    coupon = face_value * coupon_rate / frequency
    return [
        CashFlow(
            time_years=k / frequency,
            amount=coupon + (face_value if k == count else 0.0),
        )
        for k in range(1, count + 1)
    ]
