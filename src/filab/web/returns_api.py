"""Return-calculator request validation and adapters to the financial ledger."""
from dataclasses import asdict
from datetime import date, timedelta
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from filab.analytics import BondHolding, YieldPoint, holding_period_ledger
from filab.analytics.returns import CONVENTIONS, ReturnError
from filab.pricing import coupon_schedule, settled_yield_to_maturity

router = APIRouter()


class Inputs(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra='forbid')

    @field_validator('*', mode='before')
    @classmethod
    def no_boolean_numbers(cls, value, info):
        if isinstance(value, bool) and info.field_name != 'include_comparison':
            raise ValueError('Enter a number, not a boolean value.')
        return value


class ReturnInputs(Inputs):
    start_date: date = date(2026, 11, 14)
    end_date: date = date(2026, 11, 16)
    issue_date: date = date(2025, 11, 15)
    maturity_date: date = date(2028, 11, 15)
    face_value: float = Field(default=100, gt=0, le=1e9)
    coupon_rate: float = Field(default=.04, ge=0, le=.20)
    frequency: Literal[1, 2, 4, 12] = 2
    purchase_method: Literal['yield', 'clean'] = 'yield'
    price: float = Field(default=98.12, gt=0, le=1000)
    start_yield: float = Field(default=.05, ge=-.02, le=.30)
    yield_path: Literal['fixed', 'shock'] = 'fixed'
    shock_date: date = date(2026, 11, 16)
    end_yield: float = Field(default=.06, ge=-.02, le=.30)
    cash_policy: Literal['zero', 'interest'] = 'zero'
    cash_rate: float = Field(default=.04, ge=-.02, le=.30)
    cost_bp: float = Field(default=0, ge=0, le=100)
    end_treatment: Literal['mark', 'liquidate'] = 'liquidate'
    include_comparison: bool = False
    comparison_face_value: float = Field(default=100, gt=0, le=1e9)
    comparison_coupon_rate: float = Field(default=.04, ge=0, le=.20)
    comparison_maturity_date: date = date(2036, 11, 15)
    comparison_price: float = Field(default=90, gt=0, le=1000)


class ReturnStudy(Inputs):
    schema_version: Literal[1]
    kind: Literal['filab-bond-return']
    conventions: Literal['dated-return-ledger-v1']
    inputs: ReturnInputs

    @model_validator(mode='before')
    @classmethod
    def complete_snapshot(cls, value):
        if isinstance(value, dict):
            if type(value.get('schema_version')) is not int:
                raise ValueError('A saved scenario needs an explicit integer version.')
            fields = value.get('inputs')
            if not isinstance(fields, dict) or set(fields) != set(ReturnInputs.model_fields):
                raise ValueError('A saved scenario must include every input and its conventions.')
        return value


def fail(field, message):
    raise HTTPException(422, detail=[{'loc': ['body', field], 'msg': message}])


def calculate_return(data: ReturnInputs, *, include_cash_paths=False):
    """Build one or two positions with a fixed yield or one dated step change."""
    try:
        if data.yield_path == 'shock' and not data.start_date < data.shock_date <= data.end_date:
            raise ReturnError('shock_date', 'Yield change must be after purchase and no later than the horizon.')
        holdings, purchase_ytms = [], []
        settings = [('Bond A', '', data.face_value, data.coupon_rate, data.maturity_date, data.price)]
        if data.include_comparison:
            settings.append(('Bond B', 'comparison_', data.comparison_face_value,
                             data.comparison_coupon_rate, data.comparison_maturity_date, data.comparison_price))
        dates = set()
        for label, prefix, face, coupon, maturity, price in settings:
            try:
                if (maturity - data.issue_date).days > 366 * 50:
                    raise ReturnError('maturity_date', 'Use a bond term of at most 50 years.')
                if data.purchase_method == 'clean' and abs(price - round(price, 2)) > 1e-9:
                    raise ReturnError('price', 'Commit the clean purchase quote in one-cent increments.')
                ytm = data.start_yield
                if data.purchase_method == 'clean':
                    ytm = settled_yield_to_maturity(price=price, price_type='clean', face_value=100,
                        coupon_rate=coupon, issue_date=data.issue_date, maturity_date=maturity,
                        settlement_date=data.start_date, frequency=data.frequency)
                points = [YieldPoint(data.start_date, ytm)]
                if data.yield_path == 'shock':
                    points.append(YieldPoint(data.shock_date, data.end_yield))
                holdings.append(BondHolding(label, face, coupon, data.issue_date,
                                           maturity, tuple(points), data.frequency))
                purchase_ytms.append(dict(label=label, ytm=ytm))
                for day in coupon_schedule(issue_date=data.issue_date, maturity_date=maturity, frequency=data.frequency):
                    if data.start_date < day <= data.end_date:
                        dates.add(day - timedelta(days=1))
            except ValueError as exc:
                field = getattr(exc, 'field', 'price' if data.purchase_method == 'clean' else 'start_yield')
                if prefix and field in ('price', 'coupon_rate', 'maturity_date', 'issue_date'):
                    field = prefix + ('maturity_date' if field == 'issue_date' else field)
                if field == 'settlement_date':
                    field = 'start_date'
                raise ReturnError(field, str(exc)) from exc
        days = (data.end_date - data.start_date).days
        if 0 < days <= 366 * 50:
            dates.update(data.start_date + timedelta(days=round(days * k / 40)) for k in range(41))
        args = dict(holdings=holdings, start_date=data.start_date, end_date=data.end_date,
                    cost_bp=data.cost_bp, end_treatment=data.end_treatment, valuation_dates=sorted(dates))
        rate = data.cash_rate if data.cash_policy == 'interest' else 0
        result = holding_period_ledger(cash_rate=rate, **args)
        # Same positions, same fees and capital; change only the cash assumption.
        zero = result if rate == 0 else holding_period_ledger(cash_rate=0, **args)
        alternative = result if rate == data.cash_rate else holding_period_ledger(cash_rate=data.cash_rate, **args)
        cash_comparison = []
        for label, account_rate, account_result in [('Cash at 0%', 0, zero),
                ('Explicit cash rate', data.cash_rate, alternative)]:
            row = dict(label=label, rate=account_rate, ending_wealth=account_result.ending_wealth,
                       total_return=account_result.total_return, cash_interest=account_result.cash_interest)
            if include_cash_paths:
                row['path'] = [asdict(point) for point in account_result.path]
            cash_comparison.append(row)
        return dict(result=asdict(result), purchase_ytms=purchase_ytms,
                    price_provenance=dict(purchase='user-assumed clean quote' if data.purchase_method == 'clean'
                                          else 'hypothetical YTM model', later_prices='hypothetical YTM model'),
                    cash_comparison=cash_comparison,
                    inputs=data.model_dump(mode='json'), conventions=CONVENTIONS)
    except ValueError as exc:
        fail(getattr(exc, 'field', 'start_yield'), str(exc))
    except (OverflowError, ZeroDivisionError):
        fail('start_yield', 'Inputs exceed numerical precision; use less extreme prices or rates.')


@router.post('/api/returns')
def bond_returns(data: ReturnInputs):
    return calculate_return(data)


@router.post('/api/return-study')
def return_study(study: ReturnStudy):
    return dict(study=study.model_dump(mode='json'), result=calculate_return(study.inputs))


class YieldPointInputs(Inputs):
    date: date
    ytm: float = Field(ge=-.02, le=.30)


class HoldingInputs(Inputs):
    label: str = Field(min_length=1, max_length=40)
    face_value: float = Field(gt=0, le=1e9)
    coupon_rate: float = Field(ge=0, le=.20)
    issue_date: date
    maturity_date: date
    frequency: Literal[1, 2, 4, 12] = 2
    yields: List[YieldPointInputs] = Field(min_length=1, max_length=200)
    sale_date: Optional[date] = None


class PortfolioReturnInputs(Inputs):
    holdings: List[HoldingInputs] = Field(min_length=1, max_length=20)
    start_date: date
    end_date: date
    cash_rate: float = Field(default=0, ge=-.02, le=.30)
    cost_bp: float = Field(default=0, ge=0, le=100)
    end_treatment: Literal['mark', 'liquidate'] = 'liquidate'
    valuation_dates: List[date] = Field(default_factory=list, max_length=1000)


@router.post('/api/return-ledger')
def portfolio_returns(data: PortfolioReturnInputs):
    """Aggregate explicit step-yield paths, including optional early sales."""
    try:
        args = data.model_dump(exclude={'holdings'})
        args['holdings'] = [BondHolding(**h.model_dump(exclude={'yields'}),
            yields=tuple(YieldPoint(**p.model_dump()) for p in h.yields)) for h in data.holdings]
        return holding_period_ledger(**args)
    except ValueError as exc:
        fail(getattr(exc, 'field', 'holdings'), str(exc))
    except (OverflowError, ZeroDivisionError):
        fail('holdings', 'Inputs exceed numerical precision.')
