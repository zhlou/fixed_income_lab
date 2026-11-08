"""Bundled HTTP parity, calendars, and historical-data lesson navigation."""
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


def test_curve_lesson_and_full_history_viewer(client):
    page=client.get('/lessons/par-yields-and-quotes')
    assert page.status_code==200
    for text in ['data-history', 'data-pinned="true"', 'class="math block"', 'class="exercise-answer"', '/static/history.js']:
        assert text in page.text
    assert 'data-refresh-form' not in page.text
    assert 'name="history_sample"' not in page.text
    assert 'name="maturity_scale"' not in page.text
    tool=client.get('/tools/treasury-history').text
    for text in ['data-refresh-form', 'data-snapshot-options', 'name="history_sample"', 'name="maturity_scale"', 'name="revision"', 'data-missing-date']:
        assert text in tool


def test_retired_lessons_are_removed_from_the_course(client):
    for slug in ['bond-basics','bond-pricing-lab','yield-to-maturity','treasury-bill-yields',
                 'macaulay-duration','coupons-and-return','pull-to-par',
                 'observation-and-publication','revisions-and-vintages']:
        assert client.get('/lessons/'+slug).status_code==404
        assert f'href="/lessons/{slug}"' not in client.get('/').text
    page=client.get('/lessons/par-yields-and-quotes').text
    assert 'LESSON 02' in page
    assert 'href="/lessons/modified-duration-dv01" class="next-lesson"' in page


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


def test_history_dates_have_named_calendar_buttons_and_live_status(client):
    page=client.get('/tools/treasury-history').text
    assert page.count('data-history-date>')==2
    assert page.count('data-open-calendar')==2
    assert page.count('data-date-status role="status"')==2
    assert 'aria-haspopup="dialog"' in page
    assert 'Type YYYY-MM-DD or open the calendar.' in page
    assert '/static/history_dates.js' in page


def test_recent_dates_match_the_worked_spread_example(client):
    catalog=client.get('/api/history/snapshots').json()
    assert catalog['example_defaults']['first']=='2026-11-05'
    assert catalog['example_defaults']['second']=='2026-11-06'
    assert catalog['reference_defaults']['first']=='2025-02-14'
    page=client.get('/lessons/par-yields-and-quotes').text
    assert 'value="2026-11-05"' in page and 'value="2026-11-06"' in page
    assert '38 basis points' in page and '35 bp' in page
    assert 'name="history_sample"' in client.get('/tools/treasury-history').text


def test_curve_lesson_and_viewer_have_automatic_month_controls(client):
    for path in ['/tools/treasury-history','/lessons/par-yields-and-quotes']:
        page=client.get(path).text
        assert 'data-month-status' in page and 'data-retry-month' in page
        assert '/static/history_months.js' in page
    page=client.get('/lessons/par-yields-and-quotes').text
    assert 'data-lesson-example' in page and 'data-pinned="true"' in page


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
    monkeypatch.setattr(history_api,'bundled',lambda identifier:snapshot)
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
    page=client.get('/lessons/par-yields-and-quotes').text
    assets=re.findall(r'(?:src|href)="(/static/([^/]+\.(?:js|css))\?v=([a-f0-9]{16}))"',page)
    assert any(name=='history.js' for _,name,_ in assets)
    for url,name,version in assets:
        response=client.get(url)
        assert response.status_code==200
        assert version==sha256(response.content).hexdigest()[:16]
