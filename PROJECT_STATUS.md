# Fixed-Income Lab — Status and Progress

**Updated:** November 3, 2026 (America/Chicago)

## Current status

**Foundations implementation and independent reference validation are complete
for the regular-coupon educational model** (original Phase 1, now M0).
The local website has **nine interactive lessons**. **M1 risk calculations,
lessons, and the Bond Risk Explorer are implemented and validated. M2 return
accounting is next.** No M2–M7 calculation or research module is implemented.

The revised plan prioritizes the user's intended daily use: **researching bond
strategies and historical returns**. It brings return accounting forward, targets
a small two-strategy historical research release at M5, and places TIPS, macro,
credit, and advanced models after the nominal Treasury research core.

Software completion does not mean the learner has completed the reflection
questions or demonstrated the learning checkpoints.

## Completed work

### Docker runtime — November 3, 2026

Added a Python 3.12 slim image that installs the packaged application with its
`web` extra, includes all lesson and formula assets, runs as an unprivileged
user, and serves on container port 8000 without reload. A homepage health check
reports container readiness. `.dockerignore` limits uploads to installation
inputs and excludes local environments, Git history, tests, notebooks, and caches.

The image needs no runtime bind mounts or volumes. Build/run commands preserve
the selected Docker context; the README explains remote-host port publishing,
SSH tunneling, rebuilding, health/log inspection, and cleanup. This adds a runtime
option for the existing M0/M1 website; curriculum and financial conventions are
unchanged.

Validation on the selected `deepl` engine (`ssh://deepl.lan`, Linux/amd64):

- `docker build --tag fixed-income-lab:local .` succeeded, uploading a 1.715 MB
  context from the macOS/arm64 client. No source bind mounts or volumes were used.
- All **313 tests passed locally** and **313 passed inside the container** against
  the installed package as the unprivileged user. Tests were copied with
  `docker cp`; only the disposable verification container received `pytest` and
  `httpx`. The runtime image excludes test and notebook dependencies.
- HTTP checks passed for 19 pages/assets (all nine lessons, overview, standalone
  tool, API docs/schema, and bundled scripts/styles/fonts) plus eight API checks,
  including a known price and invalid-input rejection. Resources resolved from
  the installed package. Docker reported the container healthy.
- A fresh container with `--network none` served 17 lesson/tool/asset URLs and
  seven numerical APIs successfully and became healthy. A client HTTP request
  through an SSH tunnel to the remote published port returned 200.
- Temporary containers and the tunnel were stopped after verification. The
  `fixed-income-lab:local` image remains available on the remote engine.

The client currently falls back to the legacy Docker builder and emits its
deprecation notice because Buildx is absent. The container test run also emitted
one upstream Starlette/httpx test-client deprecation warning; all checks passed.
Dependencies remain unlocked under the existing `pyproject.toml` policy. No UI
or financial calculation changes were made, so no new visual or reference-price
benchmark review was required.

### Lesson clarity review — November 3, 2026

Reviewed and revised all nine canonical website lessons, and reviewed the optional
Python supplement plus the original notes and notebook. Added explicit learning
goals, definitions before formulas, guided experiments, and worked steps for YTM,
settlement, payment weights, and risk approximations. Foundation exercises now
use the existing keyboard-accessible answer reveals. Reordered the effective
annual rate discussion before the final checkpoint, clarified units and negative
yield boundaries, corrected the Treasury bill appendix reference, and replaced
outdated phase wording with M0/M1 navigation.

All **313 tests passed**. Independent arithmetic checks reproduced lesson prices,
yield solutions, dated settlement, bill quotations, and duration/convexity examples.
Browser checks on all nine lessons at **1440×900 and 390×900** covered formulas,
page/reading-panel width, keyboard answer reveals, optional code, live results,
and YTM input/reset. No formula-rendering or browser console errors were observed.
The existing local server was reused. Original learning artifacts remain preserved;
learner reflection is still pending. See [the review record](notes/lesson_content_review.md).

### Lessons and experiments

| Lesson | URL | Available experiments |
|---|---|---|
| 1. Bond Basics | `/lessons/bond-basics` | Coupon and principal cash-flow timelines |
| 2. Present Value & Bond Pricing | `/lessons/present-value` | Discounted payments, compounding conventions, and reinvestment comparisons |
| 3. Bond Pricing Lab | `/lessons/bond-pricing-lab` | Maturity, coupon, and payment-timing comparisons; exact yield-shock repricing |
| 4. Yield to Maturity | `/lessons/yield-to-maturity` | Solve yield from price; compare coupon rate, current yield, and YTM |
| 5. Settlement & Accrued Interest | `/lessons/settlement-and-accrued-interest` | Actual settlement dates, clean/dirty prices, dated YTM solving, and pull-to-par |
| 6. Treasury Bill Yields | `/lessons/treasury-bill-yields` | Discount quotations, investment yields, and the half-year convention change |
| 7. Cash-flow timing & duration | `/lessons/macaulay-duration` | Present-value weights, zero/coupon comparisons, Macaulay duration |
| 8. Modified duration & DV01 | `/lessons/modified-duration-dv01` | Yield sensitivity, face scaling, dated numerical checks |
| 9. Convexity & approximation error | `/lessons/convexity` | Exact vs first/second-order repricing and signed shock errors |

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

- Place experiments and explanations side by side at desktop widths of 1200px
  and above, with independent scrolling and most of the width for the experiment.
  Lesson navigation opens from the Course button; narrower screens stack the
  sections with direct links between them. Risk charts precede detailed measures.
- Keep the desktop page within the viewport and contain positioned formula
  accessibility content inside its panel, preventing blank outer-page scrolling.
  Add Overview, Previous, Next, and the lesson position to the top bar.
- Give distinct financial concepts their own lessons; YTM is a separate page.
- Show discrete choices as visible radio option cards, rather than dropdowns.
- Order payment frequencies **Annual → Semiannual → Quarterly**, followed
  by Monthly where available. Semiannual remains the default selection.
- Display purchase-price inputs to two decimal places, with one-cent steps;
  round typed prices when committed. Preserve calculation precision elsewhere.
- Label assumptions and distinguish immediate repricing from holding-period return.
- Define a DV01 lesson yield move as a change in YTM with fixed coupons and
  principal; contrast coupon rate with YTM before deriving sensitivity.
- Explain why the Treasury bill yield formula changes at half a year:
  six months is one period in the semiannual coupon-bond benchmark.
  Lesson 6 includes the two growth formulas, a numerical comparison,
  an explanation beside the chart, and a dotted half-year marker.

## Validation and model limits

The final M1 test run on November 1, 2026 passed **313 tests**. Coverage includes pricing
identities, yield round trips, dated settlement, coupon boundaries, leap
years, bill conventions, API validation, and lesson navigation.

Independent checks use published Treasury examples for regular and reopened
bond prices, accrued interest, and short/long bill quotations. QuantLib is
not required. Details, source links, and tolerances are recorded in
[Phase 1 validation](notes/phase_1_validation.md).

Previously recorded desktop/mobile browser checks covered the six lessons, visible choices,
calculations, disabled states, resets, keyboard navigation, and layout.
The payment-option reorder was checked in rendered HTML; the latest bill
explanation, formulas, and half-year marker were also checked in the browser.

The earlier planning audit used source/tests only. The subsequent M1 implementation
was verified in a browser at desktop and 390-pixel mobile widths: calculations,
face scaling, dated mode, invalid dates, export/import, reset, keyboard radio and
chart controls, mobile navigation, and rendered formulas. No browser console errors
were observed. Mobile pages stayed within viewport width. Temporary verification
servers are stopped after checks; normal use still requires starting the server.

The November 2 lesson layout update passed all **313 tests** and browser checks
on all nine lessons at 1440, 1200, 1024, and 390-pixel widths. Checks covered
independent reading scroll, graph width, formulas, course navigation and Escape,
keyboard radio selection, recalculation/reset, section links, optional Python,
and the overview/standalone tool. No horizontal page overflow or browser console
errors were observed. The existing local server was reused.

Follow-up browser checks covered all nine lessons at 1440×900, 1200×600,
390×844, and 320×640: desktop document height matches the viewport, wheel and
section-link navigation cannot scroll the outer page, both panels still reach
their final content, and mobile retains normal page scrolling. Header links,
first/last lesson destinations, keyboard activation, and expanded Python examples
were checked. The existing desktop/mobile interaction checks and 313 tests passed.

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

Open [the local website](http://127.0.0.1:8000). Reuse an existing server if
available; otherwise start one with the command above. Stop it with Ctrl+C
when finished; restart it after Python code changes.

Alternatively, build `fixed-income-lab:local` with the root `Dockerfile` and run
it on the selected Docker engine. With the current remote `deepl` context, the
published port is on `deepl.lan`; an SSH tunnel makes it available to the client.
See [Run with Docker](README.md#run-with-docker) for complete commands, port
choices, and container lifecycle instructions.

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

## M1 delivered

- Independent `filab.risk` functions for regular-period analytical Macaulay/modified
  duration and convexity; dollar duration and positive-magnitude DV01.
- Numerical dated dirty-price sensitivity using the existing settlement convention,
  with explicit exclusion of a textbook Macaulay conversion between coupons.
- `/tools/bond-risk`, `/api/risk`, and `/api/risk-study`: two-bond comparisons,
  exact shocks, approximation errors, PV weights, bump diagnostics, and versioned
  complete-input export/import. Invalid or stale inputs cannot be exported.
- Three separate lessons with prediction prompts, worked examples, derivations,
  collapsed transfer answers, and reflection questions.
- Shared control templates and a curriculum registry; milestone-based website
  roadmap replaces the 12-week promise.
- [Validation record](notes/m1_validation.md) and an unanswered
  [learner journal](notes/m1_learning_journal.md). Software completion is recorded;
  the learner's reflection and transfer exercises remain pending.

## Next milestone

Build **M2: Returns and cash accounting**. Start with one bond and deterministic
yield paths. Record purchases, coupons, redemption, sales, cash, and costs once;
reconcile a coupon-date example independently before simulating historical returns.
Keep dirty-price accounting and clean/accrual explanations consistent. M3 data
work can follow M1 independently, but historical backtests require the M2 ledger.

## Revised roadmap and planning audit

| Milestone | Deliverable | Status |
|---|---|---|
| M0 Foundations | Existing six lessons and pricing | Software/reference checks complete; learner checkpoint unverified |
| M1 Interest-rate risk | Duration, convexity, risk explorer | Software validated; learner checkpoint pending |
| M2 Return accounting | Deterministic cash/position ledger | Next |
| M3 Historical observations | Versioned data and curve history viewer | Planned |
| M4 Discount curves | Curve valuation and validated historical adapter | Planned |
| M5 Strategy research | Two synthetic Treasury strategies, saved runs, exports | Planned; first historical research release |
| M6 Robustness | Horizon analysis, curve scenarios, key-rate risk | Planned |
| M7 Daily use | Research desk, reproducibility, backup/recovery | Planned |

The roadmap has distinct learning, educational-site, and workbench acceptance
criteria. M1 comparison-input files are implemented; saved historical studies,
feeds, return ledgers, and research modules remain future work. The 108–170 hour
budget in the plan was the provisional pre-M1 estimate, not recorded time spent.
Re-estimate remaining work after M2.

The [original plan](notes/fixed_income_lab_plan_original_2026-11-01.md) is preserved
with its detailed credit curriculum and advanced research topics. These remain
extensions. Hosting, accounts, broker execution, and real-time quotes remain deferred.

The planning audit passed the original 221 tests. M1 adds 92 cases, including
closed-form risk identities, CME price-bump arithmetic, convergence, dated
boundaries, API parity, complete configuration validation, and lesson integration.
See the M1 validation record for sources, tolerances, and remaining limitations.

The [project plan](fixed_income_lab_plan.md) contains the full curriculum;
the [README](README.md) contains setup and interface details.
