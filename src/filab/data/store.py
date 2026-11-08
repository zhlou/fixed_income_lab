"""Immutable snapshots, exact raw bytes, and an atomic active pointer.

The bundled month is always readable without initializing a writable cache.
One file lock serializes refreshes across processes. SQLite commits the new
snapshot and active pointer together only after every selected year validates.
"""
from copy import deepcopy
from datetime import date
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

from .treasury import (DataError, SERIES, NORMALIZER_VERSION, digest,
                       encode, fetch_year, pinned_snapshot, snapshot_id, today, utc_now)
from .treasury import normalize


class RefreshBusy(DataError):
    pass


class SnapshotStore:
    def __init__(self, root=None):
        self.root = Path(root or os.environ.get('FILAB_DATA_DIR', Path.home() / '.local/share/fixed-income-lab'))
        self.fixture = pinned_snapshot()

    @property
    def database(self):
        return self.root / 'catalog.sqlite3'

    def _connect(self):
        return sqlite3.connect(self.database, timeout=30)

    def get(self, identifier):
        if identifier == self.fixture['id']:
            return deepcopy(self.fixture)
        if not re.fullmatch(r'[a-f0-9]{64}', identifier or ''):
            raise DataError('Unknown snapshot.')
        if self.database.exists():
            with self._connect() as db:
                row = db.execute('SELECT payload FROM snapshots WHERE id=?', (identifier,)).fetchone()
            if row:
                return json.loads(row[0])
        raise DataError('Unknown snapshot.')

    def catalog(self):
        snapshots = [self.fixture]
        active = self.fixture['id']
        acquisitions = []
        if self.database.exists():
            with self._connect() as db:
                # Keep the list and pointer on one read transaction during refresh.
                db.execute('BEGIN')
                snapshots += [json.loads(row[0]) for row in db.execute('SELECT payload FROM snapshots ORDER BY created_at DESC') if json.loads(row[0])['id'] != self.fixture['id']]
                row = db.execute('SELECT id FROM active WHERE singleton=1').fetchone()
                if row:
                    active = row[0]
                acquisitions = [json.loads(row[0]) for row in db.execute('SELECT payload FROM acquisitions ORDER BY sequence DESC LIMIT 50')]
        return {'active_snapshot_id': active, 'bundled_snapshot_id': self.fixture['id'],
                'current_year': today().year, 'default_year': today().year - 1,
                'snapshots': [{'id': s['id'], 'created_at': s['created_at'], 'coverage': s['coverage'],
                               'latest_observation': max(s['rows']), 'row_count': len(s['rows']),
                               'bundled': s.get('bundled', False)} for s in snapshots],
                'acquisitions': acquisitions}

    def _prepare(self):
        (self.root / 'raw').mkdir(exist_ok=True)
        if self.database.exists():
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
            rows = {day: values for day, values in previous['rows'].items() if not start_year <= int(day[:4]) <= end_year}
            coverage = [interval for interval in previous['coverage'] if not start_year <= int(interval[0][:4]) <= end_year]
            sources = {year: meta for year, meta in previous['sources'].items() if not start_year <= int(year) <= end_year}
            for year in range(start_year, end_year + 1):
                progress(f'Fetching and validating {year} ({year - start_year + 1}/{end_year - start_year + 1})')
                raw, metadata = fetcher(year)
                self._raw(raw, metadata)
                end = min(date(year, 12, 31), today())
                rows.update(normalize(raw, date(year, 1, 1), end))
                coverage.append([f'{year}-01-01', end.isoformat()])
                sources[str(year)] = metadata
            coverage.sort()
            rows = dict(sorted(rows.items()))
            identifier = snapshot_id(rows, coverage)
            snapshot = {'id': identifier, 'series': SERIES, 'rate_type': 'nominal_par',
                        'normalizer_version': NORMALIZER_VERSION, 'rows': rows,
                        'coverage': coverage, 'sources': sources, 'created_at': utc_now(), 'bundled': False}
            # The full candidate exists before this single transaction becomes visible.
            with self._connect() as db:
                db.execute('INSERT OR IGNORE INTO snapshots VALUES (?, ?, ?)', (identifier, encode(snapshot), snapshot['created_at']))
                db.execute('INSERT OR REPLACE INTO active VALUES (1, ?)', (identifier,))
            progress('Complete; your open comparison keeps its selected snapshot.')
            return identifier
