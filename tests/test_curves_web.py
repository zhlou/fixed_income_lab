"""Stateless curve APIs, full-size imports, and installed lesson integration."""
import csv
import io
from datetime import date,timedelta
from importlib.resources import files

import pytest
from fastapi.testclient import TestClient
from filab.web.app import app
from filab.data.fed import COLUMNS, bundled, normalize

client=TestClient(app)


def test_curve_pages_and_synthetic_api():
    for path in ['/tools/discount-curves','/lessons/discount-factors','/lessons/curve-roll-down']:
        page=client.get(path)
        assert page.status_code==200
        assert '/static/curves.js' in page.text
    assert client.post('/api/curves/synthetic',json={}).json()['initial_price']==pytest.approx(97.60)
    assert client.post('/api/curves/synthetic',json={'calibration_price':8.70}).status_code==422
    assert client.post('/api/curves/synthetic',json={'horizon':.1}).status_code==422


def test_compare_parity_missing_dates_and_row_validation():
    data=client.get('/api/curves/bundled').json()
    body=dict(first=data['rows'][-2],second=data['rows'][-1],snapshot_id=data['id'])
    result=client.post('/api/curves/compare',json=body)
    assert result.status_code==200
    assert result.json()['second']['nodes'][0]['zero_rate']==pytest.approx(.043905)
    assert result.json()['valuation']['dirty_price'] is None
    assert client.post('/api/curves/compare',json={**body,'coupon_rate':0}).json()['valuation']['dirty_price']>0
    assert client.post('/api/curves/compare',json={'second_date':'1980-01-01','second':data['rows'][2]}).json()['second']['status']=='No data'
    assert client.post('/api/curves/compare',json={**body,'second_date':'2026-10-31'}).status_code==422
    assert client.post('/api/curves/compare',json={'second':{'date':'2026-10-30','values':[]}}).status_code==422
    assert client.post('/api/curves/compare',json={}).json()['second']['status']=='No data'


def test_raw_import_identity_revisions_and_failure():
    raw=files('filab.data').joinpath('fixtures/fed-sample.csv').read_bytes()
    first=client.post('/api/curves/normalize',content=raw)
    assert first.status_code==200
    assert client.post('/api/curves/normalize',content=raw).json()['id']==first.json()['id']
    revised=client.post('/api/curves/normalize',content=raw+b'\n')
    assert revised.json()['id']!=first.json()['id']
    for broken in [b'',b'garbage',raw[:-100],raw.replace(b'4.3905',b'NaN')]:
        assert client.post('/api/curves/normalize',content=broken).status_code==422
    assert client.post('/api/curves/normalize',content=b'x'*24000001).status_code==413
    assert client.get('/api/curves/bundled').json()['id']==first.json()['id']


def test_full_size_csv_exceeds_treasury_limits_without_losing_rows():
    # Repeated real model values with explicitly synthetic consecutive dates.
    raw=files('filab.data').joinpath('fixtures/fed-sample.csv').read_text()
    source=list(csv.DictReader(raw[raw.index('Date,'):].splitlines()))[-1]
    output=io.StringIO();writer=csv.DictWriter(output,fieldnames=list(source));writer.writeheader()
    for i in range(17058):
        writer.writerow({**source,'Date':(date(1980,1,1)+timedelta(days=i)).isoformat()})
    payload=output.getvalue().encode()
    assert len(payload)>4_000_000
    response=client.post('/api/curves/normalize',content=payload)
    assert response.status_code==200
    assert len(response.json()['rows'])==17058


def test_numerical_overflow_is_an_input_error():
    row=bundled()['rows'][-1]
    row['values'][0]=1e300
    response=client.post('/api/curves/compare',json={'second':row})
    assert response.status_code==422
