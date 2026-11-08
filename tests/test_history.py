"""Source-backed observations, sample membership, and atomic refresh behavior."""
from copy import deepcopy
from datetime import date
from pathlib import Path
import json
from xml.etree import ElementTree as ET

import pytest

from filab.data.store import SnapshotStore, RefreshBusy
from filab.data.treasury import (ATOM, DATA, META, DataError, compare, digest,
                                 normalize, pinned_snapshot, source_url, utc_now)

RAW = (Path(__file__).resolve().parents[1] / 'src/filab/data/fixtures/treasury-202502.xml').read_bytes()
START, END = date(2025, 2, 1), date(2025, 2, 28)


def acquisition(raw=RAW, year=2025):
    return raw, {'url': source_url(year=year), 'retrieved_at': utc_now(), 'sha256': digest(raw)}


def changed(raw=RAW, value='4.65', field='BC_10YEAR'):
    root = ET.fromstring(raw)
    for row in root.findall(ATOM + 'entry'):
        properties = row.find(f'{ATOM}content/{META}properties')
        if properties.findtext(DATA + 'NEW_DATE').startswith('2025-02-18'):
            properties.find(DATA + field).text = value
    return ET.tostring(root)


def test_official_fixture_matches_independent_published_table():
    snapshot = pinned_snapshot('series-introduction')
    assert len(snapshot['rows']) == 19
    result = compare(snapshot, '2025-02-14', '2025-02-18')
    # Treasury's displayed hundredths of a percent are exact decimal inputs.
    assert result['spread_bp'] == [21, 26]
    assert result['spread_change_bp'] == 5
    assert len(result['spread_sample_dates']) == 19
    values = {t['field']: t for t in result['tenors']}
    assert values['BC_2YEAR']['first']['rate'] == pytest.approx(.0426, abs=1e-15)
    assert values['BC_10YEAR']['second']['rate'] == pytest.approx(.0455, abs=1e-15)
    assert values['BC_2YEAR']['change_bp'] == 3
    assert values['BC_10YEAR']['change_bp'] == 8
    assert values['BC_1_5MONTH']['first'] is None
    assert values['BC_1_5MONTH']['second']['rate'] == pytest.approx(.0441, abs=1e-15)
    assert values['BC_1_5MONTH']['change_bp'] is None
    assert result['missing_counts']['1.5 months'] == 10
    assert result['publication_time'] is None


def test_missing_null_zero_and_common_date_sample():
    raw = changed(value='0', field='BC_2YEAR')
    rows = normalize(raw, START, END)
    assert rows['2025-02-18']['BC_2YEAR']['rate'] == 0
    root = ET.fromstring(raw)
    row = next(p for p in root.iter(META + 'properties') if p.findtext(DATA + 'NEW_DATE').startswith('2025-02-18'))
    row.find(DATA + 'BC_10YEAR').set(META + 'null', 'true')
    snapshot = deepcopy(pinned_snapshot('series-introduction'))
    snapshot['rows'] = normalize(ET.tostring(root), START, END)
    result = compare(snapshot, '2025-02-18', '2025-02-18')
    assert result['spread_bp'] == [None, None]
    assert len(result['spread_sample_dates']) == 18
    assert result['spread_excluded_dates'] == ['2025-02-18']
    assert next(t for t in result['tenors'] if t['field'] == 'BC_2YEAR')['change_bp'] == 0


@pytest.mark.parametrize('day,state', [('2025-02-17','no_published_row'), ('2025-02-15','no_published_row'), ('2025-03-03','outside_coverage')])
def test_exact_dates_never_shift(day, state):
    result = compare(pinned_snapshot('series-introduction'), day, '2025-02-18')
    assert result['dates'][0] == day
    assert result['date_states'] == [state, 'published']
    assert result['spread_bp'] == [None, 26]
    assert result['spread_change_bp'] is None
    assert not result['common_tenors']


def test_reverse_dates_and_equal_dates():
    snapshot = pinned_snapshot('series-introduction')
    assert compare(snapshot, '2025-02-18', '2025-02-14')['spread_change_bp'] == -5
    result = compare(snapshot, '2025-02-14', '2025-02-14')
    assert result['spread_change_bp'] == 0
    assert all(t['change_bp'] == 0 for t in result['tenors'] if t['included'])


@pytest.mark.parametrize('raw', [b'<html>Access denied</html>', b'bad', b'<!DOCTYPE feed><feed/>', RAW.replace(b'4.37', b'NaN', 1), RAW.replace(b'BC_1MONTH', b'BC_99MONTH')])
def test_invalid_or_changed_source_rejected(raw):
    with pytest.raises(DataError):
        normalize(raw, START, END)


def test_empty_out_of_range_and_conflicting_duplicate_rejected():
    root = ET.fromstring(RAW)
    root.append(deepcopy(root.find(ATOM + 'entry')))
    assert len(normalize(ET.tostring(root), START, END)) == 19
    root.findall(ATOM + 'entry')[-1].find('.//' + DATA + 'BC_2YEAR').text = '9.99'
    with pytest.raises(DataError, match='Conflicting duplicate'):
        normalize(ET.tostring(root), START, END)
    with pytest.raises(DataError, match='outside'):
        normalize(RAW, date(2024, 1, 1), date(2024, 12, 31))
    for entry in root.findall(ATOM + 'entry'):
        root.remove(entry)
    with pytest.raises(DataError, match='no observations'):
        normalize(ET.tostring(root), START, END)


def test_readonly_fresh_offline_store_never_creates_cache(tmp_path):
    root = tmp_path / 'not-created'
    store = SnapshotStore(root)
    identifier = store.catalog()['bundled_snapshot_id']
    assert compare(store.get(identifier), '2026-11-05', '2026-11-06')['spread_change_bp'] == -3
    assert not root.exists()


def test_import_idempotency_revision_old_snapshot_and_raw_preservation(tmp_path):
    store = SnapshotStore(tmp_path)
    first = store.refresh(2025, 2025, lambda year: acquisition())
    second = store.refresh(2025, 2025, lambda year: acquisition(RAW.replace(b'2026-11-07T01:02:07Z', b'2026-11-08T01:02:07Z')))
    assert first == second
    new_raw = changed()
    third = store.refresh(2025, 2025, lambda year: acquisition(new_raw))
    assert third != first
    assert compare(store.get(first), '2025-02-14', '2025-02-18')['spread_change_bp'] == 5
    assert compare(SnapshotStore(tmp_path).get(third), '2025-02-14', '2025-02-18')['spread_change_bp'] == 15
    assert (tmp_path / 'raw' / (digest(RAW) + '.xml')).read_bytes() == RAW
    assert len(store.catalog()['acquisitions']) == 3
    assert all((tmp_path / 'raw' / (m['sha256'] + '.xml')).exists() for m in store.catalog()['acquisitions'])


def test_year_merge_and_failed_range_preserves_active_snapshot(tmp_path):
    store = SnapshotStore(tmp_path)
    first = store.refresh(2025, 2025, lambda year: acquisition())
    raw24 = RAW.replace(b'2025-02-', b'2024-02-')
    both = store.refresh(2024, 2024, lambda year: acquisition(raw24, year))
    assert len(store.get(both)['rows']) == 38 + len(store.viewer['rows'])
    assert store.get(both)['coverage'] == [['2024-01-01','2025-12-31']] + store.viewer['coverage']
    def failure(year):
        if year == 2025:
            raise TimeoutError('network failure')
        return acquisition(raw24, year)
    with pytest.raises(TimeoutError):
        store.refresh(2024, 2025, failure)
    assert store.catalog()['active_snapshot_id'] == both
    with pytest.raises(DataError):
        store.refresh(2024, 2025, lambda year: acquisition(b'<html/>', year))
    assert store.catalog()['active_snapshot_id'] == both
    assert store.get(first)['rows']['2025-02-18']['BC_10YEAR']['rate'] == .0455


def test_interruption_and_cross_process_lock(tmp_path):
    store = SnapshotStore(tmp_path)
    identifier = store.refresh(2025, 2025, lambda year: acquisition())
    def interrupted(year):
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        store.refresh(2025, 2025, interrupted)
    assert store.catalog()['active_snapshot_id'] == identifier
    def nested(year):
        with pytest.raises(RefreshBusy):
            SnapshotStore(tmp_path).refresh(2025, 2025, lambda y: acquisition())
        return acquisition()
    assert store.refresh(2025, 2025, nested) == identifier


@pytest.mark.parametrize('start,end', [(1989,2025),(2025,2024),(2025,9999)])
def test_invalid_year_ranges(start, end, tmp_path):
    with pytest.raises(DataError):
        SnapshotStore(tmp_path).refresh(start, end)
    assert not (tmp_path/'catalog.sqlite3').exists()


def test_reads_during_import_see_previous_snapshot_and_new_instance_reads_old(tmp_path):
    store=SnapshotStore(tmp_path)
    original=store.catalog()['active_snapshot_id']
    def fetch(year):
        assert SnapshotStore(tmp_path).catalog()['active_snapshot_id']==original
        return acquisition(RAW.replace(b'2025-02-',f'{year}-02-'.encode()),year)
    result=store.refresh(2024,2025,fetch)
    assert result!=original
    assert SnapshotStore(tmp_path).get(original)['bundled']


def test_hash_mismatch_and_extreme_value_rejected(tmp_path):
    store=SnapshotStore(tmp_path)
    raw, metadata=acquisition()
    metadata['sha256']='0'*64
    with pytest.raises(DataError,match='hash'):
        store.refresh(2025,2025,lambda year:(raw,metadata))
    with pytest.raises(DataError,match='precision'):
        normalize(changed(value='1e999'),START,END)


def test_recent_official_example_and_partial_month_boundary():
    snapshot=pinned_snapshot()
    assert len(snapshot['rows'])==5
    assert snapshot['coverage']==[['2026-11-01','2026-11-07']]
    result=compare(snapshot,'2026-11-05','2026-11-06')
    # Treasury's November table: 4.46/4.84 then 4.51/4.86 percent.
    assert result['spread_bp']==[38,35]
    assert result['spread_change_bp']==-3
    values={row['field']:row for row in result['tenors']}
    assert values['BC_2YEAR']['first']['rate']==pytest.approx(.0446,abs=1e-15)
    assert values['BC_2YEAR']['second']['rate']==pytest.approx(.0451,abs=1e-15)
    assert values['BC_10YEAR']['first']['rate']==pytest.approx(.0484,abs=1e-15)
    assert values['BC_10YEAR']['second']['rate']==pytest.approx(.0486,abs=1e-15)
    assert values['BC_2YEAR']['change_bp']==5
    assert values['BC_10YEAR']['change_bp']==2
    assert not result['excluded_tenors']
    assert compare(snapshot,'2026-11-07','2026-11-06')['date_states']==['no_published_row','published']
    assert compare(snapshot,'2026-11-08','2026-11-06')['date_states']==['outside_coverage','published']
    assert compare(snapshot,'2026-11-04','2026-11-05')['spread_change_bp']==6


def test_both_bundled_examples_reopen_offline_without_a_catalog(tmp_path):
    store=SnapshotStore(tmp_path/'not-created')
    catalog=store.catalog()
    assert len(catalog['snapshots'])==3
    assert catalog['example_defaults']['first']=='2026-11-05'
    reference=store.get(catalog['reference_snapshot_id'])
    assert reference['id']=='0cc891c2abf9e5793c54012eaa8344ba3e8eeeab522b8c57eda4dfc54b525651'
    assert compare(reference,'2025-02-14','2025-02-18')['spread_change_bp']==5
    assert not store.database.exists()
