"""Independent cash arithmetic and event/position conservation for M2."""
from dataclasses import replace
from datetime import date, timedelta

import pytest

from filab.analytics import BondHolding, YieldPoint, holding_period_ledger
from filab.pricing import settled_bond_valuation
from filab.pricing import settled_yield_to_maturity

START = date(2025, 11, 15)
END = date(2027, 11, 15)


def annual(**changes):
    h = BondHolding('A', 100, .04, START, END, (YieldPoint(START, .05),), 1)
    return replace(h, **changes)


def calculate(holdings=None, **changes):
    args = dict(holdings=holdings or [annual()], start_date=START, end_date=END)
    args.update(changes)
    return holding_period_ledger(**args)


def test_two_period_example_independent_of_pricer_and_ledger():
    price = 4 / 1.05 + 104 / 1.05 ** 2
    zero, reinvested = calculate(), calculate(cash_rate=.05)
    assert zero.beginning_wealth == pytest.approx(price, abs=1e-12)
    assert zero.ending_wealth == pytest.approx(108, abs=1e-12)
    assert reinvested.ending_wealth == pytest.approx(4 * 1.05 + 104, abs=1e-12)
    assert reinvested.cash_interest == pytest.approx(.2, abs=1e-12)
    assert reinvested.total_return == pytest.approx(1.05 ** 2 - 1, abs=1e-14)
    assert zero.total_return != pytest.approx(reinvested.total_return)
    assert [e.cash_change for e in zero.ledger if e.event == 'coupon'] == [4, 4]
    assert len([e for e in zero.ledger if e.event == 'redemption']) == 1
    assert not any(e.event == 'sale' for e in zero.ledger)


@pytest.mark.parametrize('cash_nominal,expected',[
    (.04,[.1336,.0778,.0306]),(.05,[.1344,.0787,.0316]),(.06,[.1353,.0797,.0326]),
])
def test_published_ots_total_return_table(cash_nominal,expected):
    # OTS Handbook 540 Appendix A, Table 1, hosted by OCC. Annual compounded
    # horizon returns are printed to 0.01 percentage point. Cash converts the
    # table's semiannual reinvestment rate into our Actual/365 effective account;
    # unequal calendar periods add a small, explicitly documented difference.
    maturity=date(2045,11,15)
    ytm=settled_yield_to_maturity(price=109.90,face_value=100,coupon_rate=.09,
        issue_date=START,maturity_date=maturity,settlement_date=START)
    for end_yield,target in zip([.06,.08,.10],expected):
        horizon=date(2028,11,15)
        h=annual(coupon_rate=.09,maturity_date=maturity,frequency=2,
                 yields=(YieldPoint(START,ytm),YieldPoint(horizon,end_yield)))
        r=calculate([h],end_date=horizon,cash_rate=(1+cash_nominal/2)**2-1)
        annual_compounded=(r.ending_wealth/r.beginning_wealth)**(1/3)-1
        assert annual_compounded==pytest.approx(target,abs=.00005)


def test_coupon_date_opening_after_payment_gets_no_opening_coupon():
    h = annual(issue_date=date(2024, 11, 15))
    r = calculate([h])
    assert all(e.date > START for e in r.ledger if e.event == 'coupon')
    assert r.coupons == 8
    assert r.purchase_accrued == 0


@pytest.mark.parametrize('end_treatment', ['mark', 'liquidate'])
def test_buy_before_coupon_receive_payment_before_sale_or_mark(end_treatment):
    start, end = date(2026, 11, 14), date(2026, 11, 15)
    h = annual(yields=(YieldPoint(start, .05),))
    r = calculate([h], start_date=start, end_date=end, end_treatment=end_treatment, cost_bp=10)
    events = [e.event for e in r.ledger if e.date == end]
    assert events[0] == 'coupon'
    assert r.coupons == 4
    assert r.purchase_accrued == pytest.approx(4 * 364 / 365)
    # The full coupon is a receipt; the accrued amount was paid to the seller.
    assert r.accrual_change == pytest.approx(-4 * 364 / 365)
    assert r.sale_fees == (0 if end_treatment == 'mark' else .1)
    assert r.positions[0]['ending_face'] == (100 if end_treatment == 'mark' else 0)
    if end_treatment == 'liquidate':
        assert events == ['coupon', 'sale', 'sale_fee', 'valuation']


def test_fees_charged_once_and_redemption_has_no_sale_fee():
    redeemed = calculate(cost_bp=10)
    price = 4 / 1.05 + 104 / 1.05 ** 2
    assert redeemed.beginning_wealth == pytest.approx(price + .1)
    assert redeemed.ending_wealth == pytest.approx(108)
    assert redeemed.total_fees == pytest.approx(.1)
    assert redeemed.net_profit == pytest.approx(108 - price - .1)
    sold = calculate(end_date=date(2026, 11, 15), cost_bp=10)
    assert sold.total_fees == pytest.approx(.2)
    assert len([e for e in sold.ledger if e.event.endswith('_fee')]) == 2
    marked = calculate(end_date=date(2026, 11, 15), cost_bp=10, end_treatment='mark')
    assert marked.ending_wealth - sold.ending_wealth == pytest.approx(.1)


def test_early_sale_stops_payments_and_sale_cash_grows_until_horizon():
    sale = date(2026, 11, 15)
    r = calculate([annual(sale_date=sale)], cash_rate=.05)
    sale_price = 104 / 1.05
    assert r.coupons == 4
    assert r.ending_wealth == pytest.approx((4 + sale_price) * 1.05, abs=1e-11)
    assert r.positions[0]['status'] == 'sold'
    assert not any(e.event in ('coupon', 'redemption', 'sale') and e.date > sale for e in r.ledger)


def test_cash_after_maturity_is_not_redeemed_twice_and_earns_interest():
    r = calculate(end_date=date(2028, 11, 14), cash_rate=.05)
    assert r.ending_wealth == pytest.approx(108.2 * 1.05, abs=1e-11)
    assert r.ending_bond_value == 0
    assert sum(e.face_change for e in r.ledger) == 0
    assert sum(e.cash_change for e in r.ledger if e.event == 'redemption') == 100


def test_yield_step_changes_only_marks_from_its_date_not_coupon_amounts():
    shock = date(2026, 5, 15)
    common = dict(end_date=date(2027, 5, 15), end_treatment='mark', valuation_dates=[shock - timedelta(days=1), shock])
    fixed = calculate(**common)
    shocked = calculate([annual(yields=(YieldPoint(START,.05), YieldPoint(shock,.10)))], **common)
    assert fixed.coupons == shocked.coupons == 4
    assert fixed.path[:2] == shocked.path[:2]
    assert shocked.path[2].bond_value < fixed.path[2].bond_value
    assert fixed.beginning_wealth == shocked.beginning_wealth


def test_report_grid_cannot_create_or_duplicate_payments_or_interest():
    sparse = calculate(cash_rate=.05)
    dense = calculate(cash_rate=.05, valuation_dates=[START + timedelta(days=i) for i in range(731)])
    assert dense.ending_wealth == pytest.approx(sparse.ending_wealth, abs=1e-10)
    assert dense.coupons == sparse.coupons == 8
    assert dense.cash_interest == pytest.approx(sparse.cash_interest, abs=1e-11)
    assert len([e for e in dense.ledger if e.event == 'redemption']) == 1


@pytest.mark.parametrize('cash_rate', [0, .05, -.01])
@pytest.mark.parametrize('end_treatment', ['mark', 'liquidate'])
def test_aggregate_positions_conserve_cash_face_and_add_wealth(cash_rate, end_treatment):
    a, b = annual(), annual(label='B', face_value=200, coupon_rate=.06, maturity_date=date(2028,11,15))
    kwargs = dict(cash_rate=cash_rate, cost_bp=5, end_treatment=end_treatment)
    together, only_a, only_b = calculate([a,b], **kwargs), calculate([a], **kwargs), calculate([b], **kwargs)
    assert together.beginning_wealth == pytest.approx(only_a.beginning_wealth + only_b.beginning_wealth, abs=1e-10)
    assert together.ending_wealth == pytest.approx(only_a.ending_wealth + only_b.ending_wealth, abs=1e-10)
    assert together.total_return == pytest.approx(
        (only_a.total_return * only_a.beginning_wealth + only_b.total_return * only_b.beginning_wealth) / together.beginning_wealth)
    cash = together.beginning_wealth
    faces = {'A':0, 'B':0}
    for e in together.ledger:
        cash += e.cash_change
        assert e.cash_balance == pytest.approx(cash, abs=1e-10)
        if e.position:
            faces[e.position] += e.face_change
            assert e.face_balance == pytest.approx(faces[e.position], abs=1e-12)
            assert e.face_balance >= 0
    final_events=[e.event for e in together.ledger if e.date==END]
    coupon_indices=[i for i,kind in enumerate(final_events) if kind=='coupon']
    assert max(coupon_indices)<final_events.index('redemption')
    if end_treatment=='liquidate':
        assert final_events.index('redemption')<final_events.index('sale')
    assert together.reconciliation_residual == pytest.approx(0, abs=1e-10)
    assert together.cash_residual == pytest.approx(0, abs=1e-10)
    assert together.ending_wealth == pytest.approx(together.ending_cash + together.ending_bond_value)


@pytest.mark.parametrize('frequency',[1,2,4,12])
@pytest.mark.parametrize('ytm',[-.01,0,.05])
def test_frequencies_negative_yields_zero_coupon_and_face_scaling(frequency,ytm):
    h=annual(coupon_rate=0,frequency=frequency,yields=(YieldPoint(START,ytm),))
    r=calculate([h])
    expected=100/(1+ytm/frequency)**(2*frequency)
    assert r.purchase_dirty == pytest.approx(expected,abs=1e-11)
    assert r.ending_wealth == 100
    assert r.coupons == 0
    scaled=calculate([replace(h,face_value=10000)])
    assert scaled.beginning_wealth == pytest.approx(r.beginning_wealth*100)
    assert scaled.total_return == pytest.approx(r.total_return)


def test_fractional_purchase_uses_existing_dated_convention():
    start=date(2026,2,28)
    h=annual(yields=(YieldPoint(start,.05),))
    r=calculate([h],start_date=start)
    expected=settled_bond_valuation(face_value=100,coupon_rate=.04,ytm=.05,
        issue_date=START,maturity_date=END,settlement_date=start,frequency=1)
    assert r.purchase_dirty == expected.dirty_price
    assert r.purchase_accrued == expected.accrued_interest


@pytest.mark.parametrize('changes',[
    {'end_date':START}, {'end_date':date(2024,1,1)}, {'end_treatment':'ignore'},
    {'cash_rate':-1}, {'cash_rate':float('nan')}, {'cost_bp':-1},
    {'valuation_dates':[date(2024,1,1)]}, {'start_date':'2025-11-15'},
])
def test_invalid_accounting_inputs(changes):
    with pytest.raises(ValueError):
        calculate(**changes)


@pytest.mark.parametrize('changes',[
    {'face_value':0}, {'coupon_rate':-.01}, {'frequency':3}, {'label':''},
    {'issue_date':date(2025,11,14)}, {'sale_date':START}, {'sale_date':END},
    {'sale_date':date(2028,1,1)}, {'yields':()},
    {'yields':(YieldPoint(date(2026,11,15),.05),)},
    {'yields':(YieldPoint(START,.05),YieldPoint(START,.06))},
    {'yields':(YieldPoint(START,.05),YieldPoint(date(2028,1,1),.06))},
    {'yields':(YieldPoint(START,-1),)},
])
def test_invalid_positions(changes):
    with pytest.raises(ValueError):
        calculate([annual(**changes)])


def test_duplicate_labels_empty_portfolio_and_insufficient_cash_are_rejected():
    with pytest.raises(ValueError,match='unique'):
        calculate([annual(),annual()])
    with pytest.raises(ValueError,match='one and twenty'):
        holding_period_ledger(holdings=[],start_date=START,end_date=END)
    # The sale cost exceeds the proceeds of this very deeply discounted zero.
    h=annual(coupon_rate=0,yields=(YieldPoint(START,1e5),))
    with pytest.raises(ValueError,match='borrowing'):
        calculate([h],end_date=date(2026,1,1),cost_bp=100)
