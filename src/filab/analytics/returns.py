"""Deterministic holding-period accounting, independent of HTTP and the UI.

Buy all positions at the opening date, after any payment that day. Subsequent
cash events precede that day's sales and closing valuation. Prices use the
existing regular dated YTM model. A yield point is a hypothetical step change,
effective on its date and carried forward until the next point; never backfilled.
"""
from dataclasses import dataclass
from datetime import date
from math import expm1, fsum, isfinite, log1p
from typing import Optional, Sequence, Tuple

from filab.pricing import coupon_schedule, settled_bond_valuation
from filab.pricing._validation import finite_real, positive_face_value


CONVENTIONS = 'dated-return-ledger-v1'


class ReturnError(ValueError):
    """Accounting input error with a field suitable for an API error."""
    def __init__(self, field, message):
        self.field = field
        super().__init__(message)


@dataclass(frozen=True)
class YieldPoint:
    date: date
    ytm: float


@dataclass(frozen=True)
class BondHolding:
    """A face-dollar position purchased at the common start, with no leverage.

    Yields are annual nominal decimals at the bond's coupon frequency. The first
    point must be the opening date. Optional sale_date is after start and before
    maturity; a sale on a coupon date is after the seller receives that coupon.
    """
    label: str
    face_value: float
    coupon_rate: float
    issue_date: date
    maturity_date: date
    yields: Tuple[YieldPoint, ...]
    frequency: int = 2
    sale_date: Optional[date] = None


@dataclass(frozen=True)
class LedgerEvent:
    sequence: int
    date: date
    event: str
    position: Optional[str]
    cash_change: float
    face_change: float
    cash_balance: float
    face_balance: Optional[float]
    dirty_price_per_100: Optional[float] = None
    bond_value: Optional[float] = None
    wealth: Optional[float] = None


@dataclass(frozen=True)
class ValuationPoint:
    date: date
    days: int
    clean_value: float
    accrued_interest: float
    bond_value: float
    cash: float
    wealth: float
    faces: dict


@dataclass(frozen=True)
class ReturnResult:
    conventions: str
    beginning_wealth: float
    ending_wealth: float
    net_profit: float
    total_return: float
    purchase_clean: float
    purchase_accrued: float
    purchase_dirty: float
    clean_price_change: float
    accrual_change: float
    dirty_price_change: float
    coupons: float
    cash_interest: float
    purchase_fees: float
    sale_fees: float
    total_fees: float
    ending_cash: float
    ending_bond_value: float
    reconciliation_residual: float
    cash_residual: float
    positions: list
    ledger: list
    path: list


def holding_period_ledger(*, holdings: Sequence[BondHolding], start_date: date,
                          end_date: date, cash_rate: float = 0,
                          cost_bp: float = 0, end_treatment: str = 'liquidate',
                          valuation_dates: Sequence[date] = ()) -> ReturnResult:
    """Reconcile one or more bonds bought at start in a closed USD portfolio.

    Beginning wealth is dirty purchase cost plus entry fees. Costs are one-way
    basis points of face dollars, on purchases and sales only; redemption and
    marks incur no fee. Cash earns an explicit annual effective rate with
    Actual/365 Fixed compounding, including after sale/redemption. New receipts
    earn from their payment date, with no interest credited for that same day.
    There are no external flows after opening, taxes, bond reinvestment, holiday
    adjustments, ex-coupon rules, or trade/settlement lag. 'mark' retains surviving
    positions; 'liquidate' sells them after horizon-date coupons. All intervening
    coupons and redemption are processed regardless of valuation_dates.
    """
    if type(start_date) is not date:
        raise ReturnError('start_date', 'Choose a valid purchase settlement date.')
    if type(end_date) is not date or end_date <= start_date:
        raise ReturnError('end_date', 'The horizon must be after purchase settlement.')
    if (end_date - start_date).days > 366 * 50:
        raise ReturnError('end_date', 'Use a holding period of at most 50 years.')
    if end_treatment not in ('mark', 'liquidate'):
        raise ReturnError('end_treatment', 'Choose mark or liquidate.')
    cash_rate = finite_real('cash_rate', cash_rate)
    cost_bp = finite_real('cost_bp', cost_bp)
    if cash_rate <= -1:
        raise ReturnError('cash_rate', 'An annual effective cash rate must exceed -100%.')
    if cost_bp < 0:
        raise ReturnError('cost_bp', 'Transaction costs cannot be negative.')
    if not holdings or len(holdings) > 20:
        raise ReturnError('holdings', 'Provide between one and twenty positions.')
    labels = [h.label for h in holdings]
    if any(not isinstance(label, str) or not label.strip() or len(label) > 40 for label in labels):
        raise ReturnError('label', 'Use a nonempty position label of at most 40 characters.')
    if len(set(labels)) != len(labels):
        raise ReturnError('label', 'Each position needs a unique label.')

    schedules, initial, faces = {}, {}, {}
    dates = {start_date, end_date}
    for when in valuation_dates:
        if type(when) is not date or not start_date <= when <= end_date:
            raise ReturnError('valuation_dates', 'Valuation dates must lie inside the holding period.')
        dates.add(when)

    def value(holding, when):
        # Validation guarantees a start-date point, so this is never a future fill.
        ytm = next(point.ytm for point in reversed(holding.yields) if point.date <= when)
        return settled_bond_valuation(face_value=holding.face_value, coupon_rate=holding.coupon_rate,
            ytm=ytm, issue_date=holding.issue_date, maturity_date=holding.maturity_date,
            settlement_date=when, frequency=holding.frequency)

    for h in holdings:
        positive_face_value(h.face_value)
        schedule = coupon_schedule(issue_date=h.issue_date, maturity_date=h.maturity_date,
                                   frequency=h.frequency)
        if not h.issue_date <= start_date < h.maturity_date:
            raise ReturnError('start_date', 'Purchase must be on or after issue and before every maturity.')
        if not h.yields or h.yields[0].date != start_date:
            raise ReturnError('yields', 'Each yield path must start on the purchase date.')
        previous = None
        for point in h.yields:
            if (type(point.date) is not date or not start_date <= point.date <= end_date
                    or (previous is not None and point.date <= previous)):
                raise ReturnError('yields', 'Yield dates must be unique, increasing, and inside the holding period.')
            if finite_real('ytm', point.ytm) <= -h.frequency:
                raise ReturnError('ytm', 'Nominal YTM must exceed minus the payment frequency.')
            previous = point.date
            dates.add(point.date)
        if h.sale_date is not None:
            if type(h.sale_date) is not date or not start_date < h.sale_date <= end_date or h.sale_date >= h.maturity_date:
                raise ReturnError('sale_date', 'Sale must be after purchase, no later than the horizon, and before maturity.')
            dates.add(h.sale_date)
        stop = min(end_date, h.sale_date or end_date)
        schedules[h.label] = set(day for day in schedule[1:] if start_date < day <= stop)
        dates.update(schedules[h.label])
        initial[h.label] = value(h, start_date)
        faces[h.label] = 0.0

    purchase_dirty = fsum(v.dirty_price for v in initial.values())
    purchase_clean = fsum(v.clean_price for v in initial.values())
    purchase_accrued = fsum(v.accrued_interest for v in initial.values())
    purchase_fees = fsum(h.face_value * cost_bp / 10000 for h in holdings)
    beginning = fsum([purchase_dirty, purchase_fees])
    if not isfinite(beginning) or beginning <= 0:
        raise ReturnError('holdings', 'Purchase inputs exceed accounting precision.')
    cash = beginning
    ledger, path, coupon_amounts, interest_amounts, exit_fees = [], [], [], [], []
    exits = {}

    def event(when, kind, holding=None, cash_change=0.0, face_change=0.0,
              dirty_price=None, bond_value=None, wealth=None):
        nonlocal cash
        cash = fsum([cash, cash_change])
        if not isfinite(cash):
            raise ReturnError('cash_rate', 'Inputs exceed cash-account numerical precision.')
        if cash < -beginning * 1e-12:
            raise ReturnError('cost_bp', 'Trading costs exceed available cash; borrowing is not supported.')
        if holding is not None:
            faces[holding.label] += face_change
        ledger.append(LedgerEvent(len(ledger) + 1, when, kind,
            holding.label if holding else None, cash_change, face_change, cash,
            faces[holding.label] if holding else None, dirty_price, bond_value, wealth))

    event(start_date, 'opening')
    for h in holdings:
        v = initial[h.label]
        event(start_date, 'purchase', h, -v.dirty_price, h.face_value,
              v.dirty_price / h.face_value * 100)
        if cost_bp:
            event(start_date, 'purchase_fee', h, -h.face_value * cost_bp / 10000)

    previous = start_date
    for when in sorted(dates):
        if when > previous and cash != 0 and cash_rate != 0:
            try:
                interest = cash * expm1(log1p(cash_rate) * (when - previous).days / 365)
            except OverflowError as exc:
                raise ReturnError('cash_rate', 'Cash growth exceeds numerical precision.') from exc
            event(when, 'cash_interest', cash_change=interest)
            interest_amounts.append(interest)
        for h in holdings:
            if not faces[h.label]:
                continue
            if when in schedules[h.label]:
                coupon = h.face_value * h.coupon_rate / h.frequency
                if coupon:
                    event(when, 'coupon', h, coupon)
                    coupon_amounts.append(coupon)
        for h in holdings:
            if faces[h.label] and when == h.maturity_date:
                event(when, 'redemption', h, h.face_value, -h.face_value, 100.0)
                exits[h.label] = dict(status='redeemed', date=when, clean=h.face_value,
                                     accrued=0.0, dirty=h.face_value)
        for h in holdings:
            if faces[h.label] and (when == h.sale_date or (when == end_date and end_treatment == 'liquidate')):
                v = value(h, when)
                event(when, 'sale', h, v.dirty_price, -h.face_value, v.dirty_price / h.face_value * 100)
                fee = h.face_value * cost_bp / 10000
                if fee:
                    event(when, 'sale_fee', h, -fee)
                    exit_fees.append(fee)
                exits[h.label] = dict(status='sold', date=when, clean=v.clean_price,
                                     accrued=v.accrued_interest, dirty=v.dirty_price)
        values = [value(h, when) for h in holdings if faces[h.label]]
        clean = fsum(v.clean_price for v in values)
        accrued = fsum(v.accrued_interest for v in values)
        bond_value = fsum(v.dirty_price for v in values)
        wealth = fsum([bond_value, cash])
        if not isfinite(wealth):
            raise ReturnError('ytm', 'Inputs exceed wealth numerical precision.')
        event(when, 'valuation', bond_value=bond_value, wealth=wealth)
        path.append(ValuationPoint(when, (when - start_date).days, clean, accrued,
                                   bond_value, cash, wealth, dict(faces)))
        previous = when

    for h in holdings:
        if faces[h.label]:
            v = value(h, end_date)
            exits[h.label] = dict(status='held', date=end_date, clean=v.clean_price,
                                 accrued=v.accrued_interest, dirty=v.dirty_price)
    clean_change = fsum(e['clean'] for e in exits.values()) - purchase_clean
    accrual_change = fsum(e['accrued'] for e in exits.values()) - purchase_accrued
    coupons, interest, sale_fees = map(fsum, [coupon_amounts, interest_amounts, exit_fees])
    fees = fsum([purchase_fees, sale_fees])
    profit = fsum([clean_change, accrual_change, coupons, interest, -fees])
    ending = path[-1].wealth
    return ReturnResult(CONVENTIONS, beginning, ending, ending - beginning,
        ending / beginning - 1, purchase_clean, purchase_accrued, purchase_dirty,
        clean_change, accrual_change, clean_change + accrual_change, coupons,
        interest, purchase_fees, sale_fees, fees, cash, path[-1].bond_value,
        ending - beginning - profit,
        cash - fsum([beginning] + [row.cash_change for row in ledger]),
        [dict(label=h.label, face_value=h.face_value, ending_face=faces[h.label],
              purchase_clean=initial[h.label].clean_price,
              purchase_accrued=initial[h.label].accrued_interest,
              purchase_dirty=initial[h.label].dirty_price, **exits[h.label]) for h in holdings],
        ledger, path)
