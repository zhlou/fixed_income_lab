"""Browser datasets use Python math without reading or changing server history."""
import base64
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from filab.web.app import app
from filab.data.browser import bundled_archive, export_legacy, validate_archive
from filab.data.store import SnapshotStore
from filab.data.treasury import digest, snapshot_id, source_url, utc_now


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('FILAB_DATA_DIR', str(tmp_path / 'unused'))
    def forbidden(*args, **kwargs):
        raise AssertionError('Web requests must never fetch Treasury or write server history')
    monkeypatch.setattr(SnapshotStore, 'refresh', forbidden)
    monkeypatch.setattr(SnapshotStore, 'ensure_month', forbidden)
    monkeypatch.setattr('urllib.request.urlopen', forbidden)
    monkeypatch.setattr('filab.data.treasury.urlopen', forbidden)
    return TestClient(app)


def acquisition():
    raw = (Path(__file__).parents[1] / 'src/filab/data/fixtures/treasury-202502.xml').read_bytes()
    return {'snapshot': SnapshotStore().viewer, 'year': 2025, 'month': 2,
            'raw_base64': base64.b64encode(raw).decode(), 'retrieved_at': utc_now()}


def test_normalize_compare_and_archive_roundtrip_without_server_storage(client, tmp_path):
    before = client.get('/api/history/snapshots').json()
    inputs = acquisition()
    response = client.post('/api/history/normalize', json=inputs)
    assert response.status_code == 200, response.text
    snapshot = response.json()['snapshot']
    result = client.post('/api/history/compare', json={'snapshot': snapshot, 'first': '2025-02-14', 'second': '2025-02-18'}).json()
    assert result['spread_bp'] == [21, 26]
    assert result['spread_change_bp'] == 5
    assert result['tenors'][1]['first'] is None  # missing 1.5-month observation
    archive = bundled_archive()
    archive['snapshots'] = [snapshot]
    archive['raw'][response.json()['sha256']] = inputs['raw_base64']
    checked = client.post('/api/history/validate-archive', json=archive)
    assert checked.status_code == 200, checked.text
    assert checked.json()['snapshots'][0]['id'] == snapshot['id']
    assert client.get('/api/history/snapshots').json() == before
    assert not (tmp_path / 'unused').exists()
    assert client.get('/api/history/snapshots/' + snapshot['id']).status_code == 404


@pytest.mark.parametrize('path', ['/refresh', '/month-load', '/refresh/old', '/jobs/old'])
def test_disk_refresh_interfaces_are_retired(client, path):
    response = client.post('/api/history' + path, json={}) if path in ('/refresh', '/month-load') else client.get('/api/history' + path)
    assert response.status_code == 410


@pytest.mark.parametrize('change', [
    {'year': 1989}, {'year': 9999}, {'year': '2025'}, {'month': 13},
    {'raw_base64': 'bad base64'}, {'raw_base64': base64.b64encode(b'<wrong/>').decode()},
    {'retrieved_at': 'invalid'}, {'url': 'https://example.com'},
])
def test_invalid_downloads_are_rejected(client, change):
    assert client.post('/api/history/normalize', json={**acquisition(), **change}).status_code == 422


@pytest.mark.parametrize('tamper', ['hash', 'rate', 'raw', 'missing_raw', 'coverage', 'source_url'])
def test_import_checks_provenance_and_normalized_values(client, tamper):
    archive = bundled_archive()
    s = archive['snapshots'][0]
    if tamper == 'hash': s['id'] = '0' * 64
    if tamper == 'rate': s['rows']['2026-11-06']['BC_10YEAR']['rate'] = .10
    if tamper == 'raw': archive['raw'][next(iter(archive['raw']))] = base64.b64encode(b'other bytes').decode()
    if tamper == 'missing_raw': archive['raw'] = {}
    if tamper == 'coverage': s['coverage'] = [['2026-11-02', '2026-11-07']]
    if tamper == 'source_url': next(iter(s['sources'].values()))['url'] = 'javascript:alert(1)'
    assert client.post('/api/history/validate-archive', json=archive).status_code == 422


def test_no_data_keeps_the_available_date_and_no_two_date_change(client):
    snapshot = SnapshotStore().fixture
    result = client.post('/api/history/compare', json={'snapshot': snapshot, 'first': '2019-01-02', 'second': '2026-11-06'}).json()
    assert result['date_states'] == ['outside_coverage', 'published']
    assert result['spread_bp'] == [None, 35]
    assert result['spread_change_bp'] is None
    assert all(t['first'] is None and t['change_bp'] is None for t in result['tenors'])
    assert all(t['second'] is not None for t in result['tenors'])


def test_cached_bundled_month_can_be_overlaid_without_acquisition(client):
    store = SnapshotStore()
    response = client.post('/api/history/overlay', json={'snapshot': store.fixture, 'patch': store.viewer, 'year': 2026, 'month': 10})
    assert response.status_code == 200, response.text
    snapshot = response.json()
    assert len(snapshot['rows']) == 26
    assert len(store.fixture['rows']) == 5
    archive = bundled_archive()
    archive['snapshots'] = [snapshot]
    assert validate_archive(archive)['snapshots'][0]['id'] == snapshot['id']


def test_legacy_export_is_read_only_and_can_be_imported(client, tmp_path):
    root = tmp_path / 'legacy'
    store = SnapshotStore(root)
    raw = base64.b64decode(acquisition()['raw_base64'])
    # Existing domain API remains available for independent local research scripts.
    # Seed a representative old cache without invoking the web acquisition paths.
    store.root.mkdir()
    store._prepare()
    metadata = {'url': source_url(month=202502), 'retrieved_at': utc_now(), 'sha256': digest(raw),
                'coverage': [['2025-02-01', '2025-02-28']]}
    from filab.data.treasury import normalize, SERIES, NORMALIZER_VERSION
    from datetime import date
    rows = normalize(raw, date(2025,2,1), date(2025,2,28))
    snapshot = {'id': snapshot_id(rows, metadata['coverage']), 'rows': rows, 'coverage': metadata['coverage'],
                'sources': {'2025': metadata}, 'series': SERIES, 'rate_type': 'nominal_par',
                'normalizer_version': NORMALIZER_VERSION, 'created_at': utc_now()}
    store._raw(raw, metadata)
    store._commit([snapshot], snapshot['id'])
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}
    archive = export_legacy(root)
    assert snapshot['id'] in [s['id'] for s in archive['snapshots']]
    assert client.post('/api/history/validate-archive', json=archive).status_code == 200
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob('*') if p.is_file()}


def test_upload_limit_applies_before_json_parsing(client):
    response = client.post('/api/history/normalize', content=b' ' * 32_000_001,
                           headers={'Content-Type': 'application/json'})
    assert response.status_code == 413


def test_recomputed_snapshot_hash_cannot_hide_a_source_mismatch(client):
    archive = bundled_archive()
    snapshot = archive['snapshots'][0]
    snapshot['rows']['2026-11-06']['BC_10YEAR'] = {'original_percent': '5.00', 'rate': .05}
    snapshot['id'] = snapshot_id(snapshot['rows'], snapshot['coverage'])
    response = client.post('/api/history/validate-archive', json=archive)
    assert response.status_code == 422
    assert 'source responses' in response.json()['detail']
