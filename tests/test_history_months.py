"""Monthly cache recovery, period provenance, and immutable view publication."""
from copy import deepcopy
from datetime import date
from pathlib import Path
from threading import Thread, Event
from xml.etree import ElementTree as ET

import pytest

from filab.data import store as module, treasury
from filab.data.store import SnapshotStore
from filab.data.treasury import DataError, ATOM, DATA, digest, utc_now, compare

FOLDER = Path(treasury.__file__).parent / 'fixtures'


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'today', lambda: date(2026, 11, 7))
    monkeypatch.setattr(treasury, 'today', lambda: date(2026, 11, 7))
    return SnapshotStore(tmp_path / 'cache')


def acquire(month, *, revised=False, empty=False):
    raw = (FOLDER / f'treasury-cache-{month}.xml').read_bytes()
    root = ET.fromstring(raw)
    if revised:
        root.findall(ATOM + 'entry')[-1].find('.//' + DATA + 'BC_10YEAR').text = '5.04'
    if empty:
        for entry in root.findall(ATOM + 'entry'):
            root.remove(entry)
    if revised or empty:
        raw = ET.tostring(root)
    return raw, {'sha256': digest(raw), 'retrieved_at': utc_now(), 'url': treasury.source_url(month=month)}


def forbidden(*args):
    raise AssertionError('Unexpected network request')


def test_starter_october_november_and_independent_october_benchmark(store):
    sample = store.get(store.catalog()['viewer_snapshot_id'])
    assert len(sample['rows']) == 26
    assert sample['coverage'] == [['2026-10-01', '2026-11-07']]
    result = compare(sample, '2026-10-30', '2026-11-06')
    # Treasury's published October table: 4.56 / 4.94 percent. November: 4.51 / 4.86.
    assert result['spread_bp'] == [38, 35]
    assert result['spread_change_bp'] == -3
    assert result['tenors'][7]['change_bp'] == -5
    assert result['tenors'][11]['change_bp'] == -8
    assert not store.root.exists()


def test_two_month_imports_preserve_each_source_and_reuse_identical_snapshot(store):
    base = store.fixture['id']
    first = store.ensure_month(2026, 10, base, force=True, fetcher=lambda *_: acquire('202610'))
    both = store.ensure_month(2026, 11, first['snapshot_id'], force=True, fetcher=lambda *_: acquire('202611'))
    assert both['snapshot_id'] == store.viewer['id']
    sample = store.get(both['snapshot_id'])
    assert len(sample['sources']) == 2
    for day in sample['rows']:
        contributing = [s for s in sample['sources'].values() if any(a <= day <= b for a, b in s['coverage'])]
        assert len(contributing) == 1
        assert f"month={day[:7].replace('-', '')}" in contributing[0]['url']
    cached = store.ensure_month(2026, 10, sample['id'], fetcher=forbidden)
    assert cached['snapshot_id'] == sample['id'] and cached['cache_hit']
    repeated = store.ensure_month(2026, 10, sample['id'], force=True, fetcher=lambda *_: acquire('202610'))
    assert repeated['snapshot_id'] == sample['id']
    assert len(store.catalog()['acquisitions']) == 3


def test_revision_old_view_and_year_refresh_after_months(store):
    old = store.viewer['id']
    revised = store.ensure_month(2026, 10, old, force=True, fetcher=lambda *_: acquire('202610', revised=True))['snapshot_id']
    assert revised != old
    assert compare(store.get(old), '2026-10-30', '2026-11-06')['spread_bp'] == [38, 35]
    assert compare(store.get(revised), '2026-10-30', '2026-11-06')['spread_bp'] == [48, 35]
    # Complete year replacement removes monthly provenance and retains old snapshots.
    year = store.refresh(2026, 2026, fetcher=lambda *_: acquire('202611'))
    assert store.get(year)['coverage'] == [['2026-01-01', '2026-11-07']]
    assert len(store.get(year)['sources']) == 1
    assert len(store.get(revised)['rows']) == 26


def test_failed_month_keeps_active_and_cached_dates_even_when_current_cache_stale(store):
    store.seed_bundled_history()
    before = store.catalog()['active_snapshot_id']
    result = store.ensure_month(2026, 11, before, force=True, fetcher=lambda *_: (b'<html/>', {'sha256': digest(b'<html/>'), 'url': 'test', 'retrieved_at': utc_now()}))
    assert result['snapshot_id'] == before and result['warning']
    assert store.catalog()['active_snapshot_id'] == before
    def failure(*args):
        raise TimeoutError('offline')
    # No September coverage exists anywhere locally.
    with pytest.raises(TimeoutError):
        store.ensure_month(2026, 9, before, fetcher=failure)
    assert store.catalog()['active_snapshot_id'] == before
    assert len(store.get(before)['rows']) == 26


def test_successful_empty_month_is_coverage_without_observations(store):
    result = store.ensure_month(2026, 10, store.fixture['id'], force=True, fetcher=lambda *_: acquire('202610', empty=True))
    sample = store.get(result['snapshot_id'])
    assert len(sample['rows']) == 5
    assert compare(sample, '2026-10-30', '2026-11-06')['date_states'] == ['no_published_row', 'published']
    assert compare(sample, '2026-12-01', '2026-11-06')['date_states'][0] == 'outside_coverage'
    store.ensure_month(2026, 10, sample['id'], fetcher=forbidden)


def test_current_month_hourly_check_and_partial_offline_fallback(store, monkeypatch):
    stale = deepcopy(store.viewer)
    for source in stale['sources'].values():
        source['retrieved_at'] = '2026-11-01T00:00:00Z'
    store.viewer = stale
    monkeypatch.setattr(store, 'get', lambda identifier: deepcopy(stale) if identifier == stale['id'] else SnapshotStore.get(store, identifier))
    calls = []
    def fetch(year, month):
        calls.append((year, month))
        return acquire('202611')
    result = store.ensure_month(2026, 11, stale['id'], fetcher=fetch)
    assert calls == [(2026, 11)] and not result['cache_hit']
    # Original vintage is not rewritten just because an acquisition is newer.
    assert store.get(stale['id'])['sources'] == stale['sources']
    # Freshness uses latest successful acquisition separately from immutable vintage.
    store.ensure_month(2026, 11, result['snapshot_id'], fetcher=forbidden)


def test_concurrent_clients_share_acquisition_and_preserve_working_union(store):
    # Use an uncached historical month to exercise lock + cache recheck.
    raw, metadata = acquire('202610')
    raw = raw.replace(b'2026-10-', b'2026-09-')
    # October31 absent, dates all <=30; source is artificial for concurrency only.
    metadata = {**metadata, 'sha256': digest(raw)}
    entered, release = Event(), Event()
    calls, results, errors = [], [], []
    def fetch(*args):
        calls.append(args); entered.set(); release.wait(2)
        return raw, metadata
    def worker():
        try:
            results.append(store.ensure_month(2026, 9, store.fixture['id'], fetcher=fetch))
        except Exception as exc:
            errors.append(exc)
    one, two = Thread(target=worker), Thread(target=worker)
    one.start(); assert entered.wait(2); two.start(); release.set(); one.join(4); two.join(4)
    assert not errors and len(results) == 2 and len(calls) == 1
    assert results[0]['snapshot_id'] == results[1]['snapshot_id']
    active = store.get(store.catalog()['active_snapshot_id'])
    assert '2026-09-01' in active['rows'] and '2026-10-30' in active['rows']


@pytest.mark.parametrize('year,month', [(1989,12),(2026,12),(2027,1),(2026,0),(2026,13),(True,1)])
def test_future_and_invalid_months_do_not_write(store, year, month):
    with pytest.raises(DataError):
        store.ensure_month(year, month, store.fixture['id'], fetcher=forbidden)
    assert not store.root.exists()


def test_partial_current_cache_does_not_claim_new_day_after_failed_check(store, monkeypatch):
    monkeypatch.setattr(module, 'today', lambda: date(2026, 11, 8))
    monkeypatch.setattr(treasury, 'today', lambda: date(2026, 11, 8))
    before = store.catalog()['active_snapshot_id']
    def offline(*args):
        raise DataError('offline')
    result = store.ensure_month(2026, 11, before, fetcher=offline)
    assert result['warning'] and result['snapshot_id'] == before
    assert compare(store.get(before), '2026-11-08', '2026-11-06')['date_states'][0] == 'outside_coverage'
    assert store.catalog()['active_snapshot_id'] == before


def test_newer_annual_source_wins_over_old_month_check(store):
    # Artificial 2025 dates exercise precedence without changing teaching data.
    raw, metadata = acquire('202610')
    raw = raw.replace(b'2026-10-', b'2025-10-')
    old_metadata = {**metadata, 'sha256': digest(raw), 'retrieved_at': '2026-01-01T00:00:00Z'}
    store.ensure_month(2025, 10, store.fixture['id'], force=True, fetcher=lambda *_: (raw, old_metadata))
    root = ET.fromstring(raw)
    root.findall(ATOM + 'entry')[-1].find('.//' + DATA + 'BC_10YEAR').text = '5.04'
    revised = ET.tostring(root)
    new_metadata = {**metadata, 'sha256': digest(revised), 'retrieved_at': utc_now()}
    store.refresh(2025, 2025, lambda *_: (revised, new_metadata))
    result = store.ensure_month(2025, 10, store.fixture['id'], fetcher=forbidden)
    assert compare(store.get(result['snapshot_id']), '2025-10-30', '2026-11-06')['spread_bp'][0] == 48


def test_interrupted_month_acquisition_keeps_active_pointer(store):
    before = store.catalog()['active_snapshot_id']
    def interrupted(*args):
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        store.ensure_month(2026, 9, before, fetcher=interrupted)
    assert store.catalog()['active_snapshot_id'] == before
