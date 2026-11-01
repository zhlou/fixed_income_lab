"""Derivatives with respect to annual nominal decimal YTM, at fixed dates.

Dollar duration is -dP/dy (dollars per unit decimal yield); DV01 is that
positive magnitude times 0.0001. Convexity is P''/P, with no factor of 1/2.
Dated sensitivities normalize by dirty price and preserve the settlement pricer.
"""
from dataclasses import dataclass
from math import fsum, isfinite
from typing import Optional

from filab.pricing import fixed_coupon_cashflows, price_coupon_bond, settled_bond_valuation
from filab.pricing._validation import finite_real


@dataclass(frozen=True)
class RiskMeasures:
    price: float
    macaulay_duration: Optional[float]
    modified_duration: float
    dollar_duration: float
    dv01: float
    convexity: float
    bump: Optional[float] = None


def _measures(price, duration, convexity, macaulay=None, bump=None):
    values = (price, duration, convexity, price * duration, price * duration * .0001)
    if price <= 0 or not all(isfinite(v) for v in values):
        raise ValueError('Inputs exceed numerical risk precision.')
    return RiskMeasures(price, macaulay, duration, price * duration,
                        price * duration * .0001, convexity, bump)


def bond_risk(*, face_value, coupon_rate, ytm, maturity_years, frequency=2):
    """Analytical yield risk just after payment, using regular coupon periods.

    Macaulay duration is PV-weighted time in years. Modified duration and
    convexity are derivatives with respect to annual nominal decimal YTM.
    Zero coupons are supported on the same regular schedule. Units of price,
    dollar duration, and DV01 follow face_value; intermediate values are unrounded.
    """
    args = dict(face_value=face_value, coupon_rate=coupon_rate,
                maturity_years=maturity_years, frequency=frequency)
    price = price_coupon_bond(ytm=ytm, **args)
    if price <= 0 or not isfinite(price):
        raise ValueError('Inputs exceed numerical risk precision.')
    flows = fixed_coupon_cashflows(**args)
    q = 1 + ytm / frequency
    weights = [flow.amount * q ** (-k) / price for k, flow in enumerate(flows, 1)]
    macaulay = fsum(w * flow.time_years for w, flow in zip(weights, flows))
    convexity = fsum(w * k * (k + 1) / (frequency * q) ** 2
                     for k, w in enumerate(weights, 1))
    return _measures(price, macaulay / q, convexity, macaulay)


def numerical_risk(pricer, *, ytm, bump=.0001):
    """Central differences at y +/- bump; pricer must return positive dollars.

    Default bump is one basis point of annual decimal yield. No rounding or
    curve shifts are applied. Very small bumps can suffer cancellation; use a
    bump-convergence comparison, not an assumption that smaller is always better.
    Macaulay duration is deliberately absent for an arbitrary pricing convention.
    """
    ytm, bump = finite_real('ytm', ytm), finite_real('bump', bump)
    if bump <= 0 or bump * bump == 0 or ytm + bump == ytm or ytm - bump == ytm:
        raise ValueError('bump must be positive and distinguishable at this yield.')
    down, price, up = [finite_real('price', pricer(y)) for y in (ytm - bump, ytm, ytm + bump)]
    if min(down, price, up) <= 0:
        raise ValueError('Risk requires positive prices at all three yields.')
    duration = (down - up) / (2 * bump * price)
    convexity = fsum((down, up, -2 * price)) / (bump * bump * price)
    return _measures(price, duration, convexity, bump=bump)


def dated_bond_risk(*, ytm, bump=.0001, **bond):
    """Numerical dirty-price risk at fixed settlement, preserving dated conventions.

    Actual/Actual coupon accrual; simple first fractional period; regular,
    unadjusted maturity-anchored coupons; coupon-date settlement after payment.
    No textbook Macaulay-to-modified conversion is asserted between coupons.
    """
    return numerical_risk(lambda y: settled_bond_valuation(ytm=y, **bond).dirty_price,
                          ytm=ytm, bump=bump)


def yield_scenarios(pricer, *, ytm, risk, shocks):
    """Exact and approximate instantaneous price changes; errors = estimate - exact.

    shocks are annual decimal yield changes. No time, payment, reinvestment or
    return calculation is involved. Taylor price estimates can be negative for
    sufficiently large shocks and are never clipped into plausible prices.
    """
    ytm = finite_real('ytm', ytm)
    rows = []
    for shock in shocks:
        shock = finite_real('shock', shock)
        exact = finite_real('price', pricer(ytm + shock))
        if exact <= 0:
            raise ValueError('Scenario price must be positive.')
        first = -risk.dollar_duration * shock
        second = first + .5 * risk.price * risk.convexity * shock ** 2
        change = exact - risk.price
        rows.append(dict(shock=shock, shock_bp=shock * 10000, exact_price=exact,
                         exact_change=change, exact_percent=change / risk.price,
                         duration_change=first, duration_percent=first / risk.price,
                         convexity_change=second, convexity_percent=second / risk.price,
                         duration_error=first - change, convexity_error=second - change,
                         duration_error_percent=(first - change) / risk.price,
                         convexity_error_percent=(second - change) / risk.price))
    return rows
