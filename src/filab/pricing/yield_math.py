"""Price promised cash flows using a supplied annual nominal yield."""

from math import expm1, fsum, isfinite, log

from scipy.optimize import brentq
from scipy.special import logsumexp

from ._validation import finite_real, positive_face_value, positive_frequency
from .cashflows import fixed_coupon_cashflows


def _period_rate(ytm: float, frequency: int) -> float:
    ytm = finite_real("ytm", ytm)
    if ytm <= -frequency:
        raise ValueError("ytm must be greater than -frequency (positive discount base).")
    return ytm / frequency


def price_zero_coupon(
    *,
    face_value: float,
    ytm: float,
    maturity_years: float,
    frequency: int = 2,
) -> float:
    """Return F / (1 + ytm/frequency) ** (frequency * maturity_years).

    ytm is an annual nominal decimal yield compounded frequency times a year,
    not an effective annual rate or a Treasury bill discount yield. Fractional
    periods use this compound-rate convention. At maturity (time zero), return F.
    """
    face_value = positive_face_value(face_value)
    frequency = positive_frequency(frequency)
    rate = _period_rate(ytm, frequency)
    maturity_years = finite_real("maturity_years", maturity_years)
    if maturity_years < 0:
        raise ValueError("maturity_years must be nonnegative.")

    periods = frequency * maturity_years
    return face_value / (1 + rate) ** periods


def price_coupon_bond(
    *,
    face_value: float,
    coupon_rate: float,
    ytm: float,
    maturity_years: float,
    frequency: int = 2,
) -> float:
    """Sum discounted regular coupon payments and the principal repayment.

    Rates are annual decimals. ytm is nominal, compounded at the coupon
    frequency. Valuation is immediately after a coupon payment, so the next
    payment is one full period away and accrued interest is zero. Maturity
    must contain a positive whole number of coupon periods. Prices are in
    the same units as face_value, with no intermediate rounding.
    """
    frequency = positive_frequency(frequency)
    rate = _period_rate(ytm, frequency)
    cashflows = fixed_coupon_cashflows(
        face_value=face_value,
        coupon_rate=coupon_rate,
        maturity_years=maturity_years,
        frequency=frequency,
    )
    return fsum(
        cashflow.amount / (1 + rate) ** period
        for period, cashflow in enumerate(cashflows, start=1)
    )


def yield_to_maturity(
    *,
    price: float,
    face_value: float,
    coupon_rate: float,
    maturity_years: float,
    frequency: int = 2,
) -> float:
    """Solve for annual nominal decimal YTM, compounded at coupon frequency.

    Uses the same regular-period, immediately-after-coupon assumptions as
    price_coupon_bond. Price is in face-value units, not a quote per $100.
    Zero coupon rates are supported on regular schedules. Price must be
    positive; YTM can be negative but must exceed -frequency.

    Brent's method solves in log(1 + ytm/frequency). Log-sum-exp keeps the
    objective finite near the discount-base boundary and for long maturities.
    """
    price = finite_real("price", price)
    if price <= 0:
        raise ValueError("price must be positive.")
    frequency = positive_frequency(frequency)
    flows = fixed_coupon_cashflows(
        face_value=face_value, coupon_rate=coupon_rate,
        maturity_years=maturity_years, frequency=frequency,
    )
    if any(not isfinite(flow.amount) for flow in flows):
        raise ValueError("bond inputs produce cash flows outside numerical precision.")
    payments = [(period, log(flow.amount)) for period, flow in enumerate(flows, 1)
                if flow.amount > 0]
    log_price = log(price)

    def objective(log_base):
        return float(logsumexp([amount - period * log_base
                                for period, amount in payments])) - log_price

    lower, upper = -1.0, 1.0
    while objective(lower) < 0:
        lower *= 2
    while objective(upper) > 0:
        upper *= 2
    root = brentq(objective, lower, upper, xtol=1e-14)
    try:
        ytm = frequency * expm1(root)
    except OverflowError as exc:
        raise ValueError("price implies a yield outside numerical precision.") from exc
    if not isfinite(ytm) or ytm <= -frequency:
        raise ValueError("price implies a yield outside numerical precision.")
    return ytm
