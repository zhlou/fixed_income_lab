"""Financial results for a two-bond comparison, independent of HTTP/templates."""
from dataclasses import asdict

from filab.pricing import fixed_coupon_cashflows, price_coupon_bond, settled_bond_valuation
from filab.pricing.settlement import SettlementError
from .duration import bond_risk, numerical_risk, yield_scenarios


CONVENTIONS = 'nominal-yield-risk-v1'


def compare_bonds(*, mode, face_value, ytm, frequency, coupon_rate, maturity_years,
                  comparison_coupon_rate, comparison_maturity_years, issue_date,
                  settlement_date, maturity_date, comparison_maturity_date, shock_bp):
    """Compare regular or dated fixed cash flows at one shared yield and face.

    Dated risk uses a 0.5 bp central bump and dirty-price normalization. The
    convergence table includes 1, 0.5 and 0.25 bp; it is a diagnostic, not proof.
    Regular Macaulay weights use years k/m. Dated tables use coupon periods
    (k+w)/m for labels only, not a claim to textbook Macaulay duration.
    """
    bonds = []
    for index, (coupon, maturity, maturity_day) in enumerate([
        (coupon_rate, maturity_years, maturity_date),
        (comparison_coupon_rate, comparison_maturity_years, comparison_maturity_date),
    ]):
        args = dict(face_value=face_value, coupon_rate=coupon, frequency=frequency)
        try:
            if mode == 'dated':
                args.update(issue_date=issue_date, settlement_date=settlement_date,
                            maturity_date=maturity_day)
                if (maturity_day - issue_date).days > 366 * 50:
                    raise SettlementError('maturity_date', 'Use at most 50 years.')
                value = settled_bond_valuation(ytm=ytm, **args)
                pricer = lambda y: settled_bond_valuation(ytm=y, **args).dirty_price
                risk = numerical_risk(pricer, ytm=ytm, bump=.00005)
                cashflows = [dict(time_years=(k + value.remaining_fraction) / frequency,
                                  date=f.payment_date.isoformat(), amount=f.coupon + f.principal,
                                  present_value=f.present_value, weight=f.present_value / risk.price)
                             for k, f in enumerate(value.cashflows)]
                clean, accrued = value.clean_price, value.accrued_interest
            else:
                args['maturity_years'] = maturity
                risk = bond_risk(ytm=ytm, **args)
                pricer = lambda y: price_coupon_bond(ytm=y, **args)
                cashflows = [dict(time_years=f.time_years, date=None, amount=f.amount,
                                  present_value=f.amount / (1 + ytm / frequency) ** k,
                                  weight=f.amount / (1 + ytm / frequency) ** k / risk.price,
                                  weighted_time=f.time_years * f.amount / (1 + ytm / frequency) ** k / risk.price)
                             for k, f in enumerate(fixed_coupon_cashflows(**args), 1)]
                clean, accrued = risk.price, 0.0
        except ValueError as exc:
            field = getattr(exc, 'field', 'maturity_years' if mode == 'regular' else 'maturity_date')
            if index and field == 'issue_date':
                field = 'comparison_maturity_date'
            elif index and field in ('maturity_years', 'maturity_date', 'coupon_rate'):
                field = 'comparison_' + field
            raise SettlementError(field, str(exc)) from exc
        convergence = [asdict(numerical_risk(pricer, ytm=ytm, bump=bump))
                       for bump in (.0001, .00005, .000025)]
        points = yield_scenarios(pricer, ytm=ytm, risk=risk,
                                shocks=[bp / 10000 for bp in range(-200, 201, 5)])
        shocks = sorted({-200, -100, -50, -25, 0, 25, 50, 100, 200, shock_bp})
        scenarios = yield_scenarios(pricer, ytm=ytm, risk=risk,
                                   shocks=[bp / 10000 for bp in shocks])
        bonds.append(dict(label='Bond A' if index == 0 else 'Bond B', risk=asdict(risk),
                          clean_price=clean, accrued_interest=accrued, cashflows=cashflows,
                          convergence=convergence, points=points, scenarios=scenarios,
                          selected=next(row for row in scenarios if abs(row['shock_bp'] - shock_bp) < 1e-8)))
    return dict(bonds=bonds, conventions=CONVENTIONS, mode=mode,
                normalization='dirty price', shock_bp=shock_bp)
