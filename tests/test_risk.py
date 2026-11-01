"""Independent identities, numerical convergence, and dated convention boundaries."""
from datetime import date

import pytest

from filab.pricing import price_coupon_bond, settled_bond_valuation
from filab.risk import bond_risk, dated_bond_risk, numerical_risk, yield_scenarios

BASE = dict(face_value=100, coupon_rate=.04, maturity_years=2, frequency=2)
DATED = dict(face_value=100, coupon_rate=.04, frequency=2,
             issue_date=date(2025, 11, 15), maturity_date=date(2028, 11, 15),
             settlement_date=date(2026, 8, 15))


@pytest.mark.parametrize('frequency', [1, 2, 4, 12])
@pytest.mark.parametrize('ytm', [-.01, 0, .05])
def test_zero_coupon_independent_closed_forms(frequency, ytm):
    maturity = 10
    r = bond_risk(**dict(BASE, frequency=frequency, coupon_rate=0,
                         maturity_years=maturity), ytm=ytm)
    q = 1 + ytm / frequency
    assert r.price == pytest.approx(100 / q ** (maturity * frequency), rel=1e-13)
    assert r.macaulay_duration == pytest.approx(maturity, abs=1e-12)
    assert r.modified_duration == pytest.approx(maturity / q, rel=1e-13)
    assert r.convexity == pytest.approx(maturity * (maturity + 1 / frequency) / q ** 2, rel=1e-13)
    assert r.dv01 == pytest.approx(r.price * maturity / q / 10000, rel=1e-13)


def test_two_payment_hand_calculation_and_coupon_timing():
    # Annual 10% coupon, two years, zero yield: PV weights are exactly 10/120, 110/120.
    r = bond_risk(face_value=100, coupon_rate=.1, maturity_years=2, frequency=1, ytm=0)
    assert r.price == 120
    assert r.macaulay_duration == pytest.approx(23 / 12)
    assert r.modified_duration == pytest.approx(23 / 12)
    assert r.convexity == pytest.approx((2 * 10 + 6 * 110) / 120)
    one = bond_risk(face_value=100, coupon_rate=.1, maturity_years=1, frequency=1, ytm=.05)
    assert one.macaulay_duration == pytest.approx(1)  # Coupon and principal arrive together.


@pytest.mark.parametrize('coupon', [0, .04, .12])
@pytest.mark.parametrize('frequency', [1, 2, 4, 12])
@pytest.mark.parametrize('ytm', [-.01, 0, .05])
def test_analytical_matches_numerical(coupon, frequency, ytm):
    args = dict(BASE, coupon_rate=coupon, frequency=frequency, maturity_years=10)
    exact = bond_risk(ytm=ytm, **args)
    numeric = numerical_risk(lambda y: price_coupon_bond(ytm=y, **args), ytm=ytm, bump=.00005)
    # Central truncation is O(h²); second difference also has floating cancellation.
    assert numeric.modified_duration == pytest.approx(exact.modified_duration, rel=1e-7)
    assert numeric.convexity == pytest.approx(exact.convexity, rel=3e-7)


def test_bump_convergence_before_roundoff():
    args = dict(BASE, maturity_years=10)
    exact = bond_risk(ytm=.05, **args)
    numeric = [numerical_risk(lambda y: price_coupon_bond(ytm=y, **args), ytm=.05, bump=h)
               for h in (.01, .005, .0025)]
    for key in ('modified_duration', 'convexity'):
        errors = [abs(getattr(r, key) - getattr(exact, key)) for r in numeric]
        assert errors[0] > errors[1] > errors[2]
        assert errors[1] / errors[0] == pytest.approx(.25, abs=.005)


def test_face_scaling_and_coupon_effect():
    a = bond_risk(**BASE, ytm=.05)
    b = bond_risk(**dict(BASE, face_value=100000), ytm=.05)
    for key in ('macaulay_duration', 'modified_duration', 'convexity'):
        assert getattr(b, key) == pytest.approx(getattr(a, key))
    for key in ('price', 'dollar_duration', 'dv01'):
        assert getattr(b, key) == pytest.approx(1000 * getattr(a, key))
    high = bond_risk(**dict(BASE, coupon_rate=.1), ytm=.05)
    assert high.macaulay_duration < a.macaulay_duration < 2


def test_cme_printed_price_bump_example():
    # CME DV01 note, Exhibit 2: rounded observed prices at 3.78%, 3.79%, 3.80%.
    # Tests bump arithmetic only; missing settlement details prevent pricer replication.
    prices = {.0378: 108661.41, .0379: 108593.75, .0380: 108526.14}
    r = numerical_risk(lambda y: prices[round(y, 4)], ytm=.0379)
    assert r.dv01 == pytest.approx(67.64, abs=.0051)  # Printed cents and tie rounding.
    assert r.modified_duration == pytest.approx(6.23, abs=.005)


@pytest.mark.parametrize('settlement', [date(2026, 11, 14), date(2026, 11, 15), date(2026, 11, 16)])
def test_dated_coupon_boundary_dirty_and_clean_dollar_sensitivity(settlement):
    args = dict(DATED, settlement_date=settlement)
    r = dated_bond_risk(ytm=.05, bump=.00005, **args)
    clean = numerical_risk(lambda y: settled_bond_valuation(ytm=y, **args).clean_price,
                           ytm=.05, bump=.00005)
    assert r.macaulay_duration is None
    assert r.dv01 == pytest.approx(clean.dv01, rel=1e-9)
    if settlement == date(2026, 11, 15):
        regular = bond_risk(**BASE, ytm=.05)
        assert r.price == pytest.approx(regular.price)
        assert r.modified_duration == pytest.approx(regular.modified_duration, rel=1e-8)
        assert r.convexity == pytest.approx(regular.convexity, rel=3e-7)


@pytest.mark.parametrize('settlement', [date(2028, 5, 15), date(2028, 8, 15), date(2028, 11, 14)])
def test_dated_final_payment_simple_period_derivatives(settlement):
    args = dict(DATED, settlement_date=settlement)
    r = dated_bond_risk(ytm=.05, bump=.001, **args)
    w = (date(2028, 11, 15) - settlement).days / 184
    denom = 1 + .05 * w / 2
    assert r.price == pytest.approx(102 / denom)
    assert r.modified_duration == pytest.approx((w / 2) / denom, rel=3e-7)
    assert r.convexity == pytest.approx(2 * (w / 2 / denom) ** 2, rel=3e-5)


def test_zero_shock_sign_symmetry_and_taylor_error():
    args = dict(BASE, maturity_years=10)
    r = bond_risk(ytm=.05, **args)
    rows = yield_scenarios(lambda y: price_coupon_bond(ytm=y, **args), ytm=.05,
                          risk=r, shocks=[-.02, -.01, 0, .01, .02])
    zero = rows[2]
    assert zero['exact_change'] == zero['duration_change'] == zero['convexity_change'] == 0
    assert rows[0]['exact_change'] > abs(rows[-1]['exact_change'])
    for row in rows:
        assert row['exact_percent'] == pytest.approx(row['exact_change'] / r.price)
        assert row['duration_error'] == pytest.approx(row['duration_change'] - row['exact_change'])
        assert row['convexity_error_percent'] == pytest.approx(row['convexity_error'] / r.price)
        assert abs(row['convexity_error']) <= abs(row['duration_error'])
    assert abs(rows[3]['convexity_error']) < abs(rows[4]['convexity_error'])


@pytest.mark.parametrize('changes', [{'face_value':0}, {'coupon_rate':-.01}, {'ytm':-2},
    {'ytm':float('nan')}, {'maturity_years':0}, {'maturity_years':1.2}, {'frequency':True}])
def test_invalid_regular_risk(changes):
    with pytest.raises(ValueError):
        bond_risk(**{**BASE, "ytm": .05, **changes})


@pytest.mark.parametrize('bump', [0, -.01, float('nan'), True, 1e-100])
def test_invalid_numerical_bumps(bump):
    with pytest.raises(ValueError):
        numerical_risk(lambda y:100, ytm=.05, bump=bump)


def test_nonpositive_prices_fail_explicitly():
    with pytest.raises(ValueError):
        numerical_risk(lambda y:0, ytm=.05)
