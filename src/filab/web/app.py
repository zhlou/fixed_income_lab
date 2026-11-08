"""Lesson pages and numerical endpoints. Run with uvicorn filab.web.app:app."""

from math import fsum, isclose
from dataclasses import asdict
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.container import container_plugin
from pydantic import BaseModel, ConfigDict, Field, model_validator

from filab.pricing import fixed_coupon_cashflows, price_coupon_bond, price_zero_coupon, yield_to_maturity
from filab.pricing import coupon_schedule, settled_bond_valuation, settled_yield_to_maturity, treasury_bill
from filab.pricing.settlement import SettlementError

from filab.data.treasury import pinned_snapshot
from filab.risk.explorer import compare_bonds
from .history_api import router as history_router
from .history_limits import HistoryBodyLimit
from .curriculum import LESSONS, ROADMAP
from .returns_api import router as returns_router
from .return_lessons import RETURN_LESSONS, lesson_spec, router as return_lesson_router

HERE = Path(__file__).resolve().parent
HISTORY_EXAMPLE = pinned_snapshot()["example"]
HISTORY_REFERENCE = pinned_snapshot("series-introduction")["example"]

markdown = MarkdownIt("commonmark", {"html": False}).enable("table").use(
    dollarmath_plugin, allow_space=False, allow_digits=False,
)

def reveal_answer(renderer, tokens, idx, options, env):
    if tokens[idx].nesting == 1:
        return '<details class="exercise-answer"><summary>Reveal the explanation</summary>\n'
    return '</details>\n'


markdown.use(container_plugin, 'answer', render=reveal_answer)
default_fence = markdown.renderer.rules["fence"]


def optional_code(tokens, idx, options, env):
    if env.get("expand_code"):
        return default_fence(tokens, idx, options, env)
    label = "Python implementation" if tokens[idx].info.strip() == "python" else "Example output"
    return '<details class="code-example"><summary>' + label + '</summary>' + default_fence(tokens, idx, options, env) + '</details>'


markdown.renderer.rules["fence"] = optional_code
templates = Jinja2Templates(directory=str(HERE / "templates"))
templates.env.globals['asset_versions'] = {
    path.name: sha256(path.read_bytes()).hexdigest()[:16]
    for path in (HERE / 'static').iterdir() if path.suffix in {'.js', '.css'}
}
app = FastAPI(title="Fixed-Income Lab", version="0.1.0")
app.add_middleware(HistoryBodyLimit)
app.include_router(history_router)
app.include_router(returns_router)
app.include_router(return_lesson_router)
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")


class Inputs(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")


class BondInputs(Inputs):
    instrument: Literal["coupon", "zero"] = "coupon"
    face_value: float = Field(default=1000, gt=0, le=1e9)
    coupon_rate: float = Field(default=0.04, ge=0, le=0.20)
    ytm: float = Field(default=0.05, ge=-0.02, le=0.30)
    maturity_years: float = Field(default=2, ge=0, le=50)
    frequency: Literal[1, 2, 4, 12] = 2


class RateInputs(Inputs):
    convention: Literal["nominal", "effective"] = "nominal"
    rate: float = Field(default=0.04, ge=0, le=0.30)
    frequency: Literal[1, 2, 4, 12] = 2
    face_value: float = Field(default=1000, gt=0, le=1e9)


class YieldInputs(Inputs):
    face_value: float = Field(default=100, gt=0, le=1e9)
    price: float = Field(default=98.12, gt=0, le=1e9)
    coupon_rate: float = Field(default=0.04, ge=0, le=0.20)
    maturity_years: float = Field(default=2, gt=0, le=50)
    frequency: Literal[1, 2, 4, 12] = 2


class ExperimentInputs(Inputs):
    mode: Literal["maturity", "coupon", "sensitivity"] = "maturity"
    coupon_rate: float = Field(default=0.06, ge=0, le=0.12)
    ytm: float = Field(default=0.05, ge=0, le=0.10)
    maturity_years: float = Field(default=20, gt=0, le=30)
    payment_type: Literal["coupon", "zero"] = "zero"


class SettlementInputs(Inputs):
    mode: Literal['price', 'yield'] = 'price'
    issue_date: date = date(2025, 11, 15)
    settlement_date: date = date(2026, 8, 15)
    maturity_date: date = date(2028, 11, 15)
    face_value: float = Field(default=100, gt=0, le=1e9)
    coupon_rate: float = Field(default=0.04, ge=0, le=0.20)
    ytm: float = Field(default=0.05, ge=-0.02, le=0.30)
    price: float = Field(default=98, gt=0, le=1e9)
    price_type: Literal['clean', 'dirty'] = 'clean'
    frequency: Literal[2] = 2


class BillInputs(Inputs):
    face_value: float = Field(default=100, gt=0, le=1e9)
    discount_rate: float = Field(default=0.05, ge=0, le=0.30)
    days_to_maturity: int = Field(default=182, ge=1, le=366)
    year_days: Literal[365, 366] = 365


def input_error(field, message):
    raise HTTPException(status_code=422, detail=[{"loc": ["body", field], "msg": message}])


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Avoid echoing invalid non-finite JSON values back into a JSON response.
    return JSONResponse(status_code=422, content={"detail": [
        {"loc": list(error["loc"]), "msg": error["msg"]} for error in exc.errors()
    ]})


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html", context={
        "lessons": LESSONS, "roadmap": ROADMAP, "active": "home", "page_title": "Explore how bonds work",
    })


@app.get("/lessons/{slug}")
def lesson(request: Request, slug: str):
    if slug == "cash-flows-and-pricing":
        return RedirectResponse("/lessons/present-value#under-the-hood", status_code=308)
    index = next((i for i, item in enumerate(LESSONS) if item["slug"] == slug), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    item = LESSONS[index]
    content = (HERE / "content" / item["file"]).read_text()
    return templates.TemplateResponse(request=request, name="lesson.html", context={
        "lessons": LESSONS, "lesson": item, "lesson_number": index + 1,
        "active": slug, "page_title": item["title"], "body": markdown.render(content),
        "history_example": HISTORY_EXAMPLE, "history_reference": HISTORY_REFERENCE,
        "return_experiment": lesson_spec(slug) if slug in RETURN_LESSONS else None,
        "implementation": markdown.render((HERE / "content" / "pricing.md").read_text(), {"expand_code": True}) if slug == "present-value" else None,
        "previous": LESSONS[index - 1] if index > 0 else None,
        "next": LESSONS[index + 1] if index + 1 < len(LESSONS) else None,
    })


@app.post("/api/valuation")
def valuation(data: BondInputs):
    args = dict(face_value=data.face_value, ytm=data.ytm,
                maturity_years=data.maturity_years, frequency=data.frequency)
    if data.instrument == "zero":
        price = price_zero_coupon(**args)
        payments = [(data.maturity_years, 0.0, data.face_value)]
    else:
        try:
            flows = fixed_coupon_cashflows(face_value=data.face_value, coupon_rate=data.coupon_rate,
                                           maturity_years=data.maturity_years, frequency=data.frequency)
        except ValueError as exc:
            input_error("maturity_years", str(exc))
        price = price_coupon_bond(coupon_rate=data.coupon_rate, **args)
        coupon = data.face_value * data.coupon_rate / data.frequency
        payments = [(flow.time_years, coupon, data.face_value if i == len(flows) - 1 else 0)
                    for i, flow in enumerate(flows)]
    cashflows = []
    for time, coupon, principal in payments:
        factor = (1 + data.ytm / data.frequency) ** (-data.frequency * time)
        cashflows.append(dict(time_years=time, coupon=coupon, principal=principal,
                              amount=coupon + principal, discount_factor=factor,
                              coupon_present_value=coupon * factor,
                              principal_present_value=principal * factor,
                              present_value=(coupon + principal) * factor))
    principal_pv = fsum(flow["principal"] * flow["discount_factor"] for flow in cashflows)
    coupon_pv = fsum(flow["coupon"] * flow["discount_factor"] for flow in cashflows)
    return dict(price=price, principal_pv=principal_pv, coupon_pv=coupon_pv,
                total_received=fsum(flow["amount"] for flow in cashflows),
                total_coupons=fsum(flow["coupon"] for flow in cashflows),
                payment_coupon=cashflows[0]["coupon"],
                classification="At par" if isclose(price, data.face_value, rel_tol=1e-9) else
                ("Premium" if price > data.face_value else "Discount"), cashflows=cashflows)


@app.post("/api/yield")
def implied_yield(data: YieldInputs):
    args = dict(face_value=data.face_value, coupon_rate=data.coupon_rate,
                maturity_years=data.maturity_years, frequency=data.frequency)
    try:
        flows = fixed_coupon_cashflows(**args)
    except ValueError as exc:
        input_error("maturity_years", str(exc))
    try:
        ytm = yield_to_maturity(price=data.price, **args)
        cashflows = []
        for flow in flows:
            factor = (1 + ytm / data.frequency) ** (-data.frequency * flow.time_years)
            cashflows.append(dict(time_years=flow.time_years, amount=flow.amount,
                                  discount_factor=factor, present_value=flow.amount * factor))
        repriced = price_coupon_bond(ytm=ytm, **args)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        input_error("price", str(exc))
    return dict(ytm=ytm, coupon_rate=data.coupon_rate,
                current_yield=data.face_value * data.coupon_rate / data.price,
                price=data.price, repriced=repriced, residual=repriced - data.price,
                cashflows=cashflows)


@app.post("/api/rates")
def rates(data: RateInputs):
    nominal = data.rate if data.convention == "nominal" else data.frequency * ((1 + data.rate) ** (1 / data.frequency) - 1)
    effective = (1 + nominal / data.frequency) ** data.frequency - 1
    held_interest = data.face_value * nominal
    reinvested_interest = data.face_value * effective
    return dict(nominal_rate=nominal, effective_rate=effective, period_rate=nominal / data.frequency,
                coupon_per_payment=data.face_value * nominal / data.frequency,
                held_interest=held_interest, reinvested_interest=reinvested_interest,
                extra_interest=reinvested_interest - held_interest)


@app.post('/api/settlement')
def settlement(data: SettlementInputs):
    args = dict(face_value=data.face_value, coupon_rate=data.coupon_rate, frequency=data.frequency,
                issue_date=data.issue_date, maturity_date=data.maturity_date,
                settlement_date=data.settlement_date)
    try:
        if (data.maturity_date - data.issue_date).days > 366 * 50:
            raise SettlementError('maturity_date', 'The lesson supports at most 50 years.')
        ytm = data.ytm if data.mode == 'price' else settled_yield_to_maturity(
            price=data.price, price_type=data.price_type, **args)
        result = settled_bond_valuation(ytm=ytm, **args)
        schedule = coupon_schedule(issue_date=data.issue_date, maturity_date=data.maturity_date)
        horizon = (data.maturity_date - data.settlement_date).days - 1
        offsets = {round(horizon * k / 40) for k in range(41)}
        for payment in schedule:
            offset = (payment - data.settlement_date).days
            offsets.update(k for k in [offset - 1, offset] if 0 <= k <= horizon)
        path = []
        for offset in sorted(offsets):
            when = data.settlement_date + timedelta(days=offset)
            value = settled_bond_valuation(ytm=ytm, **dict(args, settlement_date=when))
            path.append(dict(date=when, x=offset / 365.25, clean=value.clean_price,
                             dirty=value.dirty_price, accrued=value.accrued_interest))
    except SettlementError as exc:
        input_error(exc.field, str(exc))
    except (ValueError, OverflowError) as exc:
        input_error('price' if data.mode == 'yield' else 'ytm', str(exc))
    return dict(asdict(result), ytm=ytm, path=path,
                price_residual=None if data.mode == 'price' else
                (result.clean_price if data.price_type == 'clean' else result.dirty_price) - data.price)


@app.post('/api/bills')
def bills(data: BillInputs):
    try:
        result = treasury_bill(**data.model_dump())
        days = sorted({1, 366, data.days_to_maturity} | set(range(7, 367, 7)))
        samples = [treasury_bill(**dict(data.model_dump(), days_to_maturity=day)) for day in days]
        result['curves'] = [dict(label=label, points=[dict(x=day, y=value[key]) for day, value in zip(days, samples)],
                                 marker=dict(x=data.days_to_maturity, y=result[key]))
                            for label, key in [('Bank discount yield', 'discount_rate'),
                                               ('Coupon-equivalent yield', 'investment_rate')]]
        return result
    except ValueError as exc:
        input_error('discount_rate', str(exc))


@app.post("/api/experiments")
def experiments(data: ExperimentInputs):
    if not isclose(data.maturity_years * 2, round(data.maturity_years * 2), abs_tol=1e-9):
        input_error("maturity_years", "Choose a whole number of half-year periods.")

    def price(coupon, maturity, ytm):
        return price_coupon_bond(face_value=100, coupon_rate=coupon,
                                 maturity_years=maturity, ytm=ytm, frequency=2)

    if data.mode == "maturity":
        coupon, maturity = 0.04, data.maturity_years
        title = "Change maturity. Keep the coupon fixed."
        insight = (f"Selected maturity: {maturity:g} years; baseline: 10 years. "
                   "Both pay $2 every six months. Changing maturity changes the number of "
                   "coupons and the date principal is repaid. "
                   "Compare the percentage response to the same yield shock below.")
    elif data.mode == "coupon":
        coupon, maturity = data.coupon_rate, 10
        title = "Change the coupon. Keep maturity fixed."
        insight = (f"Both bonds mature in 10 years. The selected bond pays ${100 * coupon / 2:.2f} "
                   "every six months; the baseline pays $2. Larger payments have a higher "
                   "price at the same YTM.")
    else:
        coupon, maturity = (0 if data.payment_type == "zero" else 0.04), 10
        title = "Change when the money arrives."
        insight = ("The zero-coupon bond pays only $100 at year 10. The baseline pays $2 "
                   "every six months as well as principal at maturity. The dollar-price "
                   "axis stays the same; use the table to compare percentage sensitivity. "
                   "Removing coupons changes the total cash received as well as its timing.")
    identical = coupon == 0.04 and maturity == 10
    if identical:
        insight = "The selected bond matches the baseline, so the curves coincide. " + insight
    grid = [i / 1000 for i in range(101)]
    selected_label = f"Selected · {maturity:g}y · {coupon * 100:g}% coupon"
    specs = [("Baseline · 10y · 4% coupon", 0.04, 10, True),
             (selected_label, coupon, maturity, False)]
    curves, rows = [], []
    for label, rate, years, baseline in specs:
        current = price(rate, years, data.ytm)
        shocked = price(rate, years, data.ytm + 0.01)
        curves.append(dict(label=label, baseline=baseline,
                           points=[dict(x=y, y=price(rate, years, y)) for y in grid],
                           marker=dict(x=data.ytm, y=current)))
        rows.append([label, f"{current:.2f}", f"{shocked:.2f}", f"{shocked / current - 1:+.2%}"])
    timeline = valuation(BondInputs(instrument="zero" if coupon == 0 else "coupon", face_value=100, coupon_rate=coupon,
                                    maturity_years=maturity, ytm=data.ytm))
    return dict(curves=curves, rows=rows,
                headers=["Bond", f"Price at {data.ytm:.2%}", f"Price at {data.ytm + 0.01:.2%}", "Price change (%)"],
                title=title, x_label="Annual nominal YTM · semiannual compounding",
                y_label="Price per $100 face", percent_y=False, y_domain=[0, 250],
                reference_x=data.ytm, reference_y=100, insight=insight,
                timeline=timeline, timeline_label=f"{maturity:g}-year bond · {coupon * 100:g}% coupon · $100 principal",
                identical=identical)


class RiskInputs(Inputs):
    mode: Literal['regular', 'dated'] = 'regular'
    face_value: float = Field(default=100, ge=100, le=1e7)
    ytm: float = Field(default=.05, ge=-.02, le=.20)
    frequency: Literal[1, 2, 4, 12] = 2
    coupon_rate: float = Field(default=.04, ge=0, le=.20)
    maturity_years: float = Field(default=2, ge=1, le=30)
    comparison_coupon_rate: float = Field(default=.04, ge=0, le=.20)
    comparison_maturity_years: float = Field(default=10, ge=1, le=30)
    issue_date: date = date(2025, 11, 15)
    settlement_date: date = date(2026, 8, 15)
    maturity_date: date = date(2028, 11, 15)
    comparison_maturity_date: date = date(2036, 11, 15)
    shock_bp: int = Field(default=100, ge=-200, le=200)


class RiskStudy(Inputs):
    # Required literals prevent silently accepting future or incompatible files.
    schema_version: Literal[1]
    kind: Literal['filab-bond-risk']
    conventions: Literal['nominal-yield-risk-v1']
    inputs: RiskInputs

    @model_validator(mode='before')
    @classmethod
    def complete_snapshot(cls, value):
        if isinstance(value, dict):
            if type(value.get('schema_version')) is not int:
                raise ValueError('The comparison version must be an integer.')
            fields = value.get('inputs')
            if not isinstance(fields, dict) or set(fields) != set(RiskInputs.model_fields):
                raise ValueError('A saved comparison must include every input and its conventions.')
        return value


def calculate_risk(data):
    try:
        return compare_bonds(**data.model_dump())
    except SettlementError as exc:
        input_error(exc.field, str(exc))
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        input_error('ytm', str(exc))


@app.post('/api/risk')
def risk(data: RiskInputs):
    return calculate_risk(data)


@app.post('/api/risk-study')
def risk_study(study: RiskStudy):
    result = calculate_risk(study.inputs)
    return dict(study=study.model_dump(mode='json'), result=result)


@app.get('/tools/bond-risk')
def risk_tool(request: Request):
    return templates.TemplateResponse(request=request, name='risk.html', context={
        'lessons': LESSONS, 'active': 'bond-risk', 'page_title': 'Bond Risk Explorer',
    })


@app.get('/tools/bond-return')
def return_tool(request: Request):
    return templates.TemplateResponse(request=request, name='returns.html', context={
        'lessons': LESSONS, 'active': 'bond-return', 'page_title': 'Bond Return Calculator',
    })


@app.get('/tools/treasury-history')
def history_tool(request: Request):
    return templates.TemplateResponse(request=request, name='history.html', context={
        'lessons': LESSONS, 'active': 'treasury-history', 'page_title': 'Treasury History Viewer',
        'history_example': HISTORY_EXAMPLE, 'history_reference': HISTORY_REFERENCE,
    })
