# Fixed-Income Lab — Status and Progress

**Updated:** October 31, 2026 (America/Chicago)

## Current status

**Phase 1 implementation and independent reference validation are complete
for the regular-coupon educational model.** The local website has six
interactive lessons. Phase 2, duration and convexity, is the next milestone;
Phases 2–9 have not been implemented. The plan now also includes a
credit and corporate bond extension (Phases 10–13); it has not been implemented.

Software completion does not mean the learner has completed the reflection
questions or demonstrated the learning checkpoints.

## Completed work

### Lessons and experiments

| Lesson | URL | Available experiments |
|---|---|---|
| 1. Bond Basics | `/lessons/bond-basics` | Coupon and principal cash-flow timelines |
| 2. Present Value & Bond Pricing | `/lessons/present-value` | Discounted payments, compounding conventions, and reinvestment comparisons |
| 3. Bond Pricing Lab | `/lessons/bond-pricing-lab` | Maturity, coupon, and payment-timing comparisons; exact yield-shock repricing |
| 4. Yield to Maturity | `/lessons/yield-to-maturity` | Solve yield from price; compare coupon rate, current yield, and YTM |
| 5. Settlement & Accrued Interest | `/lessons/settlement-and-accrued-interest` | Actual settlement dates, clean/dirty prices, dated YTM solving, and pull-to-par |
| 6. Treasury Bill Yields | `/lessons/treasury-bill-yields` | Discount quotations, investment yields, and the half-year convention change |

Each lesson has an overview card, sidebar entry, and previous/next navigation.
Python examples are optional and collapsed. Original notes and Notebook 01
remain preserved; website Markdown is the source for lesson content.

### Financial calculations

- Regular fixed-coupon schedules, zero-coupon pricing, and coupon-bond pricing.
- Price-to-YTM root finding, including zero and negative implied yields.
- Dated regular schedules, end-of-month handling, and leap-day accrual.
- Accrued interest and clean/dirty price conversion.
- Dated YTM solving from either a clean quote or the full dirty price.
- Treasury bill actual/360 discount pricing and 365/366 investment-year bases.
- Simple short-bill annualization and the longer-bill coupon-equivalent quadratic.
- Fixed-YTM clean/dirty price paths showing coupon resets and approach to maturity.

Calculations live in `src/filab/pricing/`. FastAPI endpoints are
`/api/valuation`, `/api/rates`, `/api/experiments`, `/api/yield`,
`/api/settlement`, and `/api/bills`; each accepts POST requests. API rates
are decimals, while browser controls display percentages. See `/docs` for
request and response schemas.

### Interface decisions and recent improvements

- Give distinct financial concepts their own lessons; YTM is a separate page.
- Show discrete choices as visible radio option cards, rather than dropdowns.
- Order payment frequencies **Annual → Semiannual → Quarterly**, followed
  by Monthly where available. Semiannual remains the default selection.
- Display purchase-price inputs to two decimal places, with one-cent steps;
  round typed prices when committed. Preserve calculation precision elsewhere.
- Label assumptions and distinguish immediate repricing from holding-period return.
- Explain why the Treasury bill yield formula changes at half a year:
  six months is one period in the semiannual coupon-bond benchmark.
  Lesson 6 includes the two growth formulas, a numerical comparison,
  an explanation beside the chart, and a dotted half-year marker.

## Validation and model limits

The latest full test run passed **221 tests**. Coverage includes pricing
identities, yield round trips, dated settlement, coupon boundaries, leap
years, bill conventions, API validation, and lesson navigation.

Independent checks use published Treasury examples for regular and reopened
bond prices, accrued interest, and short/long bill quotations. QuantLib is
not required. Details, source links, and tolerances are recorded in
[Phase 1 validation](notes/phase_1_validation.md).

Desktop/mobile browser checks covered the six lessons, visible choices,
calculations, disabled states, resets, keyboard navigation, and layout.
The payment-option reorder was checked in rendered HTML; the latest bill
explanation, formulas, and half-year marker were also checked in the browser.

Dated bonds use Actual/Actual coupon-period accrual and simple discounting
over the first fractional period, followed by compound full periods.
Settlement on a coupon date is after payment. The issue/accrual start date
must lie on the regular maturity-anchored coupon grid.

Stub coupons, holiday adjustments, ex-coupon rules, market settlement lags,
and auction-specific intermediate rounding are outside this model. The bill
investment-year basis is an explicit input. Historical market data and
discount-curve valuation have not yet been added.

## Running the project

From the project root, using the existing environment:

```bash
source .venv/bin/activate
python -m uvicorn filab.web.app:app --host 127.0.0.1 --port 8000
```

Open [the local website](http://127.0.0.1:8000). At the time of this summary,
one server is listening on port 8000. Stop it with Ctrl+C when finished;
restart it after Python code changes.

An earlier high-CPU issue came from bare `--reload` recursively polling the
project, including approximately 5,947 Python files in `.venv`. The watcher
and an extra test server were stopped. Normal startup now omits reload.
For development, restrict automatic reload to application source:

```bash
python -m uvicorn filab.web.app:app --reload --reload-dir src/filab --reload-delay 1 --host 127.0.0.1 --port 8000
```

Run the numerical and web tests with:

```bash
python -m pytest -q
```

## Next milestone

Build **Phase 2: Duration, Convexity, and Interest-Rate Risk**:

1. Implement Macaulay duration, modified duration, dollar duration, and DV01.
2. Add analytical and finite-difference duration and convexity checks.
3. Compare exact repricing with first- and second-order approximations for
   positive and negative 25, 50, 100, and 200 basis-point shocks.
4. Add separate financial lessons and a Bond Risk Explorer, retaining the
   visible controls and clear conventions established in Phase 1.
5. Validate approximation errors before marking Phase 2 complete.

Subsequent phases cover historical Treasury ingestion, curve construction,
holding-period returns, nonparallel curve risk, TIPS, monetary policy, and
an integrated strategy laboratory. The planned 5–6 week extension adds
credit fundamentals and ratings, noncallable corporate bond pricing and
Z-spreads, default/survival/recovery models, and spread risk and credit returns.
It follows the Treasury core by default; ratings and basic spread pricing
can begin after Phase 4, while credit return work depends on Phases 5–6.
Callable bonds, OAS, and advanced credit models remain optional research.
The current pricing code still implements only the Phase 1 model; this
curriculum expansion adds no corporate pricing support or website lessons.
Hosting, accounts, brokerage integration,
and real-time trading remain deferred.

The [project plan](fixed_income_lab_plan.md) contains the full curriculum;
the [README](README.md) contains setup and interface details.
