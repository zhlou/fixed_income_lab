"""Bounded M2 teaching experiments over the shared return ledger.

Each lesson accepts only its financial levers. Fixed dates, face amounts, cash
treatment and settlement conventions are set here, rather than hidden browser
inputs. The standalone calculator and existing numerical APIs retain their full
interfaces. No new pricing or cash-growth convention is introduced.
"""
from datetime import date
from typing import Dict, Literal

from fastapi import APIRouter, HTTPException
from pydantic import Field, ValidationError

from .returns_api import Inputs, ReturnInputs, calculate_return, fail

router = APIRouter()


class TotalReturnControls(Inputs):
    end_yield: float = Field(default=.07, ge=-.02, le=.20)
    cost_bp: float = Field(default=0, ge=0, le=100)
    end_treatment: Literal['mark', 'liquidate'] = 'liquidate'


class CouponControls(Inputs):
    start_date: date = Field(default=date(2026, 11, 14), ge=date(2026, 11, 1), le=date(2026, 11, 16))
    end_date: date = Field(default=date(2026, 11, 16), ge=date(2026, 11, 14), le=date(2026, 11, 30))
    coupon_rate: float = Field(default=.04, ge=0, le=.08)


class CashControls(Inputs):
    cash_rate: float = Field(default=.05, ge=-.02, le=.10)
    coupon_rate: float = Field(default=.04, ge=0, le=.08)
    horizon: Literal['first_coupon', 'maturity', 'after_maturity'] = 'maturity'


class PullToParControls(Inputs):
    coupon_rate: float = Field(default=.04, ge=0, le=.08)
    start_yield: float = Field(default=.05, ge=-.02, le=.10)
    horizon: Literal['maturity', 'before_maturity', 'early_sale'] = 'maturity'
    end_yield: float = Field(default=.07, ge=-.02, le=.20)


def number(name, label, low, high, step, unit='%', hint='', rate=True):
    return dict(name=name, label=label, kind='number', min=low, max=high,
                step=step, unit=unit, hint=hint, rate=rate)


def choice(name, label, options):
    return dict(name=name, label=label, kind='choice', options=options)


HORIZONS = [('maturity', 'At maturity', 'Nov 15, 2028'),
            ('before_maturity', 'Day before maturity', 'Nov 14, 2028'),
            ('early_sale', 'Sell after six months', 'May 15, 2027')]

RETURN_LESSONS = {
    'holding-period-returns': dict(
        model=TotalReturnControls, default_example='yield-rise',
        instruction='Change the exit yield or trading cost. Compare the bond price change with the investment return.',
        input_title='Change the exit.', chart_title='Price change and investment return.',
        table_title='FROM PRICE CHANGE TO TOTAL PROFIT',
        fixed='One $100 face bond, 4% coupon, semiannual payments. Buy November 15, 2026 after payment at 5% nominal YTM; horizon May 15, 2027; maturity November 15, 2028. Cash earns 0%.',
        controls=[number('end_yield', 'YTM at the horizon', -2, 20, .25),
                  number('cost_bp', 'One-way trading cost', 0, 100, 1, 'bp',
                         'Basis points of face, on purchase and sale. Marking has no exit fee.', False),
                  choice('end_treatment', 'At the horizon', [('mark', 'Keep & value', 'Unrealized remaining value'),
                         ('liquidate', 'Sell', 'Proceeds after the coupon')])],
        examples=[dict(id='yield-rise', label='Yield rises to 7%', controls={}),
                  dict(id='unchanged-yield', label='Yield stays at 5%', controls={'end_yield':.05})]),
    'coupons-and-return': dict(
        model=CouponControls, default_example='coupon-window',
        instruction='Move purchase and valuation around November 15. Follow accrued interest, the coupon, and total wealth.',
        input_title='Cross the coupon date.', chart_title='The coupon moves value into cash.',
        table_title='CLEAN + ACCRUED = DIRTY; DIRTY + CASH = WEALTH',
        fixed='One $100 face bond, semiannual coupons, 5% nominal YTM held fixed. Coupon date November 15, 2026; issue November 15, 2025; maturity November 15, 2028. Cash earns 0%, no costs, and the bond stays held at the horizon.',
        controls=[dict(name='start_date', label='Purchase settlement', kind='date', min='2026-11-01', max='2026-11-16'),
                  dict(name='end_date', label='Valuation date', kind='date', min='2026-11-14', max='2026-11-30'),
                  number('coupon_rate', 'Annual coupon', 0, 8, .25)],
        examples=[dict(id='coupon-window', label='Buy before the coupon', controls={}),
                  dict(id='coupon-date-purchase', label='Buy on the coupon date', controls={'start_date':'2026-11-15'})]),
    'reinvestment-and-cash': dict(
        model=CashControls, default_example='five-percent-cash',
        instruction='Change only the cash rate first. The chart isolates extra wealth from cash growth; the table compares both cash policies.',
        input_title='Give coupons a cash rate.', chart_title='Same bond. Different cash growth.',
        table_title='CHANGE ONLY THE CASH ASSUMPTION',
        fixed='One $100 face bond, annual coupons, 5% annual YTM held fixed. Buy at issue November 15, 2025; maturity November 15, 2027. No fees. Surviving bonds are valued at the horizon. Cash uses annual effective interest and Actual/365 Fixed.',
        controls=[number('cash_rate', 'Annual effective cash rate', -2, 10, .25,
                         hint='Compare against 0% in the chart and table. This rate is separate from bond YTM.'),
                  number('coupon_rate', 'Annual coupon', 0, 8, .25),
                  choice('horizon', 'Investment horizon', [('first_coupon', 'First coupon', 'Nov 15, 2026'),
                         ('maturity', 'At maturity', 'Nov 15, 2027'),
                         ('after_maturity', '365 days after maturity', 'Nov 14, 2028')])],
        examples=[dict(id='five-percent-cash', label='Cash earns 5%', controls={}),
                  dict(id='zero-cash', label='Cash earns 0%', controls={'cash_rate':0})]),
    'pull-to-par': dict(
        model=PullToParControls, default_example='discount-bond',
        instruction='Compare coupon with purchase YTM. Keep yield fixed to inspect price convergence, then test an early sale.',
        input_title='Change coupon or horizon.', chart_title='Follow clean and dirty prices toward maturity.',
        table_title='TERMINAL CASH AND THE REMAINING POSITION',
        fixed='One $100 face bond, semiannual payments. Buy November 15, 2026 after payment; issue November 15, 2025; maturity November 15, 2028. Cash earns 0%, no fees. YTM stays fixed unless you choose an early sale with a new yield.',
        controls=[number('coupon_rate', 'Annual coupon', 0, 8, .25),
                  number('start_yield', 'Purchase nominal YTM', -2, 10, .25),
                  choice('horizon', 'Investment horizon', HORIZONS),
                  dict(**number('end_yield', 'YTM at the early sale', -2, 20, .25),
                       when=dict(field='horizon', value='early_sale'))],
        examples=[dict(id='discount-bond', label='Discount bond', controls={}),
                  dict(id='premium-bond', label='Premium bond', controls={'coupon_rate':.06}),
                  dict(id='early-sale', label='Early sale', controls={'horizon':'early_sale'})]),
}


def lesson_spec(slug):
    """Public teaching metadata; defaults use the same typed controls as POST."""
    profile = RETURN_LESSONS[slug]
    public = {key: value for key, value in profile.items() if key != 'model'}
    public['slug'] = slug
    public['examples'] = [dict(example, controls=profile['model'](**example['controls']).model_dump(mode='json'))
                          for example in profile['examples']]
    public['initial'] = next(e['controls'] for e in public['examples'] if e['id'] == public['default_example'])
    return public


class LessonReturnRequest(Inputs):
    example: str
    controls: Dict = Field(default_factory=dict)


def lesson_return_inputs(slug, request):
    """Map only the allowed teaching controls to a complete calculator scenario."""
    if slug not in RETURN_LESSONS:
        raise HTTPException(404, detail='Return lesson not found')
    profile = RETURN_LESSONS[slug]
    example = next((e for e in profile['examples'] if e['id'] == request.example), None)
    if example is None:
        fail('example', 'Choose an example from this lesson.')
    try:
        controls = profile['model'](**dict(example['controls'], **request.controls))
    except ValidationError as exc:
        raise HTTPException(422, detail=[dict(loc=['body', 'controls', *error['loc']], msg=error['msg'])
                                        for error in exc.errors()]) from exc
    values = controls.model_dump()
    args = dict(face_value=100, purchase_method='yield', include_comparison=False,
                issue_date=date(2025, 11, 15), frequency=2, coupon_rate=.04,
                start_yield=.05, cash_policy='zero', cash_rate=0, cost_bp=0,
                start_date=date(2026, 11, 15), end_date=date(2028, 11, 15),
                maturity_date=date(2028, 11, 15), yield_path='fixed', end_treatment='liquidate')
    if slug == 'holding-period-returns':
        args.update(values, end_date=date(2027, 5, 15), yield_path='shock', shock_date=date(2027, 5, 15))
    elif slug == 'coupons-and-return':
        args.update(values, end_treatment='mark')
    elif slug == 'reinvestment-and-cash':
        args.update(coupon_rate=controls.coupon_rate, cash_rate=controls.cash_rate,
                    start_date=date(2025, 11, 15), maturity_date=date(2027, 11, 15),
                    end_date={'first_coupon':date(2026,11,15), 'maturity':date(2027,11,15),
                              'after_maturity':date(2028,11,14)}[controls.horizon],
                    frequency=1, cash_policy='interest', end_treatment='mark')
    else:
        args.update(coupon_rate=controls.coupon_rate, start_yield=controls.start_yield)
        if controls.horizon == 'early_sale':
            args.update(end_date=date(2027,5,15), yield_path='shock', shock_date=date(2027,5,15),
                        end_yield=controls.end_yield)
        elif controls.horizon == 'before_maturity':
            args.update(end_date=date(2028,11,14), end_treatment='mark')
    return ReturnInputs(**args), controls


def metric(label, value, kind='money', detail=''):
    return dict(label=label, value=value, kind=kind, detail=detail)


def curve(label, path, key):
    return dict(label=label, points=[dict(x=p['days'], y=p[key]) for p in path])


def focused_results(slug, data, controls):
    """Derived views of ledger values; all financial arithmetic stays in Python."""
    r, inputs = data['result'], data['inputs']
    period = metric('Holding-period return', r['total_return'], 'percent', 'Whole period · not annualized')
    common = dict(x_label='Actual days after purchase settlement', y_label='Dollars per $100 face',
                  percent_x=False, x_unit='days')
    if slug == 'holding-period-returns':
        metrics = [period, metric('Dirty price change', r['dirty_price_change']/r['purchase_dirty'], 'percent',
                                  'Excludes coupons and trading costs'), metric('Coupons received', r['coupons'])]
        price_points, return_points = [], []
        for p in r['path']:
            # A sale moves the bond into cash; its pre-sale price is still the
            # price comparator, rather than the now-zero remaining position.
            mark = p['bond_value'] if p['faces']['Bond A'] else r['positions'][0]['dirty']
            price_points.append(dict(x=p['days'],y=mark/r['purchase_dirty']-1))
            return_points.append(dict(x=p['days'],y=p['wealth']/r['beginning_wealth']-1))
        plot = dict(common, title='Dirty price change versus holding-period investment return',
                    y_label='Change since purchase (%)', percent_y=True, reference_y=0,
                    curves=[dict(label='Investment return',points=return_points),dict(label='Dirty price change only',points=price_points)])
        columns = [('Component','text'),('Dollars','money')]
        rows = [['Dirty price change',r['dirty_price_change']],['Coupons received',r['coupons']],
                ['Purchase costs',-r['purchase_fees']],['Sale costs',-r['sale_fees']],
                ['Net profit',r['net_profit']],['Beginning wealth',r['beginning_wealth']],['Ending wealth',r['ending_wealth']]]
        note = 'Price change excludes coupons and costs and uses dirty purchase price as its base. Investment return includes credited cash and costs, using opening capital including entry fees. Entry fees can therefore make the opening marked return negative.'
    elif slug == 'coupons-and-return':
        metrics = [metric('Net profit',r['net_profit'],detail='Coupon receipt less price/accrual changes'),
                   metric('Accrued interest paid',r['purchase_accrued']),metric('Coupons received',r['coupons'])]
        plot = dict(common, title='Dirty bond value versus bond value plus credited cash', reference_x=(date(2026,11,15)-controls.start_date).days,
                    curves=[curve('Total wealth',r['path'],'wealth'),curve('Dirty bond value',r['path'],'bond_value')])
        columns = [('Date','text'),('Clean','money'),('Accrued','money'),('Dirty','money'),('Cash','money'),('Wealth','money')]
        dates = {inputs['start_date'],inputs['end_date'],'2026-11-14','2026-11-15','2026-11-16'}
        rows = [[p['date'],p['clean_value'],p['accrued_interest'],p['bond_value'],p['cash'],p['wealth']]
                for p in r['path'] if p['date'].isoformat() in dates]
        note = 'The marked bond stays invested. The gap between the curves is credited cash. When inside the window, the vertical marker is the November 15 coupon. Prices use clean + accrued = dirty.'
    elif slug == 'reinvestment-and-cash':
        metrics = [metric('Cash-account interest',r['cash_interest'],detail='Interest on credited receipts'),
                   metric('Ending wealth',r['ending_wealth']),period]
        zero_path = data['cash_comparison'][0]['path']
        extra = [dict(x=p['days'],y=p['wealth']-zero['wealth']) for p,zero in zip(r['path'],zero_path)]
        plot = dict(common, title='Additional wealth from the explicit cash rate relative to zero-interest cash',
                    y_label='Extra wealth from cash interest ($)', reference_y=0,
                    curves=[dict(label='Extra wealth from cash growth',points=extra),
                            dict(label='0% cash reference',baseline=True,points=[dict(x=p['days'],y=0) for p in zero_path])])
        columns = [('Cash rate','percent'),('Cash interest','money'),('Ending wealth','money'),('Period return','percent')]
        rows = [[row['rate'],row['cash_interest'],row['ending_wealth'],row['total_return']] for row in data['cash_comparison']]
        note = 'The chart shows additional wealth relative to holding cash at 0%; the table shows both ending wealth amounts. Bond prices and payments match. Cash uses Actual/365 Fixed, and new receipts earn from their receipt date.'
    else:
        position = r['positions'][0]
        prices = [dict(p, clean=p['clean_value'], dirty=p['bond_value']) for p in r['path']
                  if p['date'] < date.fromisoformat(inputs['maturity_date'])]
        if position['status'] == 'sold':
            prices[-1] = dict(prices[-1],clean=position['clean'],dirty=position['dirty'])
        metrics = [metric('Clean purchase price',r['purchase_clean']),metric('Ending wealth',r['ending_wealth']),period]
        plot = dict(common, title='Clean and dirty bond prices before sale or redemption', reference_y=100,
                    curves=[curve('Clean price',prices,'clean'),curve('Dirty price',prices,'dirty')])
        columns = [('Terminal item','text'),('Dollars','money')]
        rows = [['Coupons received',r['coupons']],['Principal redeemed' if position['status']=='redeemed' else
                'Gross sale proceeds' if position['status']=='sold' else 'Dirty price at the horizon',position['dirty']],
                ['Ending cash',r['ending_cash']],['Remaining bond value',r['ending_bond_value']],
                ['Face still held',position['ending_face']],['Ending wealth',r['ending_wealth']]]
        note = ('Prices stop on the day before maturity. At maturity the final coupon and $100 principal move to cash, leaving zero face held.'
                if position['status']=='redeemed' else 'Prices include the horizon mark before any sale. Coupon cash is separate; this price chart is not a total-return chart.')
    return dict(metrics=metrics, plot=plot, columns=columns, rows=rows, note=note,
                chart_title=RETURN_LESSONS[slug]['chart_title'], table_title=RETURN_LESSONS[slug]['table_title'])


@router.post('/api/lesson-returns/{slug}')
def return_lesson(slug: str, request: LessonReturnRequest):
    inputs, controls = lesson_return_inputs(slug, request)
    data = calculate_return(inputs, include_cash_paths=slug == 'reinvestment-and-cash')
    return dict(inputs=data['inputs'], controls=controls.model_dump(mode='json'), result=data['result'],
                focus=focused_results(slug,data,controls), conventions=data['conventions'])
