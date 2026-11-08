"""M2 numerical API parity, input snapshots, and published lesson integration."""
from dataclasses import asdict
from datetime import date

import pytest

pytest.importorskip('fastapi')
from fastapi.testclient import TestClient
from filab.web.app import app
from filab.web.curriculum import LESSONS
from filab.web.returns_api import ReturnInputs
from filab.analytics import BondHolding, YieldPoint, holding_period_ledger

client = TestClient(app)


def study(**changes):
    inputs = ReturnInputs(**changes).model_dump(mode='json')
    return dict(schema_version=1,kind='filab-bond-return',conventions='dated-return-ledger-v1',inputs=inputs)


def test_default_return_matches_domain_and_does_not_double_count_coupon():
    response=client.post('/api/returns',json={})
    assert response.status_code==200
    data=response.json();r=data['result']
    h=BondHolding('Bond A',100,.04,date(2025,11,15),date(2028,11,15),
                  (YieldPoint(date(2026,11,14),.05),))
    expected=holding_period_ledger(holdings=[h],start_date=date(2026,11,14),end_date=date(2026,11,16))
    for key in ['purchase_dirty','coupons','ending_wealth','total_return','net_profit']:
        assert r[key]==pytest.approx(getattr(expected,key),abs=1e-11)
    assert r['coupons']==2
    assert r['ending_bond_value']==0
    assert r['ending_wealth']==r['ending_cash']
    assert r['total_return']==pytest.approx(.0002679661864690708,abs=1e-13)
    assert data['conventions']=='dated-return-ledger-v1'
    assert data['inputs']==ReturnInputs().model_dump(mode='json')
    assert data['price_provenance']==dict(purchase='hypothetical YTM model',later_prices='hypothetical YTM model')


def test_quote_commits_cents_and_adds_actual_accrual_in_position_units():
    response=client.post('/api/returns',json={'purchase_method':'clean','price':98.12,'face_value':1000})
    assert response.status_code==200
    data=response.json();r=data['result']
    assert r['purchase_clean']==pytest.approx(981.2,abs=1e-9)
    assert r['purchase_accrued']==pytest.approx(20*183/184,abs=1e-10)
    assert r['purchase_dirty']==pytest.approx(r['purchase_clean']+r['purchase_accrued'])
    assert data['purchase_ytms'][0]['ytm']!=.05
    assert data['price_provenance']['purchase']=='user-assumed clean quote'


def test_annual_two_period_example_and_cash_comparison():
    payload=dict(start_date='2025-11-15',end_date='2027-11-15',maturity_date='2027-11-15',
                 frequency=1,cash_policy='interest',cash_rate=.05)
    response=client.post('/api/returns',json=payload)
    assert response.status_code==200
    data=response.json();r=data['result']
    assert r['ending_wealth']==pytest.approx(108.2,abs=1e-10)
    assert r['cash_interest']==pytest.approx(.2,abs=1e-10)
    assert r['total_return']==pytest.approx(.1025,abs=1e-12)
    assert [row['ending_wealth'] for row in data['cash_comparison']]==pytest.approx([108,108.2],abs=1e-10)
    assert len([e for e in r['ledger'] if e['event']=='redemption'])==1
    assert not any(e['event']=='sale' for e in r['ledger'])


@pytest.mark.parametrize('treatment',['mark','liquidate'])
def test_aggregate_api_wealth_and_costs(treatment):
    r=client.post('/api/returns',json={'include_comparison':True,'end_treatment':treatment,'cost_bp':10}).json()['result']
    assert len(r['positions'])==2
    assert r['purchase_fees']==pytest.approx(.2)
    assert r['sale_fees']==pytest.approx(0 if treatment=='mark' else .2)
    assert r['ending_wealth']==pytest.approx(r['ending_bond_value']+r['ending_cash'])
    assert r['reconciliation_residual']==pytest.approx(0,abs=1e-9)


@pytest.mark.parametrize('payload,field',[
    ({'end_date':'2026-11-14'},'end_date'),
    ({'start_date':'2029-11-14','end_date':'2029-11-16'},'start_date'),
    ({'issue_date':'2025-11-14'},'issue_date'),
    ({'maturity_date':'2026-01-01'},'issue_date'),
    ({'yield_path':'shock','shock_date':'2026-11-14'},'shock_date'),
    ({'yield_path':'shock','shock_date':'2027-11-15'},'shock_date'),
    ({'purchase_method':'clean','price':98.123},'price'),
    ({'purchase_method':'clean','price':0},'price'),
    ({'include_comparison':True,'comparison_maturity_date':'2036-11-14'},'comparison_maturity_date'),
    ({'include_comparison':True,'purchase_method':'clean','comparison_price':99.999},'comparison_price'),
    ({'frequency':3},'frequency'),({'cash_rate':-1},'cash_rate'),
    ({'cost_bp':-1},'cost_bp'),({'start_yield':-.03},'start_yield'),({'coupon_rate':-.01},'coupon_rate'),
    ({'face_value':True},'face_value'),
])
def test_invalid_inputs_produce_field_errors(payload,field):
    response=client.post('/api/returns',json=payload)
    assert response.status_code==422
    assert response.json()['detail'][0]['loc'][-1]==field


def test_nonfinite_json_error_is_serializable():
    response=client.post('/api/returns',content='{"cash_rate":NaN}',headers={'Content-Type':'application/json'})
    assert response.status_code==422
    assert 'finite' in response.json()['detail'][0]['msg'].lower()


def test_complete_saved_inputs_round_trip_with_all_conventions():
    saved=study(include_comparison=True,cash_policy='interest',cost_bp=10,yield_path='shock')
    response=client.post('/api/return-study',json=saved)
    assert response.status_code==200
    assert response.json()['study']==saved
    assert response.json()['result']==client.post('/api/returns',json=saved['inputs']).json()


@pytest.mark.parametrize('change',[{'schema_version':2},{'schema_version':True},{'kind':'other'},
    {'conventions':'other'}, {'unexpected':1}])
def test_incompatible_saved_scenarios_are_rejected(change):
    saved=study();saved.update(change)
    assert client.post('/api/return-study',json=saved).status_code==422


def test_saved_inputs_cannot_silently_fill_missing_fields():
    saved=study();del saved['inputs']['cash_policy']
    assert client.post('/api/return-study',json=saved).status_code==422


def portfolio():
    return dict(start_date='2025-11-15',end_date='2027-11-15',cash_rate=.05,cost_bp=10,
        holdings=[dict(label='A',face_value=100,coupon_rate=.04,issue_date='2025-11-15',
            maturity_date='2027-11-15',frequency=1,yields=[dict(date='2025-11-15',ytm=.05)],
            sale_date='2026-11-15')])


def test_explicit_ledger_api_preserves_early_sale_and_domain_parity():
    payload=portfolio()
    response=client.post('/api/return-ledger',json=payload)
    assert response.status_code==200
    h=BondHolding('A',100,.04,date(2025,11,15),date(2027,11,15),
        (YieldPoint(date(2025,11,15),.05),),1,date(2026,11,15))
    expected=holding_period_ledger(holdings=[h],start_date=date(2025,11,15),end_date=date(2027,11,15),cash_rate=.05,cost_bp=10)
    assert response.json()['ending_wealth']==pytest.approx(expected.ending_wealth,abs=1e-11)
    assert response.json()['positions'][0]['status']=='sold'


def test_explicit_paths_reject_future_fill_and_duplicate_dates():
    for points in [[dict(date='2026-11-15',ytm=.05)],
                   [dict(date='2025-11-15',ytm=.05),dict(date='2025-11-15',ytm=.06)]]:
        payload=portfolio();payload['holdings'][0]['yields']=points
        assert client.post('/api/return-ledger',json=payload).status_code==422


def test_m2_pages_have_separate_lessons_formulas_navigation_and_local_assets():
    slugs=['coupons-and-return','pull-to-par','reinvestment-and-cash','holding-period-returns']
    for index,slug in enumerate(slugs):
        response=client.get('/lessons/'+slug)
        assert response.status_code==200
        text=response.text
        assert f'LESSON {index+10:02}' in text
        assert 'data-return-lesson' in text
        assert 'data-valuation data-lesson' not in text and 'data-risk-weights' not in text
        assert 'PREDICT BEFORE' in text and 'Reflection checkpoint' in text
        assert 'Transfer exercise' in text and 'class="math block"' in text
        assert '<details class="exercise-answer"><summary>Reveal the explanation</summary>' in text
        assert '::: answer' not in text
        if index<3:
            assert f'href="/lessons/{slugs[index+1]}" class="next-lesson"' in text
        previous = slugs[index-1] if index else 'convexity'
        assert f'href="/lessons/{previous}"><small>← PREVIOUS LESSON</small>' in text
    assert 'href="/lessons/coupons-and-return" class="next-lesson"' in client.get('/lessons/convexity').text
    home=client.get('/').text
    assert f'{len(LESSONS)} available lessons' in home
    assert 'Open Bond Return Calculator' in home
    tool=client.get('/tools/bond-return')
    assert tool.status_code==200 and 'data-ledger-export' in tool.text
    assert client.get('/static/returns.js').status_code==200
