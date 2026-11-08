"""Snapshot-pinned read APIs and explicitly requested, single-server refresh jobs."""
from datetime import date
from copy import deepcopy
from threading import Lock, Thread
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from filab.data.store import SnapshotStore
from filab.data.treasury import DataError, compare, month_bounds, revision_scenario, today

router = APIRouter(prefix='/api/history', tags=['historical observations'])
_jobs = {}
_jobs_lock = Lock()


def store():
    return SnapshotStore()


class RefreshInputs(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    start_year: int = Field(ge=1990)
    end_year: int = Field(ge=1990)

    @model_validator(mode='after')
    def ordered(self):
        if not self.start_year <= self.end_year <= today().year:
            raise ValueError('Choose an ordered year range through the current year.')
        return self


class MonthInputs(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    year: int = Field(ge=1990)
    month: int = Field(ge=1, le=12)
    base_snapshot_id: str = Field(pattern=r'^[a-f0-9]{64}$')
    force: bool = False

    @model_validator(mode='after')
    def available_month(self):
        month_bounds(self.year, self.month)
        return self


@router.get('/snapshots')
def snapshots():
    return store().catalog()


@router.get('/compare')
def comparison(snapshot_id: str, first: date, second: date, hypothetical_revision: bool = False):
    try:
        snapshot = store().get(snapshot_id)
        scenario = revision_scenario(snapshot, second.isoformat())
        scenario['applied'] = hypothetical_revision and scenario['revised'] is not None
        if scenario['applied']:
            snapshot = deepcopy(snapshot)
            snapshot['rows'][second.isoformat()]['BC_10YEAR'] = scenario['revised']
        result = compare(snapshot, first.isoformat(), second.isoformat())
        result['revision_scenario'] = scenario
        result['data_kind'] = 'hypothetical' if hypothetical_revision else 'historical_observations'
        return result
    except DataError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get('/snapshots/{snapshot_id}')
def snapshot_download(snapshot_id: str):
    try:
        return store().get(snapshot_id)
    except DataError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get('/snapshots/{snapshot_id}/dates')
def snapshot_dates(snapshot_id: str):
    """Published rows and requested coverage, independent of selected dates/tenors."""
    try:
        snapshot = store().get(snapshot_id)
        return {'snapshot_id': snapshot['id'], 'coverage': snapshot['coverage'],
                'published_dates': sorted(snapshot['rows'])}
    except DataError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post('/refresh', status_code=202)
def refresh(inputs: RefreshInputs):
    with _jobs_lock:
        if any(job['state'] == 'running' for job in _jobs.values()):
            raise HTTPException(409, 'Another refresh is already running.')
        identifier = uuid4().hex
        # Bounded history; jobs are transient and snapshots survive server restarts.
        if len(_jobs) >= 30:
            del _jobs[next(iter(_jobs))]
        _jobs[identifier] = {'id': identifier, 'state': 'running', 'message': 'Starting refresh', 'snapshot_id': None}

    def update(message):
        with _jobs_lock:
            _jobs[identifier]['message'] = message

    def work():
        try:
            result = store().refresh(inputs.start_year, inputs.end_year, progress=update)
            with _jobs_lock:
                _jobs[identifier].update(state='complete', snapshot_id=result)
        except Exception as exc:
            message = str(exc) if isinstance(exc, (DataError, OSError)) else 'Refresh failed; the previous snapshot is retained.'
            with _jobs_lock:
                _jobs[identifier].update(state='failed', message=message)

    Thread(target=work, daemon=True).start()
    return {'job_id': identifier}


@router.post('/month-load', status_code=202)
def load_month(inputs: MonthInputs):
    try:
        store().get(inputs.base_snapshot_id)
    except DataError as exc:
        raise HTTPException(404, str(exc)) from exc
    key = (inputs.year, inputs.month, inputs.base_snapshot_id, inputs.force)
    with _jobs_lock:
        for identifier, job in _jobs.items():
            if job['state'] == 'running' and job.get('key') == key:
                return {'job_id': identifier}
        if sum(job['state'] == 'running' for job in _jobs.values()) >= 4:
            raise HTTPException(409, 'Other months are loading. Please retry shortly.')
        # Never evict a running job; readers may still be polling it.
        for identifier in list(_jobs):
            if len(_jobs) < 30:
                break
            if _jobs[identifier]['state'] != 'running':
                del _jobs[identifier]
        identifier = uuid4().hex
        _jobs[identifier] = {'id': identifier, 'key': key, 'state': 'running',
                             'message': f'Loading {inputs.year}-{inputs.month:02d}…', 'snapshot_id': None}

    def work():
        try:
            result = store().ensure_month(inputs.year, inputs.month, inputs.base_snapshot_id, force=inputs.force)
            with _jobs_lock:
                _jobs[identifier].update(result, state='complete', message=result.get('warning') or 'Month ready.')
        except Exception as exc:
            message = str(exc) if isinstance(exc, (DataError, OSError)) else 'Month could not be loaded; cached observations are retained.'
            with _jobs_lock:
                _jobs[identifier].update(state='failed', message=message)

    Thread(target=work, daemon=True).start()
    return {'job_id': identifier}


@router.get('/refresh/{job_id}')
@router.get('/jobs/{job_id}')
def refresh_status(job_id: str):
    with _jobs_lock:
        if job_id not in _jobs:
            raise HTTPException(404, 'Refresh status is no longer available. Reopen cached snapshots; incomplete refreshes never activate.')
        return {key: value for key, value in _jobs[job_id].items() if key != 'key'}
