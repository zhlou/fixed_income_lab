"""Stateless validation and portable archives for browser-owned Treasury history."""
import argparse
import base64
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
import re
import sqlite3

from .store import SnapshotStore, intervals, overlay, source_periods
from .treasury import (DataError, NORMALIZER_VERSION, SERIES, TENORS, digest,
                       month_bounds, normalize, snapshot_id, source_url, today)

MAX_ROWS = 15_000
MAX_RAW = 4_000_000


def validate_snapshot(value):
    """Validate normalized inputs without trusting browser-supplied arithmetic."""
    try:
        result = deepcopy(value)
        if result['series'] != SERIES or result['rate_type'] != 'nominal_par' or result['normalizer_version'] != NORMALIZER_VERSION:
            raise DataError('Unsupported Treasury dataset.')
        coverage = result['coverage']
        if not coverage or len(coverage) > 500:
            raise DataError('Invalid dataset coverage.')
        for a, b in coverage:
            if not date(1990, 1, 1) <= date.fromisoformat(a) <= date.fromisoformat(b) <= today():
                raise DataError('Invalid dataset coverage.')
        if coverage != intervals(coverage) or len(result['rows']) > MAX_ROWS:
            raise DataError('Invalid dataset coverage or row count.')
        fields = {tenor.field for tenor in TENORS}
        for day, row in result['rows'].items():
            date.fromisoformat(day)
            if not any(a <= day <= b for a, b in coverage) or set(row) != fields:
                raise DataError('Observation outside coverage or unknown tenor.')
            for observation in row.values():
                if observation is not None:
                    number = Decimal(observation['original_percent'])
                    if not number.is_finite() or observation['rate'] != float(number / 100):
                        raise DataError('Rate differs from the original source percentage.')
        if result['id'] != snapshot_id(result['rows'], coverage):
            raise DataError('Dataset identifier does not match its contents.')
        datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
        if not result['sources'] or len(result['sources']) > 500:
            raise DataError('Invalid source metadata.')
        for source in result['sources'].values():
            if not re.fullmatch(r'[a-f0-9]{64}', source['sha256']):
                raise DataError('Invalid source hash.')
            if not re.fullmatch(re.escape(source_url(year=2000)).replace('2000', r'\d{4}') + r'|'
                                + re.escape(source_url(month=200001)).replace('200001', r'\d{6}'), source['url']):
                raise DataError('Unsupported source URL.')
            datetime.fromisoformat(source['retrieved_at'].replace('Z', '+00:00'))
        return result
    except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
        if isinstance(exc, DataError):
            raise
        raise DataError('Malformed Treasury dataset.') from exc


def decode_raw(encoded):
    try:
        if not isinstance(encoded, str) or len(encoded) > (MAX_RAW + 2) // 3 * 4:
            raise DataError('Source response exceeds the supported size.')
        raw = base64.b64decode(encoded, validate=True)
        if len(raw) > MAX_RAW:
            raise DataError('Source response exceeds the supported size.')
        return raw
    except ValueError as exc:
        raise DataError('Invalid source bytes.') from exc


def acquire(base, year, month, encoded, retrieved_at):
    """Normalize browser-acquired bytes and overlay only their acquired period."""
    base = validate_snapshot(base)
    if month is None:
        if not 1990 <= year <= today().year:
            raise DataError('Choose a year from 1990 through the current year.')
        start, end = date(year, 1, 1), min(date(year, 12, 31), today())
    else:
        start, end = month_bounds(year, month)
    timestamp = datetime.fromisoformat(retrieved_at.replace('Z', '+00:00'))
    if timestamp.tzinfo is None:
        raise DataError('Retrieval timestamp needs a time zone.')
    raw = decode_raw(encoded)
    source = {'url': source_url(month=f'{year:04d}{month:02d}') if month else source_url(year=year),
              'retrieved_at': retrieved_at, 'retrieval_context': 'browser_reported',
              'sha256': digest(raw), 'series': SERIES, 'original_units': 'percent per annum',
              'normalized_units': 'decimal per annum', 'publication_time': None,
              'coverage': [[start.isoformat(), end.isoformat()]]}
    patch = {'rows': normalize(raw, start, end, allow_empty=True),
             'coverage': source['coverage'], 'sources': {source['sha256']: source}}
    result = overlay(base, patch, start.isoformat(), end.isoformat())
    return {'snapshot': result, 'sha256': source['sha256']}


def bundled_archive():
    store = SnapshotStore()
    folder = Path(__file__).resolve().parent / 'fixtures'
    raw = {}
    for file in folder.glob('*.xml'):
        data = file.read_bytes()
        raw[digest(data)] = base64.b64encode(data).decode('ascii')
    return {'schema_version': 1, 'snapshots': list(store.bundled.values()), 'raw': raw}


def validate_archive(archive):
    """Check normalized snapshots against their exact exported raw observations."""
    try:
        if archive['schema_version'] != 1 or not 1 <= len(archive['snapshots']) <= 100:
            raise DataError('Unsupported archive version or snapshot count.')
        if len(archive['raw']) > 500:
            raise DataError('Too many source files.')
        raw = {key: decode_raw(value) for key, value in archive['raw'].items()}
        if any(digest(value) != key for key, value in raw.items()):
            raise DataError('Raw source hash does not match.')
        snapshots = [validate_snapshot(value) for value in archive['snapshots']]
        for snapshot in snapshots:
            matched = {}
            acquired_coverage = []
            for source in source_periods(snapshot).values():
                payload = raw[source['sha256']]
                # A source can cover a year but contribute only a few of its months.
                # Normalize its original requested period before slicing its contribution.
                period = source['url'].split('=')[-1]
                year = int(period[:4])
                start = date(year, int(period[4:]) if len(period) == 6 else 1, 1)
                end = date(year, 12, 31) if len(period) == 4 else month_bounds(year, int(period[4:]))[1]
                rows = normalize(payload, start, end, allow_empty=True)
                for a, b in source['coverage']:
                    acquired_coverage.append([a, b])
                    for day, row in rows.items():
                        if a <= day <= b:
                            if day in matched and matched[day] != row:
                                raise DataError('Conflicting source observations.')
                            matched[day] = row
            if matched != snapshot['rows'] or intervals(acquired_coverage) != snapshot['coverage']:
                raise DataError('Dataset does not match its source responses and coverage.')
        return {'schema_version': 1, 'snapshots': snapshots, 'raw': archive['raw']}
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, DataError):
            raise
        raise DataError('Malformed Treasury archive.') from exc


def export_legacy(root):
    """Read an existing cache without initializing it, changing it, or fetching data."""
    root = Path(root).resolve()
    archive = bundled_archive()
    database = root / 'catalog.sqlite3'
    if database.exists():
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as connection:
            archive['snapshots'] += [json.loads(row[0]) for row in connection.execute('SELECT payload FROM snapshots')]
    archive['snapshots'] = list({s['id']: s for s in archive['snapshots']}.values())
    for source in (source for s in archive['snapshots'] for source in s['sources'].values()):
        key = source['sha256']
        if key not in archive['raw']:
            archive['raw'][key] = base64.b64encode((root / 'raw' / (key + '.xml')).read_bytes()).decode('ascii')
    return validate_archive(archive)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export an existing Treasury cache read-only for browser import.')
    parser.add_argument('cache_directory')
    parser.add_argument('output')
    args = parser.parse_args()
    with open(args.output, 'x') as output:
        json.dump(export_legacy(args.cache_directory), output)
