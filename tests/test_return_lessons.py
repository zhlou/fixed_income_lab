"""Teaching boundaries, independent examples, and full-calculator parity."""
import pytest

pytest.importorskip('fastapi')
from fastapi.testclient import TestClient
from filab.web.app import app
from filab.web.curriculum import LESSONS
from filab.web.return_lessons import RETURN_LESSONS, lesson_spec

client = TestClient(app)


def calculate(slug, controls=None, example=None):
    return client.post('/api/lesson-returns/'+slug,json=dict(
        example=example or RETURN_LESSONS[slug]['default_example'],controls=controls or {}))


@pytest.mark.parametrize('slug,wealth',[
    ('holding-period-returns',97.79754452862954),('coupons-and-return',100.13223648263877),
    ('reinvestment-and-cash',108.2),('pull-to-par',108),
])
def test_lesson_defaults_match_established_worked_cases_and_full_calculator(slug,wealth):
    response=calculate(slug)
    assert response.status_code==200
    data=response.json()
    assert data['result']['ending_wealth']==pytest.approx(wealth,abs=1e-10)
    assert data['result']==client.post('/api/returns',json=data['inputs']).json()['result']
    assert data['inputs']['face_value']==100
    assert data['inputs']['include_comparison'] is False
    assert data['result']['reconciliation_residual']==pytest.approx(0,abs=1e-10)
    assert len(data['focus']['metrics'])==3


@pytest.mark.parametrize('slug',list(RETURN_LESSONS))
def test_lessons_reject_unrelated_controls_and_scenarios(slug):
    response=calculate(slug,{'include_comparison':True})
    assert response.status_code==422
    assert response.json()['detail'][0]['loc'][-1]=='include_comparison'
    assert calculate(slug,example='unrelated-calculator-example').status_code==422


def test_unknown_lesson_is_not_found():
    assert calculate('missing',example='none').status_code==404


def test_m2_prerequisites_precede_the_lessons_that_use_them():
    positions = {lesson['slug']: index for index, lesson in enumerate(LESSONS)}
    for lesson in LESSONS:
        if lesson['milestone'] == 'M2':
            assert positions[lesson['prerequisite']] < positions[lesson['slug']]


@pytest.mark.parametrize('example',['discount-bond','premium-bond'])
@pytest.mark.parametrize('horizon',['maturity','before_maturity'])
def test_visible_pull_to_par_scenarios_keep_yield_fixed(example,horizon):
    spec = lesson_spec('pull-to-par')
    assert [e['id'] for e in spec['examples']] == ['discount-bond','premium-bond']
    assert {f['name'] for f in spec['controls']} == {'coupon_rate','start_yield','horizon'}
    horizons = next(f for f in spec['controls'] if f['name']=='horizon')['options']
    assert [option[0] for option in horizons] == ['maturity','before_maturity']
    data = calculate('pull-to-par',{'horizon':horizon},example=example).json()
    assert data['inputs']['yield_path'] == 'fixed'
    assert data['result']['sale_fees'] == 0
    assert data['result']['cash_interest'] == 0
    assert data['result']['positions'][0]['status'] == ('redeemed' if horizon=='maturity' else 'held')


def test_return_lesson_distinguishes_price_return_and_coupon_inclusive_return():
    data=calculate('holding-period-returns').json()
    price=2/1.025+2/1.025**2+2/1.025**3+102/1.025**4
    sale=2/1.035+2/1.035**2+102/1.035**3
    curves=data['focus']['plot']['curves']
    assert curves[0]['points'][-1]['y']==pytest.approx((sale+2)/price-1,abs=1e-13)
    assert curves[1]['points'][-1]['y']==pytest.approx(sale/price-1,abs=1e-13)
    # Liquidation zeroes the position, not the price comparator used by the plot.
    assert data['result']['ending_bond_value']==0
    assert curves[1]['points'][-1]['y'] > -.03
    assert data['focus']['plot']['percent_y'] is True


def test_entry_and_exit_costs_match_the_price_return_bases():
    sold=calculate('holding-period-returns',{'cost_bp':10}).json()
    marked=calculate('holding-period-returns',{'cost_bp':10,'end_treatment':'mark'}).json()
    r=sold['result'];curve=sold['focus']['plot']['curves'][0]['points']
    assert curve[0]['y']==pytest.approx(-.1/r['beginning_wealth'],abs=1e-13)
    assert curve[-1]['y']==pytest.approx(r['total_return'],abs=1e-13)
    assert sold['focus']['plot']['curves'][1]['points'][0]['y']==pytest.approx(0,abs=1e-14)
    assert marked['result']['ending_wealth']-r['ending_wealth']==pytest.approx(.1,abs=1e-12)
    assert sold['focus']['plot']['curves'][1]==marked['focus']['plot']['curves'][1]


def test_coupon_lesson_keeps_a_mark_and_respects_opening_coupon_eligibility():
    before=calculate('coupons-and-return').json()
    on_date=calculate('coupons-and-return',example='coupon-date-purchase').json()
    assert before['result']['coupons']==2
    assert before['result']['purchase_accrued']==pytest.approx(2*183/184,abs=1e-12)
    assert before['result']['ending_bond_value']>98
    assert before['result']['positions'][0]['ending_face']==100
    assert on_date['result']['coupons']==0
    assert on_date['result']['purchase_accrued']==0
    assert before['focus']['plot']['reference_x']==1
    assert on_date['focus']['plot']['reference_x']==0
    assert before['result']['ending_wealth']==pytest.approx(100.13223648263877,abs=1e-10)


@pytest.mark.parametrize('controls,field',[
    ({'start_date':'2026-10-31'},'start_date'),({'end_date':'2026-12-01'},'end_date'),
    ({'end_date':'2026-11-14'},'end_date'),({'coupon_rate':.09},'coupon_rate'),
])
def test_coupon_lesson_stays_in_the_teaching_window(controls,field):
    response=calculate('coupons-and-return',controls)
    assert response.status_code==422
    assert response.json()['detail'][0]['loc'][-1]==field


def test_cash_lesson_isolates_extra_wealth_with_the_independent_two_period_example():
    data=calculate('reinvestment-and-cash').json()
    r=data['result']
    assert r['purchase_dirty']==pytest.approx(4/1.05+104/1.05**2,abs=1e-12)
    assert r['ending_wealth']==pytest.approx(4*1.05+104,abs=1e-10)
    assert data['focus']['plot']['curves'][0]['points'][-1]['y']==pytest.approx(.2,abs=1e-10)
    assert all(p['y']==0 for p in data['focus']['plot']['curves'][1]['points'])
    assert data['focus']['rows'][0][2]==pytest.approx(108)
    assert data['focus']['rows'][1][2]==pytest.approx(108.2)
    zero=calculate('reinvestment-and-cash',example='zero-cash').json()
    assert all(p['y']==pytest.approx(0,abs=1e-12) for p in zero['focus']['plot']['curves'][0]['points'])


def test_cash_horizons_do_not_credit_interest_before_a_receipt():
    first=calculate('reinvestment-and-cash',{'horizon':'first_coupon'}).json()
    assert first['result']['cash_interest']==0
    assert all(p['y']==pytest.approx(0,abs=1e-12) for p in first['focus']['plot']['curves'][0]['points'])
    no_coupon=calculate('reinvestment-and-cash',{'coupon_rate':0}).json()
    assert no_coupon['result']['cash_interest']==0
    after=calculate('reinvestment-and-cash',{'coupon_rate':0,'horizon':'after_maturity'}).json()
    assert after['result']['ending_wealth']==pytest.approx(100*1.05,abs=1e-10)
    assert after['result']['cash_interest']==pytest.approx(5,abs=1e-10)


def test_pull_to_par_distinguishes_discount_premium_and_redemption_from_price():
    discount=calculate('pull-to-par').json()
    premium=calculate('pull-to-par',example='premium-bond').json()
    assert discount['result']['purchase_clean']<100
    assert premium['result']['purchase_clean']>100
    for data in [discount,premium]:
        r=data['result'];plot=data['focus']['plot']
        assert r['ending_bond_value']==0
        assert r['positions'][0]['status']=='redeemed'
        assert r['positions'][0]['ending_face']==0
        # The calendar interval includes leap day in 2028.
        assert plot['curves'][0]['points'][-1]['x']==730
        assert plot['curves'][0]['points'][-1]['y']==pytest.approx(100,abs=.02)
        assert all(p['y']>90 for curve in plot['curves'] for p in curve['points'])
    assert discount['result']['coupons']==8
    assert premium['result']['coupons']==12


def test_pull_to_par_last_day_and_early_sale_keep_prices_separate_from_remaining_positions():
    before=calculate('pull-to-par',{'horizon':'before_maturity'}).json()
    assert before['result']['positions'][0]['status']=='held'
    assert before['result']['positions'][0]['ending_face']==100
    assert before['result']['coupons']==6
    early=calculate('pull-to-par',example='early-sale').json()
    position=early['result']['positions'][0]
    assert position['status']=='sold'
    assert early['result']['ending_bond_value']==0
    assert early['focus']['plot']['curves'][1]['points'][-1]['y']==position['dirty']
    assert early['result']['total_return']==pytest.approx(-.003276310654555137,abs=1e-13)


@pytest.mark.parametrize('slug,controls,field',[
    ('holding-period-returns',{'cost_bp':-1},'cost_bp'),
    ('holding-period-returns',{'end_yield':True},'end_yield'),
    ('reinvestment-and-cash',{'cash_rate':-.03},'cash_rate'),
    ('reinvestment-and-cash',{'horizon':'anything'},'horizon'),
    ('pull-to-par',{'horizon':'anything'},'horizon'),
])
def test_invalid_lesson_controls_have_field_errors(slug,controls,field):
    response=calculate(slug,controls)
    assert response.status_code==422
    assert response.json()['detail'][0]['loc'][-1]==field


def test_negative_cash_interest_reduces_wealth_relative_to_zero_cash():
    data=calculate('reinvestment-and-cash',{'cash_rate':-.01}).json()
    assert data['result']['ending_wealth']==pytest.approx(4*.99+104,abs=1e-10)
    assert data['focus']['plot']['curves'][0]['points'][-1]['y']==pytest.approx(-.04,abs=1e-10)
