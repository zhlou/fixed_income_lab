"""Immutable snapshots, exact raw bytes, and an atomic active pointer.

Bundled examples are always readable without initializing a writable cache.
One file lock serializes refreshes across processes. SQLite commits the new
snapshot and active pointer together only after the acquired period validates.
"""
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

from .treasury import (DataError, SERIES, NORMALIZER_VERSION, digest,
                       encode, fetch_year, fetch_month, month_bounds, bundled_history, pinned_snapshot, snapshot_id, today, utc_now)
from .treasury import normalize


def intervals(values):
    """Canonical union of inclusive date intervals."""
    result = []
    for start, end in sorted(values):
        if result and date.fromisoformat(start) <= date.fromisoformat(result[-1][1]) + timedelta(days=1):
            result[-1][1] = max(end, result[-1][1])
        else:
            result.append([start, end])
    return result


def subtract(values, start, end):
    result = []
    for a, b in values:
        if b < start or a > end:
            result.append([a, b])
        else:
            if a < start:
                result.append([a, (date.fromisoformat(start) - timedelta(days=1)).isoformat()])
            if b > end:
                result.append([(date.fromisoformat(end) + timedelta(days=1)).isoformat(), b])
    return result


def source_periods(snapshot):
    """Read legacy year metadata and newer per-response coverage alike."""
    sources = {}
    for key, source in snapshot['sources'].items():
        coverage = source.get('coverage')
        if not coverage:
            coverage = [[f'{key}-01-01', f'{key}-12-31']]
        elif isinstance(coverage[0], str):
            coverage = [coverage]
        effective = [[max(a, c), min(b, d)] for a, b in coverage for c, d in snapshot['coverage'] if max(a, c) <= min(b, d)]
        if effective:
            sources[source['sha256']] = {**source, 'coverage': effective}
    return sources


def overlay(base, patch, start, end):
    """Replace exactly one acquired period, preserving other months and sources."""
    rows = {d: r for d, r in base['rows'].items() if not start <= d <= end}
    rows.update(patch['rows'])
    coverage = intervals(subtract(base['coverage'], start, end) + patch['coverage'])
    sources = source_periods(base)
    for source in sources.values():
        source['coverage'] = subtract(source['coverage'], start, end)
    for key, source in source_periods(patch).items():
        if key in sources:
            source['coverage'] = intervals(sources[key]['coverage'] + source['coverage'])
        sources[key] = source
    sources = {k: v for k, v in sources.items() if v['coverage']}
    return {'id': snapshot_id(rows, coverage), 'series': SERIES, 'rate_type': 'nominal_par',
            'normalizer_version': NORMALIZER_VERSION, 'rows': dict(sorted(rows.items())),
            'coverage': coverage, 'sources': sources, 'created_at': utc_now(), 'bundled': False}


def slice_month(snapshot, start, end):
    coverage = [[max(a, start), min(b, end)] for a, b in snapshot['coverage'] if max(a, start) <= min(b, end)]
    result = {**snapshot, 'rows': {d: r for d, r in snapshot['rows'].items() if start <= d <= end}, 'coverage': coverage}
    result['sources'] = source_periods(result)
    return result


def covers(snapshot, start, end):
    return any(a <= start and end <= b for a, b in intervals(snapshot['coverage']))


def fresh(snapshot, start, end):
    if not covers(snapshot, start, end):
        return False
    if end[:7] != today().isoformat()[:7]:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    sources = source_periods(slice_month(snapshot, start, end))
    return bool(sources) and all(datetime.fromisoformat(s['retrieved_at'].replace('Z', '+00:00')) >= cutoff for s in sources.values())


class RefreshBusy(DataError):
    pass


class SnapshotStore:
    def __init__(self, root=None):
        self.root = Path(root or os.environ.get('FILAB_DATA_DIR', Path.home() / '.local/share/fixed-income-lab'))
        self.fixture = pinned_snapshot()
        self.reference_fixture = pinned_snapshot("series-introduction")
        self.viewer = bundled_history()
        self.bundled = {sample["id"]: sample for sample in (self.fixture, self.reference_fixture, self.viewer)}

    @property
    def database(self):
        return self.root / 'catalog.sqlite3'

    def _connect(self):
        return sqlite3.connect(self.database, timeout=30)

    def get(self, identifier):
        if identifier in self.bundled:
            return deepcopy(self.bundled[identifier])
        if not re.fullmatch(r'[a-f0-9]{64}', identifier or ''):
            raise DataError('Unknown snapshot.')
        if self.database.exists():
            with self._connect() as db:
                row = db.execute('SELECT payload FROM snapshots WHERE id=?', (identifier,)).fetchone()
            if row:
                return json.loads(row[0])
        raise DataError('Unknown snapshot.')

    def catalog(self):
        snapshots = list(self.bundled.values())
        active = self.viewer['id']
        acquisitions = []
        if self.database.exists():
            with self._connect() as db:
                # Keep the list and pointer on one read transaction during refresh.
                db.execute('BEGIN')
                snapshots += [json.loads(row[0]) for row in db.execute('SELECT payload FROM snapshots ORDER BY created_at DESC') if json.loads(row[0])['id'] not in self.bundled]
                row = db.execute('SELECT id FROM active WHERE singleton=1').fetchone()
                if row:
                    active = row[0]
                acquisitions = [json.loads(row[0]) for row in db.execute('SELECT payload FROM acquisitions ORDER BY sequence DESC LIMIT 50')]
        return {'active_snapshot_id': active, 'bundled_snapshot_id': self.fixture['id'],
                'reference_snapshot_id': self.reference_fixture['id'], 'viewer_snapshot_id': active,
                'current_month': today().month,
                'example_defaults': self.fixture['example'],
                'reference_defaults': self.reference_fixture['example'],
                'current_year': today().year, 'default_year': today().year - 1,
                'snapshots': [{'id': s['id'], 'created_at': s['created_at'], 'coverage': s['coverage'],
                               'latest_observation': max(s['rows'], default=None), 'row_count': len(s['rows']),
                               'bundled': s.get('bundled', False), 'label': s.get('label', 'Saved dataset')} for s in snapshots],
                'acquisitions': acquisitions}

    def _prepare(self):
        (self.root / 'raw').mkdir(exist_ok=True)
        if self.database.exists():
            with self._connect() as db:
                db.execute('CREATE TABLE IF NOT EXISTS month_checks (period TEXT PRIMARY KEY, payload TEXT NOT NULL)')
            return
        # Readers see either no catalog or a fully initialized catalog.
        descriptor, temporary = tempfile.mkstemp(dir=self.root)
        os.close(descriptor)
        try:
            with sqlite3.connect(temporary) as db:
                db.executescript("""
                    CREATE TABLE snapshots (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL);
                    CREATE TABLE active (singleton INTEGER PRIMARY KEY CHECK(singleton=1), id TEXT NOT NULL);
                    CREATE TABLE acquisitions (sequence INTEGER PRIMARY KEY, payload TEXT NOT NULL);
                    CREATE TABLE month_checks (period TEXT PRIMARY KEY, payload TEXT NOT NULL);
                """)
            db.close()
            os.replace(temporary, self.database)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _raw(self, raw, metadata):
        if metadata['sha256'] != digest(raw):
            raise DataError('Acquisition hash mismatch.')
        path = self.root / 'raw' / (metadata['sha256'] + '.xml')
        if not path.exists():
            descriptor, temporary = tempfile.mkstemp(dir=path.parent)
            try:
                with os.fdopen(descriptor, 'wb') as output:
                    output.write(raw)
                    output.flush()
                    os.fsync(output.fileno())
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        with self._connect() as db:
            db.execute('INSERT INTO acquisitions(payload) VALUES (?)', (encode(metadata),))

    def refresh(self, start_year, end_year, fetcher=fetch_year, progress=lambda text: None):
        """Replace complete selected years; retain all other cached coverage.

        Unchanged numerical observations reuse their snapshot. Acquisitions are
        still logged, so a new retrieval is not confused with a new revision.
        Errors and process interruption leave the prior active pointer intact.
        """
        if not (isinstance(start_year, int) and isinstance(end_year, int) and 1990 <= start_year <= end_year <= today().year):
            raise DataError('Choose an ordered year range from 1990 through the current year.')
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / 'refresh.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RefreshBusy('Another refresh is already running.') from exc
            self._prepare()
            previous = self.get(self.catalog()['active_snapshot_id'])
            snapshot = previous
            for year in range(start_year, end_year + 1):
                progress(f'Fetching and validating {year} ({year - start_year + 1}/{end_year - start_year + 1})')
                raw, metadata = fetcher(year)
                self._raw(raw, metadata)
                start, end = date(year, 1, 1), min(date(year, 12, 31), today())
                patch = {'rows': normalize(raw, start, end), 'coverage': [[start.isoformat(), end.isoformat()]],
                         'sources': {str(year): {**metadata, 'coverage': [start.isoformat(), end.isoformat()]}}}
                snapshot = overlay(snapshot, patch, start.isoformat(), end.isoformat())
            identifier = snapshot['id']
            self._commit([snapshot], identifier)
            progress('Complete; your open comparison keeps its selected snapshot.')
            return identifier

    def _commit(self, snapshots, active, month_check=None):
        with self._connect() as db:
            for snapshot in snapshots:
                db.execute('INSERT OR IGNORE INTO snapshots VALUES (?, ?, ?)',
                           (snapshot['id'], encode(snapshot), snapshot['created_at']))
            db.execute('INSERT OR REPLACE INTO active VALUES (1, ?)', (active,))
            if month_check:
                period, patch = month_check
                db.execute('INSERT OR REPLACE INTO month_checks VALUES (?, ?)', (period, encode(patch)))

    def ensure_month(self, year, month, base_snapshot_id, *, force=False, fetcher=None):
        """Load a month onto an explicit base; old snapshots remain immutable.

        Complete historical months are reused. Current-month acquisitions are
        checked at most hourly. A failed check returns available cached coverage
        with a warning, without inventing coverage for later dates. Writers are
        serialized and recheck the cache after locking to deduplicate requests.
        """
        start_date, end_date = month_bounds(year, month)
        start, end = start_date.isoformat(), end_date.isoformat()
        base = self.get(base_snapshot_id)
        if not force and fresh(base, start, end):
            return {'snapshot_id': base['id'], 'cache_hit': True, 'warning': None}
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / 'refresh.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self._prepare()
            active = self.get(self.catalog()['active_snapshot_id'])
            candidates = [slice_month(s, start, end) for s in (base, active, self.viewer)]
            with self._connect() as db:
                checked = db.execute('SELECT payload FROM month_checks WHERE period=?', (start[:7],)).fetchone()
            if checked:
                candidates.insert(0, slice_month(json.loads(checked[0]), start, end))
            # A newer annual refresh takes precedence over an older month check.
            def acquired_at(candidate):
                return min((s['retrieved_at'] for s in candidate['sources'].values()), default='')
            usable = [s for s in candidates if fresh(s, start, end)]
            cached = max(usable, key=acquired_at, default=None)
            warning = None
            cache_hit = cached is not None and not force
            if not cache_hit:
                try:
                    raw, metadata = (fetcher or fetch_month)(year, month)
                    self._raw(raw, metadata)
                    cached = {'rows': normalize(raw, start_date, end_date, allow_empty=True),
                              'coverage': [[start, end]],
                              'sources': {metadata['sha256']: {**metadata, 'coverage': [[start, end]]}}}
                except (DataError, OSError) as exc:
                    # Prefer the most complete local coverage after a failed check.
                    cached = max(candidates, key=lambda s: (max((b for a, b in s['coverage']), default=''), acquired_at(s)))
                    if not cached['coverage']:
                        raise
                    warning = f'{exc} Showing cached coverage; no new data was activated.'
                    cache_hit = True
            if warning:
                # Do not publish an incomplete or failed refresh over an existing view.
                if covers(base, start, max(b for a, b in cached['coverage'])):
                    return {'snapshot_id': base['id'], 'cache_hit': True, 'warning': warning}
            acquired_end = max(b for a, b in cached['coverage'])
            view = overlay(base, cached, start, acquired_end)
            working = overlay(active, cached, start, acquired_end)
            self._commit([view, working], working['id'], (start[:7], cached) if not warning else None)
            return {'snapshot_id': view['id'], 'cache_hit': cache_hit, 'warning': warning}

    def seed_bundled_history(self):
        """Persist the shipped month responses without needing a network request."""
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / 'refresh.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self._prepare()
            active = self.get(self.catalog()['active_snapshot_id'])
            folder = Path(__file__).resolve().parent / 'fixtures'
            for month in ('202610', '202611'):
                metadata = json.loads((folder / f'treasury-cache-{month}.json').read_text())
                raw = (folder / f'treasury-cache-{month}.xml').read_bytes()
                self._raw(raw, metadata)
                start, end = metadata['coverage']
                # Existing more recent observations must survive starter seeding.
                if not covers(active, start, end):
                    active = overlay(active, slice_month(self.viewer, start, end), start, end)
            self._commit([active], active['id'])
            return active['id']
