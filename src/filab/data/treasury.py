"""Treasury nominal par observations. Rates are decimals, never security prices.

No interpolation, filling, or publication-time inference is performed. The XML
updated field describes the feed, not the historical availability of a row.
"""
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from math import isfinite
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

SERIES = 'daily_treasury_yield_curve'
NORMALIZER_VERSION = 1
FEED = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml'
ATOM = '{http://www.w3.org/2005/Atom}'
META = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}'
DATA = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'


class DataError(ValueError):
    """Source or snapshot cannot support the requested observation."""


@dataclass(frozen=True)
class Tenor:
    field: str
    label: str
    years: float


TENORS = tuple(Tenor('BC_' + field, label, years) for field, label, years in [
    ('1MONTH', '1 month', 1/12), ('1_5MONTH', '1.5 months', 1.5/12),
    ('2MONTH', '2 months', 2/12), ('3MONTH', '3 months', .25),
    ('4MONTH', '4 months', 1/3), ('6MONTH', '6 months', .5),
    ('1YEAR', '1 year', 1), ('2YEAR', '2 years', 2), ('3YEAR', '3 years', 3),
    ('5YEAR', '5 years', 5), ('7YEAR', '7 years', 7), ('10YEAR', '10 years', 10),
    ('20YEAR', '20 years', 20), ('30YEAR', '30 years', 30),
])


def today():
    return datetime.now(ZoneInfo('America/Chicago')).date()


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_url(year=None, month=None):
    key, value = ('field_tdr_date_value_month', month) if month else ('field_tdr_date_value', year)
    return f'{FEED}?data={SERIES}&{key}={value}'


def normalize(raw, start, end):
    """Validate a complete response; absent/null tenors stay None, zero stays zero.

    Identical date duplicates collapse; conflicts and unknown rate fields fail
    visibly so a changed Treasury schema cannot silently remove observations.
    """
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise DataError('XML declarations with entities are unsupported.')
    try:
        root = ET.fromstring(raw)
        if root.tag != ATOM + 'feed' or root.findtext(ATOM + 'title') != 'DailyTreasuryYieldCurveRateData':
            raise DataError('Expected the nominal Treasury par feed.')
        rows = {}
        known = {t.field for t in TENORS} | {'BC_30YEARDISPLAY'}
        if root.find(f"{ATOM}link[@rel='next']") is not None:
            raise DataError('Response is paginated; a complete annual response is required.')
        for entry in root.findall(ATOM + 'entry'):
            properties = entry.find(f'{ATOM}content/{META}properties')
            if properties is None:
                raise DataError('Missing observation properties.')
            day = date.fromisoformat(properties.findtext(DATA + 'NEW_DATE', '')[:10])
            if not start <= day <= end:
                raise DataError('Observation falls outside the requested coverage.')
            unknown = [p.tag for p in properties if p.tag.startswith(DATA + 'BC_') and p.tag[len(DATA):] not in known]
            if unknown:
                raise DataError('Unrecognized tenor in source; update the normalizer.')
            rates = {}
            for tenor in TENORS:
                node = properties.find(DATA + tenor.field)
                value = None
                if node is not None and node.get(META + 'null') != 'true' and (node.text or '').strip():
                    text = node.text.strip()
                    number = Decimal(text)
                    if not number.is_finite():
                        raise DataError('Source rate must be finite.')
                    rate = float(number / 100)
                    if not isfinite(rate):
                        raise DataError('Source rate exceeds supported numerical precision.')
                    value = {'original_percent': text, 'rate': rate}
                rates[tenor.field] = value
            if all(value is None for value in rates.values()):
                raise DataError('Published row contains no usable rates.')
            key = day.isoformat()
            if key in rows and rows[key] != rates:
                raise DataError(f'Conflicting duplicate observation on {key}.')
            rows[key] = rates
        if not rows:
            raise DataError('Source returned no observations; previous data is retained.')
        return dict(sorted(rows.items()))
    except (ET.ParseError, InvalidOperation, ValueError) as exc:
        if isinstance(exc, DataError):
            raise
        raise DataError('Malformed Treasury observations: ' + str(exc)) from exc


def snapshot_id(rows, coverage):
    # Lexical formatting and retrieval time do not manufacture a revision.
    values = {day: {k: v['rate'] if v else None for k, v in rates.items()} for day, rates in rows.items()}
    return digest(encode({'version': NORMALIZER_VERSION, 'rows': values, 'coverage': coverage}).encode())


def fetch_year(year):
    """Fetch only the fixed official annual endpoint, with a timeout and size cap."""
    url = source_url(year=year)
    try:
        with urlopen(Request(url, headers={'User-Agent': 'FixedIncomeLab/0.1'}), timeout=45) as response:
            raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise DataError('Treasury response exceeds the supported size.')
        return raw, {'url': url, 'retrieved_at': utc_now(), 'sha256': digest(raw),
                     'series': SERIES, 'original_units': 'percent per annum',
                     'normalized_units': 'decimal per annum', 'publication_time': None}
    except (OSError, TimeoutError) as exc:
        raise DataError('Treasury could not be reached; cached observations are unchanged.') from exc


def pinned_snapshot():
    folder = Path(__file__).resolve().parent / 'fixtures'
    raw = (folder / 'treasury-202502.xml').read_bytes()
    metadata = json.loads((folder / 'treasury-202502.json').read_text())
    if digest(raw) != metadata['sha256']:
        raise DataError('Bundled sample hash does not match its provenance.')
    coverage = [['2025-02-01', '2025-02-28']]
    rows = normalize(raw, date(2025, 2, 1), date(2025, 2, 28))
    return {'id': snapshot_id(rows, coverage), 'series': SERIES, 'rate_type': 'nominal_par',
            'normalizer_version': NORMALIZER_VERSION, 'coverage': coverage, 'rows': rows,
            'sources': {'2025': metadata}, 'created_at': metadata['retrieved_at'], 'bundled': True}


def compare(snapshot, first, second):
    """Compare exact requested dates, using only tenors present on both dates."""
    days = [date.fromisoformat(first), date.fromisoformat(second)]
    states = []
    for day in days:
        covered = any(date.fromisoformat(a) <= day <= date.fromisoformat(b) for a, b in snapshot['coverage'])
        states.append('outside_coverage' if not covered else 'published' if day.isoformat() in snapshot['rows'] else 'no_published_row')
    rows = [snapshot['rows'].get(day.isoformat(), {}) for day in days]
    table = []
    for tenor in TENORS:
        a, b = (row.get(tenor.field) for row in rows)
        delta = float((Decimal(b['original_percent']) - Decimal(a['original_percent'])) * 100) if a and b else None
        table.append({'field': tenor.field, 'label': tenor.label, 'years': tenor.years,
                      'first': a, 'second': b, 'change_bp': delta,
                      'included': a is not None and b is not None})
    spreads = []
    for row in rows:
        short, long = row.get('BC_2YEAR'), row.get('BC_10YEAR')
        spreads.append(float((Decimal(long['original_percent']) - Decimal(short['original_percent'])) * 100) if short and long else None)
    available = {day for day, row in snapshot['rows'].items() if row.get('BC_2YEAR') and row.get('BC_10YEAR')}
    return {'snapshot_id': snapshot['id'], 'dates': [first, second], 'date_states': states,
            'tenors': table, 'spread_bp': spreads,
            'spread_change_bp': float(Decimal(str(spreads[1])) - Decimal(str(spreads[0]))) if all(v is not None for v in spreads) else None,
            'common_tenors': [t['label'] for t in table if t['included']],
            'excluded_tenors': [t['label'] for t in table if not t['included']],
            'coverage': snapshot['coverage'], 'published_dates': sorted(snapshot['rows']),
            'spread_sample_dates': sorted(available), 'spread_excluded_dates': sorted(set(snapshot['rows']) - available),
            'missing_counts': {t.label: sum(row[t.field] is None for row in snapshot['rows'].values()) for t in TENORS},
            'sources': snapshot['sources'], 'rate_type': snapshot['rate_type'],
            'publication_time': None, 'created_at': snapshot['created_at']}
