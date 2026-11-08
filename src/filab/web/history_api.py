"""Bundled read APIs and stateless Python operations for browser-owned datasets."""
from copy import deepcopy
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from filab.data.browser import acquire, bundled_archive, validate_archive, validate_snapshot
from filab.data.store import SnapshotStore
from filab.data.treasury import DataError, compare, revision_scenario, today

router = APIRouter(prefix='/api/history', tags=['historical observations'])


def bundled(identifier):
    try:
        return SnapshotStore().bundled[identifier]
    except KeyError as exc:
        raise HTTPException(404, 'Unknown bundled snapshot. Import browser datasets with a stateless request.') from exc


@router.get('/snapshots')
def snapshots():
    store = SnapshotStore()
    return {'active_snapshot_id': store.viewer['id'], 'viewer_snapshot_id': store.viewer['id'],
            'bundled_snapshot_id': store.fixture['id'], 'reference_snapshot_id': store.reference_fixture['id'],
            'example_defaults': store.fixture['example'], 'reference_defaults': store.reference_fixture['example'],
            'current_month': today().month, 'current_year': today().year, 'default_year': today().year - 1,
            'snapshots': [{'id': s['id'], 'created_at': s['created_at'], 'coverage': s['coverage'],
                           'latest_observation': max(s['rows'], default=None), 'row_count': len(s['rows']),
                           'bundled': True, 'label': s['label']} for s in store.bundled.values()],
            'acquisitions': []}


@router.get('/bundled-archive')
def archive_download():
    return bundled_archive()


def comparison_result(snapshot, first, second, hypothetical):
    scenario = revision_scenario(snapshot, second.isoformat())
    scenario['applied'] = hypothetical and scenario['revised'] is not None
    if scenario['applied']:
        snapshot = deepcopy(snapshot)
        snapshot['rows'][second.isoformat()]['BC_10YEAR'] = scenario['revised']
    result = compare(snapshot, first.isoformat(), second.isoformat())
    result['revision_scenario'] = scenario
    result['data_kind'] = 'hypothetical' if hypothetical else 'historical_observations'
    return result


@router.get('/compare')
def comparison(snapshot_id: str, first: date, second: date, hypothetical_revision: bool = False):
    return comparison_result(bundled(snapshot_id), first, second, hypothetical_revision)


@router.get('/snapshots/{snapshot_id}')
def snapshot_download(snapshot_id: str):
    return bundled(snapshot_id)


@router.get('/snapshots/{snapshot_id}/dates')
def snapshot_dates(snapshot_id: str):
    snapshot = bundled(snapshot_id)
    return {'snapshot_id': snapshot_id, 'coverage': snapshot['coverage'], 'published_dates': sorted(snapshot['rows'])}


class BrowserInputs(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)
    snapshot: dict


class AcquisitionInputs(BrowserInputs):
    year: int = Field(ge=1990, le=9999)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    raw_base64: str = Field(max_length=5_333_336)
    retrieved_at: str = Field(max_length=40)


class ComparisonInputs(BrowserInputs):
    # Date strings are parsed explicitly because strict JSON Python-mode models reject them.
    first: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    second: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    hypothetical_revision: bool = False


@router.post('/normalize')
def normalize_download(inputs: AcquisitionInputs):
    try:
        return acquire(inputs.snapshot, inputs.year, inputs.month, inputs.raw_base64, inputs.retrieved_at)
    except (DataError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/compare')
def browser_comparison(inputs: ComparisonInputs):
    try:
        return comparison_result(validate_snapshot(inputs.snapshot), date.fromisoformat(inputs.first),
                                 date.fromisoformat(inputs.second), inputs.hypothetical_revision)
    except (DataError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/validate-archive')
def archive_import(archive: dict):
    try:
        return validate_archive(archive)
    except DataError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/refresh', deprecated=True)
@router.post('/month-load', deprecated=True)
@router.get('/refresh/{job_id}', deprecated=True)
@router.get('/jobs/{job_id}', deprecated=True)
def retired_job(job_id: str = ''):
    raise HTTPException(410, 'Treasury downloads now run in the browser. Use /normalize and POST /compare for supplied data.')


class OverlayInputs(BrowserInputs):
    patch: dict
    year: int = Field(ge=1990)
    month: int = Field(ge=1, le=12)


@router.post('/overlay')
def overlay_cached_month(inputs: OverlayInputs):
    from filab.data.store import covers, overlay
    from filab.data.treasury import month_bounds
    try:
        base, patch = validate_snapshot(inputs.snapshot), validate_snapshot(inputs.patch)
        start, end = (d.isoformat() for d in month_bounds(inputs.year, inputs.month))
        if not covers(patch, start, end):
            raise DataError('Cached dataset does not cover this month.')
        # Restrict rows, sources, and coverage to the requested period.
        from filab.data.store import slice_month
        return overlay(base, slice_month(patch, start, end), start, end)
    except (DataError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
