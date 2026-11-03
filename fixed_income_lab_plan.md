# Fixed-Income Lab — Learning, Education, and Research Workbench

**Revised:** November 1, 2026 (America/Chicago)

**Primary daily use:** Research bond strategies and historical returns.

**Current release:** Nine lessons, regular-bond pricing, bill quotations, and M1 risk tools.

**Next release:** M2 holding-period returns and cash accounting.

## 1. Direction and assessment

Build one local application in which learning produces reusable research tools.
Each concept should become an explanation, a controlled experiment, and a validated
calculation. The eventual workbench should answer: **What did this bond strategy
earn, why, under which assumptions, and how robust is the result?**

The original plan is a strong curriculum but an oversized first product. It
places data ingestion, curve fitting, portfolio simulation, TIPS, macroeconomics,
and backtesting inside a 12-week Treasury core at 5–8 hours per week. That is only
60–96 hours for learning, implementation, educational content, and validation.
Treat that as an initial aspiration, not an evidence-based delivery schedule.
The workbench arrives too late and lacks a concrete recurring workflow, saved
experiments, a reproducibility contract, and operational acceptance criteria.

Keep the financial foundations. Bring return accounting and a limited historical
strategy comparison forward. Defer advanced fitting, macro dashboards, TIPS, and
credit until the nominal Treasury research workflow works end to end.

### Baseline assessment before M1

This assessment records the planning baseline. M1 was subsequently implemented;
see the delivery update below and `PROJECT_STATUS.md` for current status.

Audit based on pricing modules, FastAPI routes, lesson Markdown, templates,
JavaScript, tests, and validation notes on November 1, 2026. The existing suite
passed **221 tests**. This was a source and automated-test review; a fresh visual
browser review was not completed because no server answered on port 8000.
Earlier browser checks are recorded separately in `PROJECT_STATUS.md`.

| Area | Present capability and evidence | Assessment / gap |
|---|---|---|
| Education | Six lesson routes, navigation, local KaTeX, interactive SVG and tables | A substantive foundations module, not merely a scaffold |
| Pricing | `pricing/cashflows.py`, `yield_math.py`, `settlement.py`, `bills.py` | Reusable regular-bond calculations; preserve public interfaces |
| Validation | Financial identities, published Treasury examples, invalid inputs, dated boundaries, API checks | Strong foundation within the supported model |
| Learning process | Worked examples, experiments, reflection questions, optional code | No recorded learner mastery, prediction journal, or transfer-exercise workflow |
| Risk and returns | Exact instantaneous yield shocks and fixed-YTM price paths | No duration, convexity, holding-period ledger, or portfolio returns |
| Historical data and curves | Roadmap only | No ingestion, historical store, discount curves, or vintage tracking |
| Research workflow | Calculators embedded in lessons | No saved studies, strategies, run comparison, exports, or research journal |
| Architecture | Python, FastAPI/Jinja, Markdown, plain JS/SVG | Retain stack; split page-specific branches as features arrive |
| Roadmap consistency | Website still lists the original nine modules and 12 weeks | Replace week promises in the next website release; written credit expansion was never reflected there |

Dated pricing uses regular maturity-anchored schedules, Actual/Actual coupon-period
accrual, simple first-fractional-period discounting, and after-payment coupon-date
settlement. Stub coupons, holidays, ex-coupon rules, settlement lags, and
auction-specific intermediate rounding remain excluded. The dated website is
semiannual, although reusable schedules support other regular frequencies.
This is not a complete security-level Treasury settlement engine.

### M1 delivery update — November 1, 2026

M1 software is implemented: three new lessons, analytical regular-period risk,
numerical dated sensitivities, exact/approximate shock comparisons, PV weights,
bump diagnostics, and complete versioned comparison-input export/import. The
standalone tool is `/tools/bond-risk`. The website now has nine lessons and
milestone-based roadmap labels. All 313 tests pass; the validation record is
[notes/m1_validation.md](notes/m1_validation.md). Learner reflection remains pending
in [the M1 journal](notes/m1_learning_journal.md). M2–M7 remain planned.

### Three separate measures of success

**Teaching review, November 3, 2026:** All nine published lessons have been
reviewed for prerequisite order, terminology, notation, reproducible examples,
experiment guidance, and reflection. The revisions keep the existing M0/M1
sequence and calculation conventions. Definitions now precede the more advanced
formulas; foundational exercises include revealed explanations, and YTM and dated
settlement have fuller worked examples. See [the review record](notes/lesson_content_review.md).
This is an educational-content improvement, not completion of learner checkpoints
or delivery of M2.

| Goal | Evidence |
|---|---|
| Learn during the process | Predict a result, reproduce a calculation, explain a surprise, and solve a new case without copying the example |
| Build an educational site | A new learner can follow prerequisites, inspect assumptions, reproduce examples, and open the related tool |
| Build a daily research workbench | Reopen a question, refresh available data, rerun strategies, inspect returns/risk, and export a reproducible result |

Software completion, lesson publication, and learner completion remain separate.
A passing test or a page visit does not establish learning.

## 2. The first useful research product

### Recurring workflow

1. Open **Research desk**: see each source's latest observation, retrieval time,
   coverage issues, and saved studies.
2. Reopen a question: “How did regularly renewed 2-year and 10-year Treasury
   exposures compare across different investment horizons?”
3. Choose a frozen dataset, common sample, capital, two strategy templates,
   rebalance rule, cash treatment, and transaction-cost assumption.
4. Compare wealth, total return, drawdown, duration, turnover, costs, and cash
   contributions. Curve-derived prices and strategy results are labeled synthetic.
5. Inspect a difficult month down to positions, payments, trades, prices, and
   cash balances. Follow metric explanations back to lessons.
6. Save an interpretation and export configuration, metadata, results, and ledger.
   Refreshing data creates a new run; it never silently changes the old study.

Daily use means the app is useful whenever opened. It does not imply daily
publication from every source, live quotes, or executable market prices.

### First historical research release scope

- U.S. nominal Treasuries, USD, long-only, unlevered, regular synthetic schedules.
- Two fixed-rule strategies: monthly renewed 2-year and 10-year synthetic coupon
  bonds. Define initial coupon setting, dates, purchases, sales, and rebalancing.
- Equal starting capital and common sample; show duration differences because
  equal capital does not imply equal interest-rate risk.
- Coupon cash held at zero interest initially, explicitly labeled. Add a separate
  cash-return model later; never silently assume reinvestment at YTM.
- Monthly reporting/rebalancing with every intervening payment accounted for.
  No external contributions, withdrawals, taxes, leverage, or short positions.
- Configurable costs on traded notional under a documented convention, with
  gross/net results and turnover.
- Historical discount-curve valuation, distinct from the existing YTM quotation
  model. No claim to replicate a tradable index, ETF, or actual investor fills.
- Saved configurations, immutable runs, downloadable ledgers, and one independently
  reconciled study.

Actual holdings, broker imports, and a comprehensive security master are later
branches, not prerequisites for this research-first product.

## 3. Learn while building

Use **predict → derive → experiment → validate → explain → reuse** for each concept.
Coding is optional for the learner; understanding cash flows and conventions is not.

Each distinct lesson gets its own page, overview card, sidebar entry, and navigation:

1. A financial question, prerequisites, and intuition before equations.
2. Defined symbols/units, a derivation, and a reproducible worked example.
3. A prediction prompt before moving controls; tables and charts tied to cash flows.
4. A controlled experiment and a boundary case or counterexample.
5. Misconceptions, assumptions, reflection, and a transfer exercise with new inputs.
6. An optional revealed answer and a link to the reusable tool; Python stays collapsed.

Keep a lightweight learning journal, initially Markdown: question, prediction,
result, explanation, remaining uncertainty, and dated revisit. Revisit an earlier
exercise without its answer at the next milestone. Add saved learning progress
only when useful; do not build a learning-management platform first. The assistant
can give feedback but must not write a personal reflection as if the learner did it.

Use one continuing case: explain 2-year and 10-year hypothetical bond prices,
measure sensitivity, follow cash receipts, and eventually compare defined rolling
strategies over history. The education site should stand alone for another learner,
while the journal records the original learner's progress.

## 4. Milestones and dependencies

These replace the original calendar phases. Estimates are provisional focused-work
budgets including lessons and validation, not deadlines. Re-estimate after M1–M2.
The pre-M1 budget for M1–M7 was roughly **108–170 hours**, or **14–34 weeks at 5–8 hours/week**;
learning pace and data issues may extend it. Useful releases arrive along the way.

| Milestone | Dependency | Learning outcome | Reusable deliverable | Estimate |
|---|---|---|---|---|
| M0 Foundations | Existing | Cash flows, prices, yields, accrual | Six lessons and calculators | Software complete; learner checkpoint unverified |
| M1 Interest-rate risk | M0 | Sensitivity and approximation error | Delivered; learner checkpoint pending | Original estimate: 12–18 h |
| M2 Returns and cash accounting | M0; M1 for risk comparisons | Reconcile a holding-period return | Event ledger and return calculator | 12–20 h |
| M3 Historical observations | M0; independent of M2 | Understand dataset meaning | Historical curve viewer and versioned data | 16–24 h |
| M4 Discount curves | M1, M3 | Par, spot, forward, and YTM distinctions | Curve valuation and historical adapter | 16–24 h |
| M5 First strategy study | M1–M4 | Explain historical strategy returns | Two-strategy backtest, saved runs, exports | 24–40 h |
| M6 Robustness and curve risk | M5 | Test stability of a finding | Horizon analysis and key-rate scenarios | 16–24 h |
| M7 Daily-use release | M5–M6 | Reproduce and communicate research | Reliable research desk and acceptance study | 12–20 h |

Default sequence: M1 → M2 → M3 → M4 → M5 → M6 → M7. M3 can follow M1 if early
real data improves motivation. M5 is the first useful historical research release;
TIPS, credit, macro dashboards, and advanced modeling are not prerequisites.

### M1 — Duration, convexity, and exact repricing

**Lessons:** cash-flow timing/Macaulay duration; modified duration/DV01;
convexity/approximation error. Give these distinct financial concepts their own pages.

Derive analytical duration/convexity for regular periods and compare central
finite differences of the same pricer. Define DV01 sign, dollar sensitivity,
yield units, normalization, and bump size. For dated bonds, begin with numerical
derivatives of the existing dated pricer: do not apply textbook regular-period
identities unchanged to its different fractional-period convention.

**Experiment:** low/high coupon and short/long maturity; positive and negative
25, 50, 100, and 200 bp shocks. Show exact changes, first/second-order estimates,
and errors in dollars/percent. Label these immediate repricings, not returns.

**Gate:** independent zero-coupon example; analytical/numerical agreement under
matching conventions; bump convergence; face scaling; dated coupon boundaries;
export/reload comparison inputs with conventions intact.

**Learner evidence:** explain why maturity differs from duration and why large
shocks weaken a duration-only approximation.

### M2 — Holding-period returns before backtesting

**Lessons:** price change versus return; coupons/accrual; reinvestment and cash;
pull-to-par. Complete curved-term-structure roll-down in M4.

Build an event ledger for purchases, coupons, redemption, sales, cash, and
valuation. Start with one bond and deterministic yield paths, then aggregate
positions. Specify trade/settlement assumptions and same-date event ordering.
Use dirty prices for cash accounting, with clean/accrual components for explanation.
For a closed portfolio, return is ending wealth / beginning wealth − 1. Ending
wealth includes credited cash; do not add those coupons again.

**Experiment:** buy before a coupon and value after payment; hold a discount bond
to maturity; sell early after a shock; compare cash held versus explicit reinvestment.

**Gate:** cash/position conservation; fees charged once; coupon eligibility at
settlement; no duplicated payments; redemption once; explicit end-horizon liquidation;
an independently hand-calculated two-period example.

**Learner evidence:** reconcile one return and explain why YTM does not determine
a shorter-horizon realized return.

### M3 — Historical data with provenance

**Lessons:** par observations versus security quotes; missing dates; observation,
publication, and retrieval time; revisions/vintages.

Start with one official Treasury nominal par dataset and a small pinned fixture,
then expand history. Preserve raw responses, source/series, observation date,
retrieval timestamp, rate type, original and normalized units, and content hash.
Record known release timing or mark it unknown. Keep raw revisions and define
normalization/duplicate policies. Missing rates must never become zero.

**Tool:** historical curve comparison, tenor changes, 2s10s spread, coverage
and data-quality tables. This is not yet a bond return calculator.

**Gate:** idempotent imports, fixture/source agreement, identifiable missing tenors
and nonpublication days, failed-refresh recovery, and offline cached use. Define
the valid sample intersection before strategy comparisons.

**Learner evidence:** explain why a constant-maturity par yield is neither a
security price nor necessarily the YTM of a particular bond.

### M4 — Discount curves and historical valuation

**Lessons:** discount factors/spot rates; synthetic bootstrapping; forwards;
interpolation/model risk; roll-down along an unchanged curve.

Implement discount-factor cash-flow valuation and recover a known synthetic curve
from consistent instruments. Start with linear interpolation in log discount
factors. Require D(0) = 1 and positive discount factors; do not forbid increasing
discount factors when negative rates are allowed. Declare time basis, compounding,
short-end treatment, and extrapolation policy.

Evaluate the Federal Reserve's published fitted nominal curve parameters/data
for the first historical adapter. Reconstruct its documented discount curve and
verify reported yields. Custom Nelson–Siegel/Svensson fitting is not a prerequisite.
This is a fitted off-the-run curve, not actual security quotations. Keep Treasury
par observations separate: never treat par yields as spot rates or silently splice
sources.

**Data feasibility gate:** establish units, coverage, short-end behavior, gaps,
revisions, and publication delays. Validate every required cash-flow horizon,
including short coupons. Interpolation from D(0) to the first supported node is
an explicit model assumption; reject unsupported extrapolation. If the adapter
fails this gate, release synthetic scenarios and resolve the blocker before
claiming historical strategy support. Do not substitute approximate YTM returns.

**Gate:** reprice synthetic calibration instruments; match published curve outputs
to documented precision; flat-curve equivalence under matching conventions;
forward/short-end sensitivity checks. Explain why curve valuation can differ from
the existing dated YTM model when discount conventions differ.

**Learner evidence:** explain why forwards are not guaranteed forecasts and why an
aging bond can change price on an unchanged curve.

### M5 — A small historical strategy laboratory

**Lessons:** defining a strategy; rolling versus holding; wealth/drawdown;
costs; synthetic backtests and their limitations.

Connect M2's ledger to M4's historical curves for the two strategies in Section 2.
Define coupon setting, regular dates, sale of aged bonds, replacement purchases,
rebalance calendar, missing-date policy, fractional face holdings, and terminal
liquidation. Defer signal optimization and a general strategy language.

Report monthly but process every intervening payment. Label drawdown/volatility
with reporting frequency: monthly observations can miss intra-month losses.
Store positions and cash events, not only a return series.

**Outputs:** wealth/total return, annualized geometric return when meaningful,
monthly volatility/drawdown, duration/DV01 history, turnover, costs, and cash
contributions. Define metrics. Delay Sharpe ratios until a compatible cash
benchmark and excess-return convention exist.

**Gate:** independently reconcile a tiny frozen dataset; single-bond cases match
M2; no trades means no trading costs; identical strategies match; changing future
observations cannot alter earlier holdings; identical runs reproduce results.
Export configuration, normalized observations, provenance, and audit ledger.

**Learner evidence:** a research note with question, rules, result, explanation,
limitations, and one alternative explanation.

### M6 — Robustness, horizons, and nonparallel risk

**Lessons:** horizon dependence; duration-matched comparisons; twists/key-rate
duration; regime selection/overfitting; empirical versus causal claims.

Add rolling 1-, 3-, and 5-year returns where coverage permits. Explain dependence
among overlapping windows. Compare predefined periods, rebalance frequencies,
costs, and interpolation assumptions. Separate exploration from held-out evaluation,
record attempted variants, and avoid selecting only favorable endpoints.

Add exact parallel/steepening/flattening scenarios and key-rate sensitivities under
a specified bump/interpolation rule. Compare estimates with exact small-shock
repricing. Duration-matching decisions must use available information.

**Gate:** show a finding that weakens or reverses under a reasonable alternative;
show unmatched risks; reconcile portfolio/position sensitivities. Add a ladder
and bullet/barbell comparison only after calendars and initial strategies pass
validation. PCA remains optional.

**Learner evidence:** explain why the best historical result is not necessarily
the best future strategy and why equal duration is incomplete risk matching.

### M7 — A dependable research desk

Provide **Learn**, **Experiments**, and **Research desk** entry points over the
same calculations. Keep stable lesson URLs. Add saved studies, run comparison,
explicit refresh, freshness/coverage status, journal, local backup/restore, and
portable exports. Pin old runs to their inputs; create linked new runs on refresh.

**Release acceptance:** across five separate use sessions, reopen a study,
identify its vintage, reproduce it, explain one month's return, compare an
assumption change, and export without editing code. Include one offline session
and a failed-refresh recovery that preserves previous results. Target about ten
minutes for the routine saved-study workflow; measure actual runtime on the agreed
sample. Long jobs need visible state, double-submission protection, and cancellation
if measured runtime warrants it.

Verify desktop/mobile reading, keyboard controls, formulas, errors, resets,
stale-response handling, and console errors. The learner completes the research
exercises; software checks alone do not satisfy acceptance.

## 5. Research integrity requirements

Label **identities**, **hypothetical scenarios**, **historical observations**,
**model-derived estimates**, and **forecasts** separately.

- **Price provenance:** observed quote, curve-implied synthetic price, and user
  assumption remain distinct in calculations, displays, and exports.
- **Information timing:** observation date does not prove availability. Studies
  using today's revised historical curves are retrospective model studies. Do not
  claim a point-in-time implementable signal test without release/vintage evidence
  and decision/execution lags.
- **Missing observations:** no future backfill. Explicitly skip, delay a rebalance,
  or carry a stale mark with a maximum age. Compare common dates and show exclusions.
- **Accounting:** count positions, cash, coupons, redemption, fees, and reinvestment
  once. Carry/roll-down attribution requires a stated counterfactual and ordering;
  it is not a unique observed decomposition. Report attribution residuals.
- **Comparability:** same capital, calendar, sample, cash policy, and cost convention;
  report duration and curve-risk differences alongside returns.
- **Reproducibility:** save run ID, configuration/strategy version, code version or
  source hash, data hashes/vintages, conventions, timestamp, warnings, metrics,
  trades, positions, and cash events. Save a seed if randomness is later introduced.
- **Claims:** synthetic history is not actual execution, causal proof, or a return
  forecast. Bound claims to coverage and supported conventions.

## 6. Architecture and implementation discipline

Retain FastAPI/Jinja, Markdown, local KaTeX, plain JS/SVG, and Python financial
calculations. API rates are decimals; controls use percentages. Display cents,
commit purchase prices in one-cent increments, and keep intermediate precision.
Preserve option cards, semiannual defaults, units, and accessibility.

`pricing/`, `risk/`, and `web/` now exist. Add the remaining modules when needed,
not empty architecture in advance.

| Layer | Responsibility | Milestone |
|---|---|---|
| `pricing/` | Existing schedules and quotation/pricing functions | Existing |
| `risk/` | Yield duration/convexity implemented; curve sensitivity later | M1 delivered; M6 planned |
| `analytics/` | Event ledger, returns, metrics | M2 |
| `data/` | Source adapters, normalization, snapshot metadata | M3 |
| `curves/` | Discount factors, interpolation, bootstrap, historical adapter | M4 |
| `research/` | Fixed strategies, run orchestration, reproducibility | M5 |
| `web/` | Lessons, tools, presentation, request validation | Existing; extend |

Use typed instrument, position, observation, curve, and run records as needed.
HTTP request models should not define the financial domain. Keep valuation,
payment, observation, and information-availability dates distinct.

Start saved comparisons with versioned JSON export/import. For data/research,
use raw files plus immutable normalized snapshots and, if needed, a small SQLite
catalog for studies/runs. Add pandas for time-series work when required.
DuckDB/Parquet are responses to measured volume, not initial prerequisites.

Extract lesson-specific templates/JS from current conditional pages as modules
arrive. Use one small curriculum registry for prerequisites, availability, and
roadmap labels. Preserve existing interfaces. No framework rewrite, hosting,
accounts, cloud sync, or browser-executed financial Python is required.

## 7. Definition of done

Every milestone delivers:

- **Calculation:** explicit conventions, independent example, identities,
  meaningful boundaries/invalid-input checks, API parity where exposed.
- **Education:** lessons, worked example, experiment, misconceptions,
  reflection, and transfer exercise.
- **Tool:** reusable workflow connected to the lesson and saved inputs where useful.
- **Validation:** sources, expected outputs, tolerances, and actual checks recorded.
  Preserve `notes/phase_1_validation.md`; add milestone-specific validation notes.
- **Usability:** relevant desktop/mobile/keyboard/error checks for UI changes;
  offline checks for data-dependent workflows.
- **Documentation:** status and README match delivered interfaces; software and
  learner completion tracked separately.

Allocate learning sessions roughly one quarter to explanation/derivation, one
quarter to predictions/experiments, one third to building/validation, and the
remainder to reflection. Adjust to the learner; do not let UI polishing replace
the financial question.

## 8. Extensions after the research core

| Track | Prerequisites | Result and boundary |
|---|---|---|
| TIPS and inflation | M2–M5; reliable indexation data | Validate lag, principal floor, cash flows, and returns before historical strategy claims |
| Monetary policy/term premium | M3, M6 | Context dashboard with model labels, release timing, revisions, and causal limits |
| ETF mechanics | M2, M5 | Distributions, fees, turnover, NAV/price; validate total-return treatment before comparisons |
| Credit fundamentals/ratings | M0–M1 | Ratings, capital structure, covenants, recovery; ratings are not guarantees or mechanical default probabilities |
| Noncallable credit pricing | M4, credit fundamentals | Benchmark/spread and Z-spread models with separately validated corporate conventions |
| Default/recovery | Credit pricing | Survival/hazard models with explicit probability measure and recovery timing; avoid double-counting credit compensation |
| Credit risk/returns | M2, M6, credit pricing/default | Rate/spread risk and default/recovery ledger; preserve defaulted securities in empirical studies |
| Advanced research | Specific question and baseline | Custom curve fitting, PCA, stochastic rates, optimization, callable bonds/OAS |

The original detailed credit and advanced curriculum remains in
[the archived plan](notes/fixed_income_lab_plan_original_2026-11-01.md). These are
intended learning paths, not prerequisites for the first useful workbench. Estimate
and validate each separately before implementation.

Defer broker execution, real-time quotes, comprehensive settlement conventions,
tax accounting, derivatives, machine-learning trading, and general-purpose
optimization until a concrete research need justifies the scope.

## 9. Immediate implementation backlog

1. Complete the M1 learner journal: predict, inspect payment weights, reconcile a
   shock row, and export/reload a comparison. Software does not answer these prompts.
2. Build M2's deterministic ledger and reconcile a coupon-date example before
   historical return simulation.
3. Add the M2 lessons and reusable return calculator with clear cash treatment,
   transaction costs, settlement assumptions, and same-date event ordering.
4. Start M3 with an official source, pinned fixture, and provenance panel; assess
   M4's data feasibility before promising a historical backtest date.
5. Re-estimate remaining work after M2. Keep saved comparison inputs distinct
   from future immutable historical research runs.

M1 implementation does not add market data, holding-period returns, historical
strategy results, or saved research studies.

## 10. Sources and migration

Source pages checked November 1, 2026:

- [Treasury interest-rate statistics](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics):
  par curves derived from indicative quotations and separate bill-rate products.
- [Treasury curve methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology):
  official source construction and methodological changes.
- [Federal Reserve nominal yield curve](https://www.federalreserve.gov/data/nominal-yield-curve.htm):
  fitted off-the-run curves/parameters; excludes bills and selected recent issues.
  Describes typically weekly posting and possible delays/revisions. A daily
  historical series is not a same-day feed or a point-in-time vintage archive.
- [TreasuryDirect pricing](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/):
  quotation context; retain published benchmarks in `notes/phase_1_validation.md`.

Use Tuckman and Serrat for pricing/curves and Fabozzi for instruments/portfolios,
consulting relevant chapters as questions arise. The archived plan retains the
original reading list. Sources support financial/data assumptions; estimates and
product priorities are project judgments.

| Original phase | Revised home |
|---|---|
| 1 Foundations | M0, retained |
| 2 Risk | M1 |
| 3 Historical data | M3 |
| 4 Curves | M4; custom fitting deferred |
| 5 Returns | M2, brought forward |
| 6 Curve risk | M6; PCA optional |
| 7–8 TIPS and macro | Extensions |
| 9 Strategy lab | M5 first release, M6 robustness, M7 daily use |
| 10–13 Credit | Preserved extension track |

Core completion means the site teaches the reasoning, the learner can explain a
new case, and the workbench reproduces and audits a useful historical strategy
comparison. These are three distinct achievements.
