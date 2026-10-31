"""Regular dated bonds: actual/actual accrual and Treasury-style discounting.

Dates are contractual, unadjusted calendar dates. Settlement on a coupon date
is after payment. Issue date must be on the regular maturity-anchored grid;
stub coupons, business-day adjustments and ex-coupon rules are not modeled.
"""
from bisect import bisect_right
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from math import fsum, isfinite, log, log1p, nextafter
from typing import List

from scipy.optimize import brentq
from scipy.special import logsumexp

from ._validation import finite_real, positive_face_value, positive_frequency


class SettlementError(ValueError):
    """Input failure with a field usable by the website."""
    def __init__(self, field, message):
        self.field = field
        super().__init__(message)


def coupon_schedule(*, issue_date: date, maturity_date: date, frequency: int = 2) -> List[date]:
    """Include issue date and each payment date, preserving maturity's EOM rule."""
    frequency = positive_frequency(frequency)
    if frequency not in (1, 2, 4, 12):
        raise SettlementError('frequency', 'frequency must be 1, 2, 4, or 12.')
    for name, value in [('issue_date', issue_date), ('maturity_date', maturity_date)]:
        if type(value) is not date:
            raise SettlementError(name, name + ' must be a date.')
    if issue_date >= maturity_date:
        raise SettlementError('maturity_date', 'Maturity must be after the issue date.')
    if (maturity_date - issue_date).days > 366 * 100:
        raise SettlementError('maturity_date', 'Schedules are limited to 100 years.')
    months = 12 // frequency
    eom = maturity_date.day == monthrange(maturity_date.year, maturity_date.month)[1]
    result = []
    offset = 0
    while True:
        month_index = maturity_date.year * 12 + maturity_date.month - 1 - offset
        year, month = divmod(month_index, 12)
        month += 1
        last = monthrange(year, month)[1]
        payment = date(year, month, last if eom else min(maturity_date.day, last))
        result.append(payment)
        if payment <= issue_date:
            break
        offset += months
    if result[-1] != issue_date:
        raise SettlementError('issue_date', 'Issue date must be on the regular coupon schedule; stub coupons are not supported.')
    return list(reversed(result))


def _period(issue_date, maturity_date, settlement_date, frequency):
    schedule = coupon_schedule(issue_date=issue_date, maturity_date=maturity_date, frequency=frequency)
    if type(settlement_date) is not date or not issue_date <= settlement_date < maturity_date:
        raise SettlementError('settlement_date', 'Settlement must be on or after issue and before maturity.')
    index = bisect_right(schedule, settlement_date)
    previous, following = schedule[index - 1:index + 1]
    days = (following - previous).days
    elapsed = (settlement_date - previous).days
    return schedule[index:], previous, following, elapsed, days


def accrued_interest(*, face_value, coupon_rate, issue_date, maturity_date, settlement_date, frequency=2):
    """Coupon dollars times actual elapsed days / actual coupon-period days."""
    face_value = positive_face_value(face_value)
    coupon_rate = finite_real('coupon_rate', coupon_rate)
    if coupon_rate < 0:
        raise SettlementError('coupon_rate', 'coupon_rate must be nonnegative.')
    _, _, _, elapsed, days = _period(issue_date, maturity_date, settlement_date, frequency)
    return face_value * coupon_rate / frequency * elapsed / days


def clean_to_dirty(clean_price, accrued):
    """Convert dollar prices in matching face-value units, without rounding."""
    return finite_real('clean_price', clean_price) + finite_real('accrued', accrued)


def dirty_to_clean(dirty_price, accrued):
    return finite_real('dirty_price', dirty_price) - finite_real('accrued', accrued)


@dataclass(frozen=True)
class DatedCashFlow:
    payment_date: date
    coupon: float
    principal: float
    discount_factor: float
    present_value: float


@dataclass(frozen=True)
class SettledBondValuation:
    clean_price: float
    dirty_price: float
    accrued_interest: float
    previous_coupon: date
    next_coupon: date
    elapsed_days: int
    period_days: int
    remaining_fraction: float
    cashflows: List[DatedCashFlow]


def settled_bond_valuation(*, face_value, coupon_rate, ytm, issue_date, maturity_date,
                           settlement_date, frequency=2):
    """Dirty = sum(CF_k / (1+y/m)^k) / (1+w*y/m), k starts at zero.

    w is the fraction of the current coupon period remaining. The first
    fractional period uses simple interest; later whole periods compound.
    Annual nominal YTM must exceed -frequency. All prices are dollar amounts.
    """
    face_value = positive_face_value(face_value)
    frequency = positive_frequency(frequency)
    coupon_rate = finite_real('coupon_rate', coupon_rate)
    if coupon_rate < 0:
        raise SettlementError('coupon_rate', 'coupon_rate must be nonnegative.')
    ytm = finite_real('ytm', ytm)
    if ytm <= -frequency:
        raise SettlementError('ytm', 'YTM must be greater than minus the payment frequency.')
    dates, previous, following, elapsed, days = _period(issue_date, maturity_date, settlement_date, frequency)
    coupon = face_value * coupon_rate / frequency
    w = (days - elapsed) / days
    try:
        flows = []
        for k, payment in enumerate(dates):
            principal = face_value if payment == maturity_date else 0.0
            factor = (1 + ytm / frequency) ** (-k) / (1 + w * ytm / frequency)
            flows.append(DatedCashFlow(payment, coupon, principal, factor, (coupon + principal) * factor))
        dirty = fsum(flow.present_value for flow in flows)
        accrued = coupon * elapsed / days
        if not all(isfinite(value) for value in [dirty, accrued] + [flow.discount_factor for flow in flows]):
            raise OverflowError
    except (OverflowError, ZeroDivisionError) as exc:
        raise SettlementError('ytm', 'Inputs exceed numerical pricing precision.') from exc
    return SettledBondValuation(dirty_to_clean(dirty, accrued), dirty, accrued,
                               previous, following, elapsed, days, w, flows)


def settled_yield_to_maturity(*, price, price_type='clean', face_value, coupon_rate,
                              issue_date, maturity_date, settlement_date, frequency=2):
    """Solve dated nominal YTM from clean or dirty dollars, using the same model."""
    price = finite_real('price', price)
    if price <= 0:
        raise SettlementError('price', 'Price must be positive.')
    if price_type not in ('clean', 'dirty'):
        raise SettlementError('price_type', 'Choose clean or dirty price.')
    base = settled_bond_valuation(face_value=face_value, coupon_rate=coupon_rate, ytm=0,
        issue_date=issue_date, maturity_date=maturity_date, settlement_date=settlement_date, frequency=frequency)
    target = price + (base.accrued_interest if price_type == 'clean' else 0)
    logs = [(k, log(flow.coupon + flow.principal)) for k, flow in enumerate(base.cashflows)
            if flow.coupon + flow.principal > 0]
    w = base.remaining_fraction

    def objective(y):
        q = y / frequency
        return float(logsumexp([amount - k * log1p(q) for k, amount in logs])) - log1p(w * q) - log(target)

    lower, upper = nextafter(-float(frequency), 0), 1.0
    if objective(lower) < 0:
        raise SettlementError('price', 'Price implies a yield below the supported nominal-yield boundary.')
    for _ in range(1024):
        if objective(upper) <= 0:
            break
        upper *= 2
        if not isfinite(upper):
            raise SettlementError('price', 'Price implies a yield outside numerical precision.')
    return brentq(objective, lower, upper, xtol=1e-13)
