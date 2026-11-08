"""Cash-flow valuation with explicit discount curves, independent of HTTP."""
from bisect import bisect_left
from dataclasses import dataclass
from math import exp, fsum, isfinite, log

from filab.pricing import fixed_coupon_cashflows, coupon_schedule
from filab.pricing.settlement import accrued_interest
from filab.pricing._validation import finite_real as number


@dataclass(frozen=True)
class DiscountCurve:
    """Positive nodes including (0, 1), log-linear interpolation, no extrapolation."""
    nodes: tuple

    def __post_init__(self):
        nodes = tuple((number('maturity', t), number('discount_factor', d)) for t, d in self.nodes)
        if len(nodes) < 2 or nodes[0] != (0, 1):
            raise ValueError('Start the curve at D(0) = 1 and supply a later node.')
        if any(d <= 0 for _, d in nodes) or any(b[0] <= a[0] for a, b in zip(nodes, nodes[1:])):
            raise ValueError('Factors must be positive and maturities strictly increasing.')
        object.__setattr__(self, 'nodes', nodes)

    def discount(self, time):
        time = number('time_years', time)
        if not 0 <= time <= self.nodes[-1][0]:
            raise ValueError('Payment lies outside the supported curve maturities.')
        i = bisect_left([t for t, _ in self.nodes], time)
        if self.nodes[i][0] == time:
            return self.nodes[i][1]
        left, right = self.nodes[i - 1], self.nodes[i]
        weight = (time - left[0]) / (right[0] - left[0])
        return exp((1 - weight) * log(left[1]) + weight * log(right[1]))


def spot_rate(curve, time):
    """Annual continuously compounded spot rate, decimal."""
    time = number('time_years', time)
    if time <= 0:
        raise ValueError('Spot maturity must be positive.')
    return -log(curve.discount(time)) / time


def forward_rate(curve, start, end):
    """Annual simple forward over the stated interval, decimal."""
    start, end = number('start', start), number('end', end)
    if start < 0 or end <= start:
        raise ValueError('Forward end must follow its nonnegative start.')
    return (curve.discount(start) / curve.discount(end) - 1) / (end - start)


def present_value(curve, payments):
    """Value (time_years, amount) payments in matching face units."""
    return fsum(number('amount', amount) * curve.discount(time) for time, amount in payments if amount != 0)


def bootstrap(instruments, initial_nodes=((0, 1),)):
    """Recover one final factor per instrument from already known earlier payments.

    Each instrument is (price, [(time, amount), ...]). Earlier payments must be
    within the existing curve. Prices are full-precision dirty dollar prices.
    """
    nodes = list(initial_nodes)
    for price, payments in instruments:
        price = number('price', price)
        flows = [(number('maturity', t), number('amount', a)) for t, a in payments]
        if not flows or any(a < 0 for _, a in flows) or flows[-1][1] <= 0:
            raise ValueError('Calibration requires nonnegative payments and a positive final payment.')
        maturity, final = flows[-1]
        if any(b[0] <= a[0] for a, b in zip(flows, flows[1:])) or maturity <= nodes[-1][0]:
            raise ValueError('Calibration payments and final maturities must increase.')
        curve = DiscountCurve(tuple(nodes)) if len(nodes) > 1 else None
        prior = present_value(curve, flows[:-1]) if flows[:-1] and curve else 0
        if flows[:-1] and curve is None:
            raise ValueError('Earlier calibration payments require known discount factors.')
        factor = (price - prior) / final
        if not isfinite(factor) or factor <= 0:
            raise ValueError('Calibration price implies a nonpositive discount factor.')
        nodes.append((maturity, factor))
    return DiscountCurve(tuple(nodes))


def dated_payments(*, face_value, coupon_rate, issue_date, maturity_date, settlement_date, frequency=2):
    """Regular cash flows after payment on settlement day; Lab time basis ACT/365F.

    Accrued interest retains Actual/Actual coupon-period accrual. Curve time is
    elapsed calendar days / 365, independently of the existing dated YTM pricer.
    """
    accrued = accrued_interest(face_value=face_value, coupon_rate=coupon_rate,
        issue_date=issue_date, maturity_date=maturity_date, settlement_date=settlement_date, frequency=frequency)
    schedule = coupon_schedule(issue_date=issue_date, maturity_date=maturity_date, frequency=frequency)
    coupon = face_value * coupon_rate / frequency
    flows = [dict(payment_date=d.isoformat(), time_years=(d - settlement_date).days / 365,
                  amount=coupon + (face_value if d == maturity_date else 0))
             for d in schedule if d > settlement_date]
    return flows, accrued


def dated_valuation(curve, **bond):
    """Dirty curve PV and clean quote using the existing coupon accrual convention."""
    flows, accrued = dated_payments(**bond)
    for flow in flows:
        flow['discount_factor'] = curve.discount(flow['time_years']) if flow['amount'] else None
        flow['present_value'] = flow['amount'] * flow['discount_factor'] if flow['amount'] else 0
    dirty = fsum(f['present_value'] for f in flows)
    return dict(dirty_price=dirty, accrued_interest=accrued, clean_price=dirty - accrued, cashflows=flows)


def synthetic_example(calibration_price=101.40, horizon=0.5):
    """The two-year $100-face 4% note; time is exact regular coupon years."""
    calibration_price, horizon = number('calibration_price', calibration_price), number('horizon', horizon)
    if horizon not in (0, 0.5, 1, 1.5, 2):
        raise ValueError('Choose a half-year horizon from zero to two years.')
    calibration = fixed_coupon_cashflows(face_value=100, coupon_rate=0.06, maturity_years=2)
    curve = bootstrap([(calibration_price, [(f.time_years, f.amount) for f in calibration])],
                      initial_nodes=((0, 1), (0.5, .99), (1, .97), (1.5, .94)))
    payments = fixed_coupon_cashflows(face_value=100, coupon_rate=.04, maturity_years=2)
    flows = [dict(time_years=f.time_years - horizon, original_time=f.time_years, amount=f.amount,
                  discount_factor=curve.discount(f.time_years - horizon),
                  present_value=f.amount * curve.discount(f.time_years - horizon))
             for f in payments if f.time_years > horizon]
    initial = present_value(curve, [(f.time_years, f.amount) for f in payments])
    ending = fsum(f['present_value'] for f in flows)
    cash = fsum(f.amount for f in payments if f.time_years <= horizon)
    return dict(nodes=curve.nodes, initial_price=initial, remaining_price=ending, cash_received=cash,
                price_change=ending-initial, ending_wealth=ending+cash,
                forward_rate=forward_rate(curve, .5, 1), cashflows=flows,
                calibration_price=calibration_price, horizon=horizon)
