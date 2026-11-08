"""Federal Reserve fitted nominal curves and bounded, stateless CSV normalization.

Source yields and betas are percent per annum; taus are years. Normalized rates
and betas are decimals. Historical valuation is restricted to published horizons
(1 year to that row's last contiguous published node). Subyear calculations are
available only through explicitly hypothetical validation diagnostics.
"""
import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import date
from importlib.resources import files
from math import exp, expm1, fsum, isfinite

from filab.curves import dated_payments
from filab.pricing._validation import finite_real as number
from filab.pricing import coupon_schedule

SOURCE_URL = 'https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv'
MAX_BYTES = 24_000_000
MAX_ROWS = 26_000
TOLERANCE = 0.00000051  # 0.000051 percentage points, half the 4-decimal source increment + margin
PARAMETERS = ['BETA0', 'BETA1', 'BETA2', 'BETA3', 'TAU1', 'TAU2']
SERIES = [f'{prefix}{i:02d}' for prefix in ('SVENY', 'SVENF', 'SVENPY') for i in range(1, 31)]
COLUMNS = ['Date'] + PARAMETERS + SERIES + ['SVEN1F01', 'SVEN1F04', 'SVEN1F09']


def maximum_maturity(day):
    """Published historical range from GSW section 4."""
    for boundary, limit in [('1985-11-25', 30), ('1981-07-02', 20), ('1971-11-15', 15), ('1971-08-16', 10)]:
        if day >= boundary:
            return limit
    return 7


@dataclass(frozen=True)
class FedCurve:
    parameters: tuple
    maximum: float

    def __post_init__(self):
        if len(self.parameters) != 6 or not all(v is None or (type(v) in (float, int) and isfinite(v)) for v in self.parameters):
            raise ValueError('Invalid fitted curve parameters.')
        b0, b1, b2, b3, tau1, tau2 = self.parameters
        if any(v is None for v in (b0, b1, b2, b3, tau1)) or tau1 <= 0 or (b3 != 0 and (tau2 is None or tau2 <= 0)):
            raise ValueError('Missing or invalid fitted curve parameters.')

    def zero(self, time):
        time = number('time_years', time)
        if time < 0:
            raise ValueError('Curve time must be nonnegative.')
        b0, b1, b2, b3, tau1, tau2 = self.parameters
        x = time / tau1
        loading = -expm1(-x) / x if x else 1
        result = b0 + b1 * loading + b2 * (loading - exp(-x))
        if b3:
            z = time / tau2
            result += b3 * (-expm1(-z) / z - exp(-z)) if z else 0
        if not isfinite(result):
            raise ValueError('Curve inputs exceed numerical precision.')
        return result

    def instantaneous_forward(self, time):
        time = number('time_years', time)
        if time < 0:
            raise ValueError('Curve time must be nonnegative.')
        b0, b1, b2, b3, tau1, tau2 = self.parameters
        x = time / tau1
        result = b0 + b1 * exp(-x) + b2 * x * exp(-x) + (b3 * time / tau2 * exp(-time / tau2) if b3 else 0)
        if not isfinite(result):
            raise ValueError('Curve inputs exceed numerical precision.')
        return result

    def model_discount(self, time):
        """Unrestricted fitted formula for source reproduction and diagnostics only."""
        factor = exp(-time * self.zero(time))
        if not isfinite(factor) or factor <= 0:
            raise ValueError('Curve inputs exceed numerical discount precision.')
        return factor

    def discount(self, time):
        if type(time) not in (float, int) or not isfinite(time) or not 1 <= time <= self.maximum:
            raise ValueError(f'Historical payment requires 1–{self.maximum:g} years of remaining maturity.')
        return self.model_discount(time)

    def par(self, maturity):
        return 2 * (1 - self.model_discount(maturity)) / fsum(self.model_discount(k / 2) for k in range(1, 2 * maturity + 1))


def validate_row(row):
    """Revalidate browser-supplied rows before reconstructing any result."""
    if not isinstance(row, dict) or set(row) != {'date', 'values'}:
        raise ValueError('Invalid Fed row.')
    day = date.fromisoformat(row['date']).isoformat()
    values = row['values']
    if day != row['date'] or not '1961-06-14' <= day or not isinstance(values, list) or len(values) != 99:
        raise ValueError('Invalid Fed row date or column count.')
    if any(v is not None and (type(v) not in (int, float) or not isfinite(v)) for v in values):
        raise ValueError('Fed values must be finite numbers or missing.')
    if all(v is None for v in values):
        return None
    curve = FedCurve(tuple(values[:6]), maximum_maturity(day))
    zeros, forwards, pars = values[6:36], values[36:66], values[66:96]
    available = 0
    for i in range(int(curve.maximum)):
        if any(series[i] is None for series in (zeros, forwards, pars)):
            break
        available = i + 1
    if available == 0:
        return None
    curve = FedCurve(curve.parameters, available)
    return curve


def reproduction_errors(row, curve):
    zeros, forwards, pars = row['values'][6:36], row['values'][36:66], row['values'][66:96]
    errors = []
    for i in range(int(curve.maximum)):
        for name, observed, calculated in (('zero', zeros[i], curve.zero(i + 1)), ('forward', forwards[i], curve.instantaneous_forward(i + 1)), ('par', pars[i], curve.par(i + 1))):
            errors.append(dict(series=name, maturity=i+1, error=abs(observed-calculated)))
    return errors


def normalize(raw):
    """Parse official CSV bytes, preserving missing values and all published columns.

    Identity is the raw SHA-256. Import timestamps are browser-local metadata.
    No acquisition time is inferred from the observation dates or a local file.
    """
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError('Choose a nonempty Fed CSV of at most 24 MB.')
    try:
        lines = raw.decode('utf-8-sig').splitlines()
        header = next(i for i, line in enumerate(lines[:100]) if line.startswith('Date,'))
        reader = csv.DictReader(lines[header:])
        if len(reader.fieldnames) != 100 or set(reader.fieldnames) != set(COLUMNS):
            raise ValueError('The Fed CSV columns do not match this adapter version.')
        rows = []
        previous = ''
        for source in reader:
            if len(rows) >= MAX_ROWS or None in source or any(v is None for v in source.values()):
                raise ValueError('The Fed CSV exceeds the row limit or contains an incomplete row.')
            day = date.fromisoformat(source['Date']).isoformat()
            if day <= previous:
                raise ValueError('Fed dates must be unique and increasing.')
            values = []
            for key in COLUMNS[1:]:
                value = source[key].strip()
                numeric = None if value in ('NA', '', '-999.99') else float(value)
                if numeric is not None and key not in ('TAU1', 'TAU2'):
                    numeric /= 100
                values.append(numeric)
            row = dict(date=day, values=values)
            validate_row(row)
            rows.append(row)
            previous = day
        if not rows:
            raise ValueError('The Fed CSV has no dated rows.')
    except (UnicodeError, StopIteration, csv.Error, TypeError, OverflowError) as exc:
        raise ValueError('Unable to read the official Fed CSV format.') from exc
    return dict(version=1, id=hashlib.sha256(raw).hexdigest(), source_url=SOURCE_URL,
                raw_bytes=len(raw), coverage=[[rows[0]['date'], rows[-1]['date']]], columns=COLUMNS[1:], rows=rows)


def bundled():
    raw = files('filab.data').joinpath('fixtures/fed-sample.csv').read_bytes()
    result = normalize(raw)
    result['source'] = json.loads(files('filab.data').joinpath('fixtures/fed-sample.json').read_text())
    # The excerpt contains isolated exact dates. It establishes no intervening coverage.
    result['coverage'] = [[row['date'], row['date']] for row in result['rows']]
    return result


def historical_valuation(row, *, maturity_years=2, coupon_rate=.04, age_months=0):
    """Regular synthetic note on a historical date; ACT/365F curve time, no stubs."""
    curve = validate_row(row)
    if curve is None:
        return dict(status='No data', cashflows=[], dirty_price=None, clean_price=None)
    settlement = date.fromisoformat(row['date'])
    from calendar import monthrange
    def shift(months):
        year, month = divmod(settlement.year * 12 + settlement.month - 1 + months, 12)
        month += 1
        day = monthrange(year, month)[1] if settlement.day == monthrange(settlement.year, settlement.month)[1] else min(settlement.day, monthrange(year, month)[1])
        return date(year, month, day)
    # Anchor to the contractual maturity, preserving the existing maturity EOM convention.
    maturity = shift(maturity_years * 12 - age_months)
    issue = shift(-age_months)
    if maturity.day == monthrange(maturity.year, maturity.month)[1]:
        issue = date(issue.year, issue.month, monthrange(issue.year, issue.month)[1])
    if coupon_rate == 0:
        flows = [dict(payment_date=maturity.isoformat(), time_years=(maturity-settlement).days/365, amount=100)]
        accrued = 0
    elif issue > settlement:
        return dict(status='Regular coupon grid cannot start on this issue date. Stub coupons are excluded.',
                    cashflows=[], dirty_price=None, clean_price=None, accrued_interest=None)
    else:
        flows, accrued = dated_payments(face_value=100, coupon_rate=coupon_rate, issue_date=issue,
            maturity_date=maturity, settlement_date=settlement, frequency=2)
    reproduction_error = max(e['error'] for e in reproduction_errors(row, curve))
    supported = reproduction_error <= TOLERANCE
    for flow in flows:
        valid = flow['amount'] == 0 or 1 <= flow['time_years'] <= curve.maximum
        flow['supported'] = valid
        flow['discount_factor'] = curve.discount(flow['time_years']) if valid and flow['amount'] else None
        flow['present_value'] = flow['amount'] * flow['discount_factor'] if flow['discount_factor'] is not None else (0 if flow['amount'] == 0 else None)
        supported = supported and valid
    dirty = fsum(f['present_value'] for f in flows) if supported else None
    return dict(status=('Supported' if supported else 'Parameter reconstruction exceeds source rounding' if reproduction_error > TOLERANCE else 'Unsupported payment maturity'),
                supported_range=[1, curve.maximum], reproduction_error=reproduction_error, cashflows=flows, accrued_interest=accrued,
                dirty_price=dirty, clean_price=dirty-accrued if supported else None,
                time_basis='Actual/365 Fixed (Lab curve convention)', settlement_date=settlement.isoformat())
