"""Independent curve identities, source reproduction, and payment ownership."""
from datetime import date
from math import exp

import pytest

from filab.curves import (DiscountCurve, bootstrap, dated_valuation, forward_rate,
                          present_value, spot_rate, synthetic_example)
from filab.pricing import price_coupon_bond
from filab.data.fed import bundled, historical_valuation, normalize, validate_row, reproduction_errors, TOLERANCE


def test_hand_bootstrap_and_aging():
    result = synthetic_example()
    assert result['nodes'][-1][1] == pytest.approx(.9, abs=1e-14)
    assert result['initial_price'] == pytest.approx(97.60, abs=1e-12)
    assert result['remaining_price'] == pytest.approx(99.80, abs=1e-12)
    assert result['cash_received'] == 2
    assert result['price_change'] == pytest.approx(2.20, abs=1e-12)
    assert result['ending_wealth'] == pytest.approx(101.80, abs=1e-12)
    assert result['forward_rate'] == pytest.approx(.0412371134020619, abs=1e-14)
    changed = synthetic_example(100.37, 1)
    assert changed['initial_price'] == pytest.approx(96.58, abs=1e-12)
    assert changed['remaining_price'] == pytest.approx(100.92, abs=1e-12)
    assert changed['cash_received'] == 4
    final = synthetic_example(horizon=2)
    assert final['remaining_price'] == 0 and final['cash_received'] == 108


@pytest.mark.parametrize('yield_rate',[-.01,0,.05])
def test_flat_curve_matches_regular_period_pricer(yield_rate):
    curve = DiscountCurve(tuple((k/2,(1+yield_rate/2)**(-k)) for k in range(5)))
    price = present_value(curve,[(.5,2),(1,2),(1.5,2),(2,102)])
    assert price == pytest.approx(price_coupon_bond(face_value=100,coupon_rate=.04,ytm=yield_rate,maturity_years=2,frequency=2),abs=1e-12)
    assert curve.discount(.75) == pytest.approx((1+yield_rate/2)**(-1.5),abs=1e-14)
    assert exp(-spot_rate(curve,1)*1) == pytest.approx(curve.discount(1),abs=1e-14)
    assert (1+forward_rate(curve,.5,1)*.5)*curve.discount(1) == pytest.approx(curve.discount(.5),abs=1e-14)


@pytest.mark.parametrize('nodes', [((0,.9),(1,.8)),((0,1),(1,0)),((0,1),(1,.9),(1,.8)),((0,1),(-1,1)),((0,1),(1,float('nan')))])
def test_invalid_curves(nodes):
    with pytest.raises(ValueError): DiscountCurve(nodes)


def test_curve_boundaries_and_invalid_calibration():
    curve = DiscountCurve(((0,1),(1,.95)))
    for time in [-1,1.01,float('nan')]:
        with pytest.raises(ValueError): curve.discount(time)
    with pytest.raises(ValueError): forward_rate(curve,1,1)
    with pytest.raises(ValueError): bootstrap([(1,[(1,2),(2,100)])],initial_nodes=curve.nodes)
    with pytest.raises(ValueError): synthetic_example(horizon=.1)


def test_dated_coupon_ownership_and_accrual():
    curve = DiscountCurve(((0,1),(5,.8)))
    args=dict(face_value=100,coupon_rate=.04,issue_date=date(2025,11,15),maturity_date=date(2027,11,15))
    before = dated_valuation(curve,**args,settlement_date=date(2026,5,14))
    after = dated_valuation(curve,**args,settlement_date=date(2026,5,15))
    assert before['cashflows'][0]['payment_date']=='2026-05-15'
    assert after['cashflows'][0]['payment_date']=='2026-11-15'
    assert after['accrued_interest']==0
    assert before['dirty_price']==pytest.approx(before['clean_price']+before['accrued_interest'],abs=1e-12)


def test_fed_source_sample_and_model_transition():
    data = bundled()
    assert len(data['rows'])==6
    assert data['source']['parent_rows']==17058
    for row in data['rows']:
        curve=validate_row(row)
        if row['date']=='1980-01-01':
            assert curve is None
            continue
        assert max(e['error'] for e in reproduction_errors(row,curve))<=TOLERANCE
        if row['date']<'1980': assert curve.parameters[3]==0 and curve.parameters[5] is None
    row=data['rows'][-1]
    assert row['values'][6] == pytest.approx(.043905,abs=1e-15)
    assert validate_row(data['rows'][0]).maximum==7
    assert validate_row(row).maximum==30


@pytest.mark.parametrize('maturity',[2,10])
@pytest.mark.parametrize('age',[0,1])
def test_every_coupon_checked_and_short_end_rejected(maturity,age):
    row=bundled()['rows'][-1]
    result=historical_valuation(row,maturity_years=maturity,age_months=age)
    assert result['dirty_price'] is None
    assert result['status']=='Unsupported payment maturity'
    assert len(result['cashflows'])==maturity*2
    assert any(not f['supported'] for f in result['cashflows'])
    assert all(f['present_value'] is None for f in result['cashflows'] if not f['supported'])
    zero=historical_valuation(row,maturity_years=maturity,age_months=age,coupon_rate=0)
    assert zero['status']=='Supported' and zero['dirty_price']>0


def test_old_long_bond_rejected_and_reconstruction_discrepancy():
    row=bundled()['rows'][0]
    assert historical_valuation(row,maturity_years=10,coupon_rate=0)['dirty_price'] is None
    row=bundled()['rows'][-1]
    row['values'][6]+=.001
    result=historical_valuation(row,coupon_rate=0)
    assert result['status']=='Parameter reconstruction exceeds source rounding'
    assert result['dirty_price'] is None


def test_leap_day_grid_boundary_keeps_historical_curve_accessible():
    # Reuse a model on an explicitly synthetic date to isolate date generation.
    row=bundled()['rows'][-1]
    row['date']='2024-02-28'
    result=historical_valuation(row)
    assert result['dirty_price'] is None
    assert 'Stub coupons are excluded' in result['status']
    assert historical_valuation(row,coupon_rate=0)['dirty_price']>0
