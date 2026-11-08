"""HTTP parity, explicit acquisition, and M3 lesson navigation."""
import time
import pytest
from fastapi.testclient import TestClient
from filab.web.app import app
from filab.web import history_api
from filab.data.store import SnapshotStore
from filab.data.treasury import compare


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('FILAB_DATA_DIR', str(tmp_path/'cache'))
    return TestClient(app)


def test_read_api_parity_and_snapshot_pinning(client):
    catalog = client.get('/api/history/snapshots').json()
    identifier = catalog['bundled_snapshot_id']
    response = client.get('/api/history/compare', params={'snapshot_id':identifier,'first':'2025-02-14','second':'2025-02-18'})
    assert response.status_code == 200
    data = response.json()
    assert data['data_kind'] == 'historical_observations'
    del data['data_kind']
    assert data == compare(SnapshotStore().fixture, '2025-02-14', '2025-02-18')
    assert client.get(f'/api/history/snapshots/{identifier}').json()['id'] == identifier
    assert client.get('/api/history/compare',params={'first':'2025-02-14','second':'2025-02-18'}).status_code == 422
    assert client.get('/api/history/compare',params={'snapshot_id':'unknown','first':'2025-02-14','second':'2025-02-18'}).status_code == 404
    assert client.get('/api/history/compare',params={'snapshot_id':identifier,'first':'invalid','second':'2025-02-18'}).status_code == 422


def test_hypothetical_revision_is_labeled_and_never_persists(client):
    identifier = client.get('/api/history/snapshots').json()['bundled_snapshot_id']
    params={'snapshot_id':identifier,'first':'2025-02-14','second':'2025-02-18','hypothetical_revision':True}
    data = client.get('/api/history/compare',params=params).json()
    assert data['data_kind'] == 'hypothetical' and data['spread_change_bp'] == 15
    params['hypothetical_revision'] = False
    assert client.get('/api/history/compare',params=params).json()['spread_change_bp'] == 5


@pytest.mark.parametrize('payload',[{'start_year':1989,'end_year':2025},{'start_year':2025,'end_year':2024},{'start_year':2025,'end_year':9999},{'start_year':'2025','end_year':2025},{'start_year':2025,'end_year':2025,'url':'https://example.com'}])
def test_refresh_validation(client,payload):
    assert client.post('/api/history/refresh',json=payload).status_code == 422


def test_failed_job_and_duplicate_submission(client,monkeypatch):
    from threading import Event
    release = Event()
    def failure(*args,**kwargs):
        release.wait(2)
        raise ValueError('internal error')
    monkeypatch.setattr(SnapshotStore,'refresh',failure)
    before=client.get('/api/history/snapshots').json()['active_snapshot_id']
    response=client.post('/api/history/refresh',json={'start_year':2025,'end_year':2025})
    assert response.status_code==202
    job=response.json()['job_id']
    try:
        assert client.post('/api/history/refresh',json={'start_year':2025,'end_year':2025}).status_code==409
    finally:
        release.set()
    for _ in range(100):
        state=client.get('/api/history/refresh/'+job).json()
        if state['state']!='running': break
        time.sleep(.01)
    assert state['state']=='failed'
    assert client.get('/api/history/snapshots').json()['active_snapshot_id']==before
    assert client.get('/api/history/refresh/unknown').status_code==404


@pytest.mark.parametrize('slug', ['par-yields-and-quotes','missing-observations','observation-and-publication','revisions-and-vintages'])
def test_m3_lessons_have_experiments_and_learning_structure(client,slug):
    page=client.get('/lessons/'+slug)
    assert page.status_code==200
    for text in ['data-history', 'data-pinned="true"', 'PREDICT BEFORE', 'class="math block"','Reflect and transfer','class="exercise-answer"','/static/history.js']:
        assert text in page.text
    assert 'data-valuation data-lesson' not in page.text
    assert 'data-refresh-form' not in page.text
    assert 'cdn.' not in page.text
    tool=client.get('/tools/treasury-history').text
    assert 'data-refresh-form' in tool and 'data-snapshot-options' in tool


def test_successful_job_publishes_snapshot_and_preserves_pinned_sample(client,monkeypatch):
    from pathlib import Path
    from filab.data.treasury import digest, source_url, utc_now
    raw=(Path(__file__).resolve().parents[1]/'src/filab/data/fixtures/treasury-202502.xml').read_bytes()
    original=SnapshotStore.refresh
    def local_refresh(self,start,end,**kwargs):
        return original(self,start,end,fetcher=lambda year:(raw,{'url':source_url(year=year),'retrieved_at':utc_now(),'sha256':digest(raw)}),**kwargs)
    monkeypatch.setattr(SnapshotStore,'refresh',local_refresh)
    pinned=client.get('/api/history/snapshots').json()['active_snapshot_id']
    job=client.post('/api/history/refresh',json={'start_year':2025,'end_year':2025}).json()['job_id']
    for _ in range(100):
        state=client.get('/api/history/refresh/'+job).json()
        if state['state']!='running': break
        time.sleep(.01)
    assert state['state']=='complete'
    assert state['snapshot_id']!=pinned
    assert client.get('/api/history/snapshots').json()['active_snapshot_id']==state['snapshot_id']
    assert client.get('/api/history/snapshots/'+pinned).json()['bundled']
