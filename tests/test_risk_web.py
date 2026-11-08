from dataclasses import asdict

import pytest
from fastapi.testclient import TestClient
from filab.web.app import app, RiskInputs
from filab.risk import bond_risk

client = TestClient(app)


def test_default_comparison_matches_financial_library_and_weights():
    response=client.post('/api/risk',json={})
    assert response.status_code == 200
    a,b=response.json()['bonds']
    expected=bond_risk(face_value=100,coupon_rate=.04,ytm=.05,maturity_years=2,frequency=2)
    assert a['risk']==asdict(expected)
    assert sum(f['weight'] for f in a['cashflows'])==pytest.approx(1)
    assert sum(f['weighted_time'] for f in a['cashflows'])==pytest.approx(expected.macaulay_duration)
    assert b['risk']['modified_duration'] > a['risk']['modified_duration']
    assert [p['shock_bp'] for p in a['scenarios']]==[-200,-100,-50,-25,0,25,50,100,200]
    assert len(a['points'])==81
    assert a['selected']['exact_price']==pytest.approx(96.28290159718962)


def test_dated_mode_uses_dirty_normalization():
    result=client.post('/api/risk',json={'mode':'dated'}).json()
    assert result['normalization']=='dirty price'
    for bond in result['bonds']:
        assert bond['risk']['macaulay_duration'] is None
        assert bond['risk']['bump']==.00005
        assert bond['clean_price']+bond['accrued_interest']==pytest.approx(bond['risk']['price'])
        assert sum(f['present_value'] for f in bond['cashflows'])==pytest.approx(bond['risk']['price'])


@pytest.mark.parametrize('payload,field', [
    ({'maturity_years':1.2},'maturity_years'),
    ({'comparison_maturity_years':1.2},'comparison_maturity_years'),
    ({'mode':'dated','maturity_date':'2024-11-15'},'maturity_date'),
    ({'mode':'dated','comparison_maturity_date':'2036-11-14'},'comparison_maturity_date'),
    ({'mode':'dated','settlement_date':'2030-01-01'},'settlement_date'),
    ({'frequency':3},'frequency'),({'shock_bp':201},'shock_bp'),
    ({'ytm':-.03},'ytm'),({'coupon_rate':-.01},'coupon_rate'),
])
def test_invalid_risk_inputs_have_field_errors(payload,field):
    response=client.post('/api/risk',json=payload)
    assert response.status_code==422
    assert response.json()['detail'][0]['loc'][-1]==field


@pytest.mark.parametrize('mode',['regular','dated'])
def test_versioned_study_round_trip(mode):
    inputs=RiskInputs(mode=mode,face_value=100000,frequency=4,shock_bp=-200).model_dump(mode='json')
    study=dict(schema_version=1,kind='filab-bond-risk',conventions='nominal-yield-risk-v1',inputs=inputs)
    response=client.post('/api/risk-study',json=study)
    assert response.status_code==200
    assert response.json()['study']==study
    assert response.json()['result']==client.post('/api/risk',json=inputs).json()


@pytest.mark.parametrize('change',[{'schema_version':2},{'kind':'another-tool'},
    {'conventions':'other-pricer'},{'unexpected':42}])
def test_incompatible_study_is_rejected(change):
    study=dict(schema_version=1,kind='filab-bond-risk',conventions='nominal-yield-risk-v1',inputs=RiskInputs().model_dump(mode='json'))
    study.update(change)
    assert client.post('/api/risk-study',json=study).status_code==422


def test_focused_risk_lessons_and_full_explorer():
    for index, slug in enumerate(['modified-duration-dv01', 'convexity'], start=3):
        page=client.get('/lessons/'+slug)
        assert page.status_code==200
        assert f'LESSON {index:02}' in page.text
        assert 'data-core-experiment' in page.text and 'math block' in page.text
        assert 'data-risk-export' not in page.text
        assert '/tools/bond-risk' in page.text
    tool=client.get('/tools/bond-risk')
    assert tool.status_code==200 and 'data-risk-export' in tool.text
    assert 'data-risk-convergence' in tool.text
    assert client.get('/static/risk.js').status_code==200


def test_saved_study_requires_complete_inputs_and_explicit_version():
    study=dict(schema_version=1,kind='filab-bond-risk',conventions='nominal-yield-risk-v1',
               inputs=RiskInputs().model_dump(mode='json'))
    del study['inputs']['frequency']
    assert client.post('/api/risk-study',json=study).status_code==422
    study['inputs']=RiskInputs().model_dump(mode='json')
    study['schema_version']=True
    assert client.post('/api/risk-study',json=study).status_code==422


def test_transfer_answers_are_collapsed_and_math_is_renderable():
    for slug in ['modified-duration-dv01','convexity']:
        page=client.get('/lessons/'+slug).text
        assert '<details class="exercise-answer"><summary>Reveal the explanation</summary>' in page
        assert '<details class="exercise-answer" open' not in page
        assert '::: answer' not in page
