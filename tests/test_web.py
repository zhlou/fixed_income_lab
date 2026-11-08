"""HTTP behavior and financial parity for the local learning website."""

from math import isclose
from html import unescape
import re
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from filab.web.app import app
from filab.web.app import markdown
from filab.web.curriculum import LESSONS

client = TestClient(app)


@pytest.mark.parametrize("path", ["/"] + ["/lessons/" + item["slug"] for item in LESSONS] + ["/tools/treasury-bills"])
def test_pages_load_with_navigation(path):
    response = client.get(path)
    assert response.status_code == 200
    assert 'aria-label="Lessons"' in response.text
    assert '/static/app.js' in response.text
    assert 'https://cdn.' not in response.text


def test_unknown_lesson_is_not_found():
    assert client.get('/lessons/not-a-lesson').status_code == 404


@pytest.mark.parametrize('lesson_number, lesson', list(enumerate(LESSONS, start=1)), ids=[item['slug'] for item in LESSONS])
def test_lesson_picker_destinations_and_current_lesson(lesson_number, lesson):
    response = client.get('/lessons/' + lesson['slug'])
    assert response.status_code == 200
    page = response.text
    assert 'aria-controls="lesson-picker-panel" aria-expanded="false"' in page
    assert f'current lesson {lesson_number} of {len(LESSONS)}' in page
    panel = re.search(r'<div id="lesson-picker-panel"[^>]* hidden>(.*?)</div>', page, re.S).group(1)
    links = re.findall(r'<a href="(/lessons/[^"]+)"([^>]*)>(.*?)</a>', panel, re.S)
    assert [href for href, _, _ in links] == ['/lessons/' + item['slug'] for item in LESSONS]
    assert [href for href, attrs, _ in links if 'aria-current="page"' in attrs] == ['/lessons/' + lesson['slug']]
    for number, ((_, _, label), item) in enumerate(zip(links, LESSONS), start=1):
        assert unescape(re.sub(r'<[^>]+>', '', label)) == f'{number:02d}{item["title"]}'


@pytest.mark.parametrize("instrument, expected", [("coupon", 981.1901289599514), ("zero", 905.9506447997552)])
def test_worked_prices_and_discounting_table_agree(instrument, expected):
    response = client.post('/api/valuation', json={"instrument": instrument})
    assert response.status_code == 200
    data = response.json()
    assert data['price'] == pytest.approx(expected)
    assert sum(flow['present_value'] for flow in data['cashflows']) == pytest.approx(data['price'])
    assert data['coupon_pv'] + data['principal_pv'] == pytest.approx(data['price'])
    assert sum(flow['coupon_present_value'] for flow in data['cashflows']) == pytest.approx(data['coupon_pv'])
    assert sum(flow['principal_present_value'] for flow in data['cashflows']) == pytest.approx(data['principal_pv'])
    for flow in data['cashflows']:
        assert flow['coupon_present_value'] == pytest.approx(flow['coupon'] * flow['discount_factor'])
        assert flow['principal_present_value'] == pytest.approx(flow['principal'] * flow['discount_factor'])
    assert data['cashflows'][-1]['principal'] == 1000


def test_schedule_and_final_coupon():
    data = client.post('/api/valuation', json={}).json()
    assert len(data['cashflows']) == 4
    assert data['cashflows'][-1]['amount'] == 1020
    assert data['total_received'] == 1080


def test_par_zero_yield_and_negative_yields():
    assert client.post('/api/valuation', json={'ytm': 0.04}).json()['price'] == pytest.approx(1000)
    assert client.post('/api/valuation', json={'ytm': 0}).json()['price'] == pytest.approx(1080)
    assert client.post('/api/valuation', json={'ytm': -0.01}).json()['price'] > 1080


def test_zero_supports_fractional_periods_and_maturity():
    fractional = client.post('/api/valuation', json={'instrument': 'zero', 'maturity_years': 0.25})
    assert fractional.status_code == 200
    matured = client.post('/api/valuation', json={'instrument': 'zero', 'maturity_years': 0})
    assert matured.json()['price'] == 1000


@pytest.mark.parametrize("payload", [
    {'maturity_years': 0.75}, {'maturity_years': 0}, {'face_value': -1},
    {'frequency': 0}, {'ytm': -2}, {'coupon_rate': -0.04}, {'maturity_years': 100000},
    {'instrument': 'unknown'}, {'extra': 1},
])
def test_invalid_inputs_have_structured_errors(payload):
    response = client.post('/api/valuation', json=payload)
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'][0] == 'body'


def test_nonfinite_value_has_serializable_error():
    response = client.post('/api/valuation', content='{"ytm": NaN}', headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    assert 'finite' in response.json()['detail'][0]['msg'].lower()


def test_effective_rate_and_reinvestment_are_distinct():
    data = client.post('/api/rates', json={}).json()
    assert data['effective_rate'] == pytest.approx(0.0404)
    assert data['held_interest'] == pytest.approx(40)
    assert data['reinvested_interest'] == pytest.approx(40.40)
    assert data['extra_interest'] == pytest.approx(0.40)
    reverse = client.post('/api/rates', json={'convention': 'effective', 'rate': data['effective_rate']}).json()
    assert reverse['nominal_rate'] == pytest.approx(0.04)


def test_equivalent_rate_conventions_price_the_same_zero():
    effective = client.post('/api/rates', json={'rate': 0.04}).json()['effective_rate']
    nominal_price = client.post('/api/valuation', json={'instrument': 'zero', 'ytm': 0.04, 'maturity_years': 0.5}).json()['price']
    effective_price = client.post('/api/valuation', json={'instrument': 'zero', 'ytm': effective, 'frequency': 1, 'maturity_years': 0.5}).json()['price']
    assert nominal_price == pytest.approx(effective_price)


@pytest.mark.parametrize('mode', ['maturity', 'coupon', 'sensitivity'])
def test_experiments_keep_price_axes_and_match_shock_table(mode):
    data = client.post('/api/experiments', json={'mode': mode}).json()
    assert len(data['curves']) == 2
    assert data['y_label'] == 'Price per $100 face'
    assert data['percent_y'] is False
    assert data['y_domain'] == [0, 250]
    assert data['curves'][0]['baseline'] is True
    assert data['curves'][1]['baseline'] is False
    for curve, row in zip(data['curves'], data['rows']):
        points = curve['points']
        assert [p['x'] for p in points] == pytest.approx([i / 1000 for i in range(101)])
        assert all(0 < p['y'] < 250 for p in points)
        assert all(a['y'] > b['y'] for a, b in zip(points, points[1:]))
        assert float(row[1]) == pytest.approx(curve['marker']['y'], abs=0.005)
        after = next(p['y'] for p in points if isclose(p['x'], 0.06))
        assert float(row[2]) == pytest.approx(after, abs=0.005)
        assert float(row[3].rstrip('%')) == pytest.approx((after / curve['marker']['y'] - 1) * 100, abs=0.005)


def test_maturity_changes_only_selected_maturity():
    short = client.post('/api/experiments', json={'mode': 'maturity', 'maturity_years': 2, 'coupon_rate': 0.12}).json()
    long = client.post('/api/experiments', json={'mode': 'maturity', 'maturity_years': 30}).json()
    assert short['curves'][0] == long['curves'][0]
    for data, maturity in ((short, 2), (long, 30)):
        assert data['timeline']['payment_coupon'] == 2
        assert data['timeline']['cashflows'][-1]['time_years'] == maturity
        assert next(p['y'] for p in data['curves'][1]['points'] if isclose(p['x'], 0.04)) == pytest.approx(100)
    assert abs(float(long['rows'][1][3].rstrip('%'))) > abs(float(short['rows'][1][3].rstrip('%')))


def test_coupon_changes_only_selected_coupon():
    low = client.post('/api/experiments', json={'mode': 'coupon', 'coupon_rate': 0.02, 'maturity_years': 30}).json()
    high = client.post('/api/experiments', json={'mode': 'coupon', 'coupon_rate': 0.065}).json()
    assert low['curves'][0] == high['curves'][0]
    assert low['timeline']['cashflows'][-1]['time_years'] == 10
    assert high['timeline']['payment_coupon'] == 3.25
    assert '6.5% coupon' in high['curves'][1]['label']
    assert high['curves'][1]['marker']['y'] > low['curves'][1]['marker']['y']


@pytest.mark.parametrize('payload', [
    {'mode': 'maturity', 'maturity_years': 10},
    {'mode': 'coupon', 'coupon_rate': 0.04},
    {'mode': 'sensitivity', 'payment_type': 'coupon'},
])
def test_matching_baseline_explains_coincident_curves(payload):
    data = client.post('/api/experiments', json=payload).json()
    assert data['identical'] is True
    assert 'curves coincide' in data['insight']
    assert data['curves'][0]['points'] == data['curves'][1]['points']


def test_timing_uses_dollar_prices_and_single_zero_coupon_payment():
    data = client.post('/api/experiments', json={'mode': 'sensitivity', 'payment_type': 'zero'}).json()
    assert data['curves'][1]['marker']['y'] == pytest.approx(61.02709428588309)
    assert len(data['timeline']['cashflows']) == 1
    assert data['timeline']['total_coupons'] == 0
    assert data['rows'][1][3] == '-9.27%'


def test_comparison_yield_moves_markers_but_not_curves():
    before = client.post('/api/experiments', json={'ytm': 0.04}).json()
    after = client.post('/api/experiments', json={'ytm': 0.05}).json()
    for a, b in zip(before['curves'], after['curves']):
        assert a['points'] == b['points']
        assert a['marker']['x'] != b['marker']['x']
    assert before['rows'] != after['rows']


def test_assets_and_math_are_local():
    response = client.get('/lessons/present-value')
    assert 'class="math block"' in response.text
    assert client.get('/static/vendor/katex/katex.min.js').status_code == 200
    assert client.get('/static/vendor/katex/fonts/KaTeX_Main-Regular.woff2').status_code == 200
    assert 'id="under-the-hood"' in response.text
    assert "fixed_coupon_cashflows" in response.text


def test_currency_is_not_mistaken_for_inline_math():
    rendered = markdown.render('A $1,000 bond pays two $20 coupons and $40 in total.')
    assert 'math inline' not in rendered
    assert '$1,000' in rendered and '$20' in rendered and '$40' in rendered
    assert 'math inline' in markdown.render('Time $T$ is in years.')


def test_lesson_sequence_and_optional_implementation():
    home = client.get('/').text
    assert f'{len(LESSONS)} available lessons' in home
    assert home.count('class="lesson-card"') == len(LESSONS)
    for index, lesson in enumerate(LESSONS):
        page = client.get('/lessons/' + lesson['slug']).text
        assert page.count('class="lesson-link ') == len(LESSONS)
        if index + 1 < len(LESSONS):
            assert f'href="/lessons/{LESSONS[index+1]["slug"]}" class="next-lesson"' in page
        if lesson['prerequisite']:
            assert next(i for i, l in enumerate(LESSONS) if l['slug'] == lesson['prerequisite']) < index
    first = client.get('/lessons/present-value').text
    details = re.search(r'<details[^>]*id="under-the-hood"[^>]*>', first).group()
    assert ' open' not in details
    assert 'Optional Python examples' in first
    assert 'lesson-time' not in home


def test_old_implementation_url_redirects_to_optional_section():
    response = client.get('/lessons/cash-flows-and-pricing', follow_redirects=False)
    assert response.status_code == 308
    assert response.headers['location'] == '/lessons/present-value#under-the-hood'


def test_yield_worked_example_and_payment_table():
    response = client.post('/api/yield', json={})
    assert response.status_code == 200
    data = response.json()
    assert data['price'] == 98.12
    assert data['ytm'] == pytest.approx(0.04999468825810297)
    assert data['coupon_rate'] == 0.04
    assert data['current_yield'] == pytest.approx(4 / data['price'])
    assert data['repriced'] == pytest.approx(data['price'])
    assert sum(flow['present_value'] for flow in data['cashflows']) == pytest.approx(data['price'])
    assert abs(data['residual']) < 1e-10


@pytest.mark.parametrize('price', [90, 100, 108, 120])
def test_coupon_current_and_implied_yield_ordering(price):
    response = client.post('/api/yield', json={'price': price})
    assert response.status_code == 200
    data = response.json()
    if price < 100:
        assert data['coupon_rate'] < data['current_yield'] < data['ytm']
    elif price > 100:
        assert data['coupon_rate'] > data['current_yield'] > data['ytm']
    else:
        assert data['ytm'] == pytest.approx(data['coupon_rate'])
    if price == 108:
        assert data['ytm'] == pytest.approx(0, abs=1e-12)
    if price == 120:
        assert data['ytm'] < 0


@pytest.mark.parametrize('frequency', [1, 2, 4, 12])
def test_yield_zero_coupon_and_frequency(frequency):
    data = client.post('/api/yield', json={'coupon_rate': 0, 'price': 90, 'frequency': frequency}).json()
    assert data['ytm'] == pytest.approx(frequency * ((100 / 90) ** (1 / (2 * frequency)) - 1))
    assert data['current_yield'] == 0


@pytest.mark.parametrize('payload, field', [
    ({'price': 0}, 'price'), ({'price': -10}, 'price'),
    ({'maturity_years': 0}, 'maturity_years'),
    ({'maturity_years': 0.75}, 'maturity_years'),
    ({'coupon_rate': -0.01}, 'coupon_rate'), ({'frequency': 3}, 'frequency'),
    ({'ytm': 0.05}, 'ytm'),
])
def test_invalid_yield_inputs_have_field_errors(payload, field):
    response = client.post('/api/yield', json=payload)
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', field]


def test_yield_nonfinite_price_has_serializable_error():
    response = client.post('/api/yield', content='{"price": NaN}', headers={'Content-Type': 'application/json'})
    assert response.status_code == 422


def test_pricing_lesson_has_both_directions_and_cent_price_input():
    page = client.get('/lessons/present-value').text
    assert 'data-core-experiment="pricing"' in page
    assert 'value="98.12" min="0.01" max="300" step="0.01"' in page
    assert 'id="core-price" name="price"' in page
    assert 'value="price"' in page and 'value="yield"' in page
    priced = client.post('/api/valuation', json={'face_value':100}).json()
    solved = client.post('/api/yield', json={'price':priced['price']}).json()
    assert priced['ytm'] == pytest.approx(solved['ytm'], abs=1e-12)
    assert priced['current_yield'] == pytest.approx(solved['current_yield'], abs=1e-12)


def test_settlement_default_prices_day_counts_and_path():
    response = client.post('/api/settlement', json={})
    assert response.status_code == 200
    data = response.json()
    assert data['accrued_interest'] == 1
    assert data['elapsed_days'] == 92 and data['period_days'] == 184
    assert data['dirty_price'] == pytest.approx(data['clean_price'] + 1)
    assert sum(flow['present_value'] for flow in data['cashflows']) == pytest.approx(data['dirty_price'])
    assert data['cashflows'][0]['payment_date'] > '2026-08-15'
    assert data['path'][0]['clean'] == pytest.approx(data['clean_price'])
    assert data['path'][-1]['date'] == '2028-11-14'
    assert data['path'][-1]['clean'] == pytest.approx(100, abs=.01)
    coupon = next(p for p in data['path'] if p['date'] == '2026-11-15')
    assert coupon['accrued'] == 0


@pytest.mark.parametrize('price_type', ['clean', 'dirty'])
def test_settlement_api_yield_solves_correct_price_type(price_type):
    data = client.post('/api/settlement', json={}).json()
    response = client.post('/api/settlement', json={'mode':'yield', 'price_type':price_type, 'price':data[price_type + '_price']})
    assert response.status_code == 200
    solved = response.json()
    assert solved['ytm'] == pytest.approx(.05)
    assert abs(solved['price_residual']) < 1e-9


@pytest.mark.parametrize('payload, field', [
    ({'issue_date':'2025-11-14'}, 'issue_date'),
    ({'settlement_date':'2028-11-15'}, 'settlement_date'),
    ({'settlement_date':'2024-11-15'}, 'settlement_date'),
    ({'maturity_date':'2024-11-15'}, 'maturity_date'),
    ({'settlement_date':'not-a-date'}, 'settlement_date'),
    ({'maturity_date':'2128-11-15'}, 'maturity_date'),
    ({'price':0}, 'price'), ({'price_type':'unknown'}, 'price_type'),
])
def test_settlement_api_field_errors(payload, field):
    response = client.post('/api/settlement', json=payload)
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', field]


def test_bill_api_and_curve_values_share_convention():
    response = client.post('/api/bills', json={})
    assert response.status_code == 200
    data = response.json()
    assert data['price'] == pytest.approx(100 * (1 - .05 * 182 / 360))
    assert data['investment_rate'] == pytest.approx((100 / data['price'] - 1) * 365 / 182)
    for key, curve in zip(['discount_rate','investment_rate'], data['curves']):
        point = next(p for p in curve['points'] if p['x'] == 182)
        assert point['y'] == data[key]
        assert curve['marker'] == point
    long = client.post('/api/bills', json={'days_to_maturity':364}).json()
    assert long['method'] == 'Coupon-equivalent quadratic'
    assert long['investment_rate'] != pytest.approx(long['simple_annual_rate'])
    leap = client.post('/api/bills', json={'year_days':366}).json()
    assert leap['price'] == data['price']
    assert leap['investment_rate'] > data['investment_rate']


@pytest.mark.parametrize('payload', [{'days_to_maturity':0}, {'days_to_maturity':367}, {'days_to_maturity':1.5}, {'year_days':360}, {'discount_rate':-1}])
def test_bill_api_rejects_invalid_conventions(payload):
    assert client.post('/api/bills', json=payload).status_code == 422


def test_settlement_and_bill_tool_have_distinct_entrypoints():
    settlement = client.get('/lessons/settlement-and-accrued-interest').text
    bills = client.get('/tools/treasury-bills').text
    assert 'data-settlement' in settlement and 'data-bills' in bills
    assert 'href="/lessons/reinvestment-and-cash" class="next-lesson"' in settlement
    assert 'name="settlement_date" type="date"' in settlement
    assert 'href="/tools/treasury-bills"' in client.get('/lessons/present-value').text
    assert 'data-core-experiment' not in bills
    assert 'Available' in client.get('/').text
