"""Stateless discount-curve calculations and local-file normalization."""
from datetime import date
from math import exp
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from filab.curves import synthetic_example
from filab.data.fed import (MAX_BYTES, SOURCE_URL, TOLERANCE, bundled, normalize,
                            historical_valuation, validate_row, reproduction_errors)

router = APIRouter(prefix='/api/curves')


class CurveInputs(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    calibration_price: float = Field(default=101.40, gt=8.70, le=300)
    horizon: Literal[0, .5, 1, 1.5, 2] = .5


class HistoryInputs(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    first: Optional[dict] = None
    second: Optional[dict] = None
    first_date: date = date(2026, 10, 29)
    second_date: date = date(2026, 10, 30)
    valuation: Literal['first', 'second'] = 'second'
    maturity_years: Literal[2, 10] = 2
    coupon_rate: float = Field(default=.04, ge=0, le=.20)
    age_months: Literal[0, 1] = 0
    snapshot_id: str = Field(default='bundled', max_length=128)


def invalid(exc):
    raise HTTPException(status_code=422, detail=str(exc))


@router.get('/bundled')
def sample():
    return bundled()


@router.post('/synthetic')
def synthetic(inputs: CurveInputs):
    try:
        return synthetic_example(inputs.calibration_price, inputs.horizon)
    except (ValueError, OverflowError) as exc:
        invalid(exc)


@router.post('/normalize')
async def import_csv(request: Request):
    # The bound applies while reading, even for chunked bodies without Content-Length.
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_BYTES:
            raise HTTPException(status_code=413, detail='Fed CSV exceeds 24 MB.')
        raw.extend(chunk)
    try:
        return await run_in_threadpool(normalize, bytes(raw))
    except (ValueError, OverflowError) as exc:
        invalid(exc)


def curve_view(row, day):
    if row is None:
        return dict(date=day, status='No data', nodes=[])
    if row.get('date') != day:
        raise ValueError('The selected row does not match the observation date.')
    curve = validate_row(row)
    if curve is None:
        return dict(date=day, status='No data', nodes=[])
    values = row['values']
    errors = reproduction_errors(row, curve)
    discrepancy = max(e['error'] for e in errors)
    return dict(date=day, status='Published fitted observations', supported_range=[1, curve.maximum],
                reconstruction_matches=discrepancy <= TOLERANCE, maximum_error=discrepancy,
                nodes=[dict(maturity=i, zero_rate=values[5+i], forward_rate=values[35+i],
                            par_rate=values[65+i], discount_factor=exp(-values[5+i]*i),
                            reconstructed_zero=curve.zero(i)) for i in range(1, int(curve.maximum)+1)])


@router.post('/compare')
def compare(inputs: HistoryInputs):
    try:
        first = curve_view(inputs.first, inputs.first_date.isoformat())
        second = curve_view(inputs.second, inputs.second_date.isoformat())
        row = inputs.first if inputs.valuation == 'first' else inputs.second
        value = historical_valuation(row, maturity_years=inputs.maturity_years,
            coupon_rate=inputs.coupon_rate, age_months=inputs.age_months) if row else dict(status='No data', cashflows=[], dirty_price=None, clean_price=None)
        first_nodes = {n['maturity']: n for n in first['nodes']}
        second_nodes = {n['maturity']: n for n in second['nodes']}
        changes = [dict(maturity=t, first=first_nodes.get(t, {}).get('zero_rate'),
                        second=second_nodes.get(t, {}).get('zero_rate'),
                        change_bp=(second_nodes[t]['zero_rate']-first_nodes[t]['zero_rate'])*10000
                        if t in first_nodes and t in second_nodes else None)
                   for t in sorted(first_nodes.keys() | second_nodes.keys())]
        return dict(first=first, second=second, changes=changes, valuation=value, snapshot_id=inputs.snapshot_id,
                    source_url=SOURCE_URL, classification='Historical fitted curve; model-derived synthetic prices',
                    convention='Source spot and instantaneous forward rates continuously compounded. Par rates nominal semiannual. Curve time Actual/365 Fixed (Lab convention).',
                    short_end='Historical valuation requires every nonzero payment to have at least one year remaining.')
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        invalid(exc)
