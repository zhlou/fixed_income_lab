"""Snapshot-pinned read APIs and explicitly requested, single-server refresh jobs."""
from datetime import date
from copy import deepcopy
from decimal import Decimal
from threading import Lock, Thread
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from filab.data.store import SnapshotStore
from filab.data.treasury import DataError, compare, today

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


@router.get('/snapshots')
def snapshots():
    return store().catalog()


@router.get('/compare')
def comparison(snapshot_id: str, first: date, second: date, hypothetical_revision: bool = False):
    try:
        snapshot = store().get(snapshot_id)
        if hypothetical_revision:
            snapshot = deepcopy(snapshot)
            row = snapshot['rows'].get(second.isoformat())
            if row and row.get('BC_10YEAR'):
                revised = Decimal(row['BC_10YEAR']['original_percent']) + Decimal('0.10')
                row['BC_10YEAR'] = {'original_percent': str(revised), 'rate': float(revised / 100)}
        result = compare(snapshot, first.isoformat(), second.isoformat())
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


@router.get('/refresh/{job_id}')
def refresh_status(job_id: str):
    with _jobs_lock:
        if job_id not in _jobs:
            raise HTTPException(404, 'Refresh status is no longer available. Reopen cached snapshots; incomplete refreshes never activate.')
        return dict(_jobs[job_id])
