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
    response = client.get('/api/history/compare', params={'snapshot_id':identifier,'first':'2026-11-05','second':'2026-11-06'})
    assert response.status_code == 200
    data = response.json()
    assert data['data_kind'] == 'historical_observations'
    del data['data_kind']
    del data['revision_scenario']
    assert data == compare(SnapshotStore().fixture, '2026-11-05', '2026-11-06')
    assert client.get(f'/api/history/snapshots/{identifier}').json()['id'] == identifier
    assert client.get('/api/history/compare',params={'first':'2026-11-05','second':'2026-11-06'}).status_code == 422
    assert client.get('/api/history/compare',params={'snapshot_id':'unknown','first':'2026-11-05','second':'2026-11-06'}).status_code == 404
    assert client.get('/api/history/compare',params={'snapshot_id':identifier,'first':'invalid','second':'2026-11-06'}).status_code == 422


def test_hypothetical_revision_is_labeled_and_never_persists(client):
    identifier = client.get('/api/history/snapshots').json()['bundled_snapshot_id']
    params={'snapshot_id':identifier,'first':'2026-11-05','second':'2026-11-06','hypothetical_revision':True}
    data = client.get('/api/history/compare',params=params).json()
    assert data['data_kind'] == 'hypothetical' and data['spread_change_bp'] == 7
    params['hypothetical_revision'] = False
    assert client.get('/api/history/compare',params=params).json()['spread_change_bp'] == -3


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


@pytest.mark.parametrize('slug', ['par-yields-and-quotes','observation-and-publication','revisions-and-vintages'])
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


def test_merged_lesson_contains_missing_data_and_updated_navigation(client):
    page = client.get('/lessons/par-yields-and-quotes').text
    assert '<h2>Which observations can we compare?</h2>' in page
    assert 'data-missing-date' in page
    assert 'Missing tenor on a published date' in page
    assert 'No published row within coverage' in page
    assert 'Outside cached coverage' in page
    assert '1.5-month' in page and '4.41%' in page
    assert 'href="/lessons/observation-and-publication" class="next-lesson"' in page
    timing = client.get('/lessons/observation-and-publication').text
    assert 'LESSON 15' in timing
    assert 'href="/lessons/par-yields-and-quotes"><small>← PREVIOUS LESSON' in timing
    assert 'LESSON 16' in client.get('/lessons/revisions-and-vintages').text


@pytest.mark.parametrize('sample,coverage,count,published,missing', [
    ('recent',[['2026-11-01','2026-11-07']],5,'2026-11-06','2026-11-07'),
    ('reference',[['2025-02-01','2025-02-28']],19,'2025-02-14','2025-02-17'),
])
def test_calendar_metadata_matches_published_rows_without_fetching(client,monkeypatch,sample,coverage,count,published,missing):
    def forbidden(*args,**kwargs):
        raise AssertionError('Reading cached dates must not refresh Treasury data')
    monkeypatch.setattr(SnapshotStore,'refresh',forbidden)
    store=SnapshotStore()
    snapshot=store.fixture if sample=='recent' else store.reference_fixture
    response=client.get(f"/api/history/snapshots/{snapshot['id']}/dates")
    assert response.status_code==200
    data=response.json()
    assert data=={'snapshot_id':snapshot['id'],'coverage':coverage, 'published_dates':sorted(snapshot['rows'])}
    assert len(data['published_dates'])==count
    # February 14 lacks the new 1.5-month tenor but is still a published row.
    assert published in data['published_dates']
    assert missing not in data['published_dates']
    assert client.get('/api/history/snapshots/unknown/dates').status_code==404


def test_calendar_metadata_stays_pinned_when_observation_dates_change(client,monkeypatch,tmp_path):
    from pathlib import Path
    from xml.etree import ElementTree as ET
    from filab.data.treasury import ATOM, DATA, META, digest, source_url, utc_now
    store=SnapshotStore(tmp_path/'store')
    monkeypatch.setattr(history_api,'store',lambda:store)
    raw=(Path(__file__).resolve().parents[1]/'src/filab/data/fixtures/treasury-202502.xml').read_bytes()
    def acquire(payload):
        return payload,{'url':source_url(year=2025),'retrieved_at':utc_now(),'sha256':digest(payload)}
    first=store.refresh(2025,2025,lambda year:acquire(raw))
    root=ET.fromstring(raw)
    for entry in root.findall(ATOM+'entry'):
        if entry.findtext(f'{ATOM}content/{META}properties/{DATA}NEW_DATE').startswith('2025-02-14'):
            root.remove(entry)
    revised=ET.tostring(root)
    second=store.refresh(2025,2025,lambda year:acquire(revised))
    old=client.get(f'/api/history/snapshots/{first}/dates').json()
    new=client.get(f'/api/history/snapshots/{second}/dates').json()
    assert '2025-02-14' in old['published_dates']
    assert '2025-02-14' not in new['published_dates']
    assert old['coverage']==new['coverage']==[['2025-01-01','2025-12-31']] + store.viewer['coverage']


def test_history_dates_have_named_calendar_buttons_and_live_status(client):
    page=client.get('/tools/treasury-history').text
    assert page.count('data-history-date>')==2
    assert page.count('data-open-calendar')==2
    assert page.count('data-date-status role="status"')==2
    assert 'aria-haspopup="dialog"' in page
    assert 'Type YYYY-MM-DD or open the calendar.' in page
    assert '/static/history_dates.js' in page


def test_recent_dates_and_reference_selector_match_lesson_numbers(client):
    catalog=client.get('/api/history/snapshots').json()
    assert catalog['example_defaults']['first']=='2026-11-05'
    assert catalog['example_defaults']['second']=='2026-11-06'
    assert catalog['reference_defaults']['first']=='2025-02-14'
    for slug in ('par-yields-and-quotes','observation-and-publication','revisions-and-vintages'):
        text=client.get('/lessons/'+slug).text
        assert 'value="2026-11-05"' in text and 'value="2026-11-06"' in text
    lesson=client.get('/lessons/par-yields-and-quotes').text
    assert 'name="history_sample"' in lesson
    assert 'Try November 7' in lesson
    assert '38 bp' in lesson and '35 bp' in lesson
    assert '1.5-month' in lesson and '4.41%' in lesson
    revision=client.get('/lessons/revisions-and-vintages').text
    assert '4.96%' in revision and '+7 bp' in revision


@pytest.mark.parametrize('payload', [
    {'year':1989,'month':10}, {'year':2026,'month':13}, {'year':9999,'month':1},
    {'year':'2026','month':10}, {'year':2026,'month':10,'url':'https://example.com'},
])
def test_month_request_validation(client,payload):
    payload={'base_snapshot_id':SnapshotStore().viewer['id'],**payload}
    assert client.post('/api/history/month-load',json=payload).status_code==422


def test_month_job_deduplicates_and_matches_python(client,monkeypatch):
    from threading import Event
    release=Event()
    original=SnapshotStore.ensure_month
    calls=[]
    def local(self,*args,**kwargs):
        calls.append(args)
        release.wait(2)
        return original(self,*args,**kwargs)
    monkeypatch.setattr(SnapshotStore,'ensure_month',local)
    catalog=client.get('/api/history/snapshots').json()
    payload={'base_snapshot_id':catalog['viewer_snapshot_id'],'year':2026,'month':10}
    job=client.post('/api/history/month-load',json=payload).json()['job_id']
    try:
        assert client.post('/api/history/month-load',json=payload).json()['job_id']==job
    finally:
        release.set()
    for _ in range(100):
        result=client.get('/api/history/jobs/'+job).json()
        if result['state']!='running':break
        time.sleep(.01)
    assert result['state']=='complete' and result['cache_hit']
    assert len(calls)==1
    params={'snapshot_id':result['snapshot_id'],'first':'2026-10-30','second':'2026-11-06'}
    data=client.get('/api/history/compare',params=params).json()
    del data['data_kind']
    del data['revision_scenario']
    assert data==compare(SnapshotStore().viewer,params['first'],params['second'])
    assert 'key' not in result
    assert client.post('/api/history/month-load',json={**payload,'base_snapshot_id':'0'*64}).status_code==404


def test_lessons_and_standalone_viewer_have_automatic_month_controls(client):
    tool=client.get('/tools/treasury-history').text
    assert 'data-month-status' in tool and 'data-retry-month' in tool
    assert '/static/history_months.js' in tool
    for slug in ('par-yields-and-quotes','observation-and-publication','revisions-and-vintages'):
        page=client.get('/lessons/'+slug).text
        assert 'data-month-status' in page and 'data-retry-month' in page
        assert 'data-lesson-example' in page and 'data-pinned="true"' in page
        assert 'Reset example restores' in page


def test_revision_description_uses_the_selected_observation_and_python_shift(client):
    store=SnapshotStore()
    params={'snapshot_id':store.viewer['id'],'first':'2026-11-06','second':'2026-10-30'}
    observed=client.get('/api/history/compare',params=params).json()
    scenario=observed['revision_scenario']
    assert scenario=={'date':'2026-10-30','change_bp':10,
                      'original':{'original_percent':'4.94','rate':.0494},
                      'revised':{'original_percent':'5.04','rate':.0504},'applied':False}
    revised=client.get('/api/history/compare',params={**params,'hypothetical_revision':True}).json()
    assert revised['revision_scenario']['applied']
    assert revised['spread_bp']==[35,48]
    assert revised['spread_change_bp']==13
    assert store.get(store.viewer['id'])['rows']['2026-10-30']['BC_10YEAR']['original_percent']=='4.94'


@pytest.mark.parametrize('second',['2026-11-07','2026-12-01'])
def test_hypothetical_revision_without_published_row_invents_nothing(client,second):
    params={'snapshot_id':SnapshotStore().fixture['id'],'first':'2026-11-05','second':second,'hypothetical_revision':True}
    data=client.get('/api/history/compare',params=params).json()
    assert data['revision_scenario']=={'date':second,'change_bp':10,'original':None,'revised':None,'applied':False}
    assert data['spread_change_bp'] is None
    assert next(t for t in data['tenors'] if t['field']=='BC_10YEAR')['second'] is None


@pytest.mark.parametrize('original',[None,{'original_percent':'0','rate':0}])
def test_revision_proposal_distinguishes_missing_tenor_and_genuine_zero(client,monkeypatch,original):
    snapshot=SnapshotStore().fixture
    snapshot['rows']['2026-11-06']['BC_10YEAR']=original
    class LocalStore:
        def get(self,identifier):
            return snapshot
    monkeypatch.setattr(history_api,'store',LocalStore)
    data=client.get('/api/history/compare',params={'snapshot_id':snapshot['id'],'first':'2026-11-05','second':'2026-11-06','hypothetical_revision':True}).json()
    scenario=data['revision_scenario']
    if original is None:
        assert not scenario['applied'] and scenario['revised'] is None
    else:
        assert scenario['applied'] and scenario['original']==original
        assert scenario['revised']=={'original_percent':'0.10','rate':.001}


def test_local_assets_have_content_versions_and_serve_offline(client):
    from hashlib import sha256
    import re
    page=client.get('/lessons/revisions-and-vintages').text
    assets=re.findall(r'(?:src|href)="(/static/([^/]+\.(?:js|css))\?v=([a-f0-9]{16}))"',page)
    assert any(name=='history.js' for _,name,_ in assets)
    for url,name,version in assets:
        response=client.get(url)
        assert response.status_code==200
        assert version==sha256(response.content).hexdigest()[:16]


def test_lesson_month_load_reuses_bundled_october_and_preserves_pinned_example(client,monkeypatch):
    from filab.data import store as data_store
    def forbidden(*args):
        raise AssertionError('Bundled October must work offline')
    monkeypatch.setattr(data_store,'fetch_month',forbidden)
    pinned=SnapshotStore().fixture['id']
    job=client.post('/api/history/month-load',json={'year':2026,'month':10,'base_snapshot_id':pinned}).json()['job_id']
    for _ in range(100):
        state=client.get('/api/history/jobs/'+job).json()
        if state['state']!='running':break
        time.sleep(.01)
    assert state['state']=='complete' and state['cache_hit']
    dates=client.get('/api/history/snapshots/'+state['snapshot_id']+'/dates').json()
    assert '2026-10-30' in dates['published_dates'] and len(dates['published_dates'])==26
    original=client.get('/api/history/snapshots/'+pinned).json()
    assert len(original['rows'])==5
    assert original['example']['first']=='2026-11-05'
    assert compare(original,'2026-11-05','2026-11-06')['spread_change_bp']==-3
