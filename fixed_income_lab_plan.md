# Fixed-Income Lab — Learning, Education, and Research Workbench

**Revised:** November 8, 2026 (America/Chicago)

**Primary daily use:** Research bond strategies and historical returns.

**Current release:** Seven core lessons plus two M4 curve lessons, a standalone Treasury Bill Calculator, regular-bond pricing, M1 risk tools, M2 return accounting, M3 Treasury observations, and the Discount Curve Explorer.

**Next research dependency:** Validate subyear discounting before M5 coupon-bond strategies. M4 synthetic calculations and historical curve exploration are delivered.

## 1. Direction and assessment

Build one application for first-time visitors and returning researchers, with lessons and standalone tools. A public URL serves the same application to everyone. Additional Treasury downloads and saved datasets belong to each browser, with stateless Python validation and calculations. The same application can run locally.
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
in [the M1 journal](notes/m1_learning_journal.md). This records M1's release;
see the M2 update below for the current implementation.

### M2 delivery update — November 3, 2026

M2 software adds a deterministic dirty-price cash/position ledger, fixed or
step-YTM scenarios, explicit cash growth and trading costs, mark/liquidation,
early sales in the domain/API, and aggregation of positions. Four distinct
lessons and `/tools/bond-return` connect prices and payments to wealth. Complete
scenario-input export/import and full ledger export support reproduction.
Cash defaults to zero interest; optional annual effective cash growth uses
Actual/365 Fixed, separately from the existing dated bond convention.

An independent two-period hand ledger and nine published OTS/OCC horizon-return
scenarios validate the accounting. The full suite now has 424 passing cases. See
[M2 validation](notes/m2_validation.md); learner evidence remains pending in
[the M2 journal](notes/m2_learning_journal.md). M3–M7 are still planned. M2 adds
neither market data nor historical strategies; curved-term-structure roll-down
remains in M4.

### M3 delivery update — November 7, 2026

M3 adds four lessons and `/tools/treasury-history`, using an exact pinned February
2025 official Treasury response with 19 rows. The two-year/ten-year spread example
reproduces 21 → 26 bp. Explicit year-range refreshes support 1990 through the current
year, with raw bytes, UTC acquisition times, rate types/units, content hashes,
immutable normalized snapshots, and atomic publication after range validation.
Missing dates and tenors remain absent; open comparisons stay on their snapshot.
The installed package works offline with the bundled example. All 480 tests pass.
See [M3 validation](notes/m3_validation.md); [learner evidence](notes/m3_learning_journal.md)
remains pending.

The Fed source review identifies short-end support as an unresolved M4 gate.
Re-estimate M4 at 20–32 focused hours (including 4–8 for that initial gate), keep
M5 at 24–40 conditional hours, and defer delivery dates until curve validation.
M4–M7 now total 72–116 provisional hours. These are planning judgments, not a
record of learning time or a successful historical-adapter implementation.

### M3 teaching refinement — November 7, 2026

The baseline release was committed as `01ac172`. The current sequence has three
M3 lessons (sixteen overall): lesson 14 now incorporates missing observations,
followed by timing and vintages. History charts default to log maturity spacing
with a linear alternative. All 479 tests pass after consolidation. This changes
the teaching interface and sequence, with financial and source conventions intact.

### M4 delivery update — November 8, 2026

Two appended lessons teach payment discounting and aging on an unchanged curve.
The Discount Curve Explorer provides bootstrapping, payment PVs, forwards, aging,
a pinned October 29–30 Fed comparison, and browser-owned full CSV import. The
six exact source-check rows retain the full acquisition hash and metadata.

The full official acquisition was audited across 16,309 model-bearing dates and
749 missing-data rows. Sixteen dates fail parameter-to-published-yield checks at
rounding precision. Published observations remain visible, with valuation blocked
on those dates. Historical discounting conservatively supports one year through
each row's published maximum. All coupon payments are checked; new and aged
semiannual coupon notes require unsupported subyear factors. M5 therefore retains
an open historical-coupon valuation dependency. Synthetic scenarios and supported
zero-coupon principal valuations are available. See [M4 validation](notes/m4_validation.md).

The original 20–32-hour M4 allowance is superseded by the 24–40-hour implementation
planning allowance, including full-file browser import. These estimates are not
logged work time. The unresolved source/short-end investigation needs its own
estimate once an alternative convention or source is selected. M5's 24–40 hours
remain conditional; no historical strategy delivery date follows from this release.

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

The core reading order, revised November 8, 2026, is payments/price/YTM → Treasury curve → duration/DV01 → convexity/error → settlement/coupon ownership → hold to maturity/reinvestment → sell early. Treasury bill quotes have a standalone calculator and concise reference. Page count follows the questions worth teaching.

Open with a reproducible financial result, explain its intuition, and derive the relationship with symbols and units introduced as needed. Reuse the $100-face, 4% semiannual note. The annual-coupon reinvestment example isolates two exact 365-day periods. End each lesson with one changed-input question and a collapsed explanation. Python remains optional.

Teach each idea in one primary home and refer back briefly. Remove repeated glossary entries, prediction banners, goals, misconceptions, reflection lists, and tool instructions. Keep core derivations inline. Place longer calculations, conventions, diagnostic checks, provenance, and file operations at the point where a tool user needs them. Match written inputs, charts, tables, and Reset. Use explicit experiment assignments in the registry, independently of delivery milestones.

The editorial budget is roughly 5,000 visible article words across the core, counting math/table text and excluding closed answers, calculations, and Python. Review experiment instructions separately. Card duration estimates require a measured walkthrough before publication. Record reductions in the lesson review, alongside numerical and browser checks.

Keep personal predictions and reflections in the existing journals. An assistant can give feedback while the learner supplies their own answers. Original notes, notebooks, archived plans, and earlier validation evidence retain their historical role.

## 4. Milestones and dependencies

These replace the original calendar phases. Estimates are provisional focused-work
budgets including lessons and validation, not deadlines. Re-estimate after M1–M2.
The pre-M1 budget for M1–M7 was roughly **108–170 hours**, or **14–34 weeks at 5–8 hours/week**;
learning pace and data issues may extend it. Useful releases arrive along the way.

| Milestone | Dependency | Learning outcome | Reusable deliverable | Estimate |
|---|---|---|---|---|
| M0 Foundations | Existing | Cash flows, prices, yields, accrual | Seven-question core and calculators across M0–M3 | Software complete; learner checkpoint unverified |
| M1 Interest-rate risk | M0 | Sensitivity and approximation error | Delivered; learner checkpoint pending | Original estimate: 12–18 h |
| M2 Returns and cash accounting | M0; M1 for risk comparisons | Reconcile a holding-period return | Delivered; learner checkpoint pending | Original estimate: 12–20 h |
| M3 Historical observations | M0; independent of M2 | Understand dataset meaning | Delivered; learner checkpoint pending | Original estimate: 16–24 h |
| M4 Discount curves | M1, M3 | Par, spot, forward, and YTM distinctions | Synthetic valuation and Fed explorer delivered; historical coupon coverage gate open | 24–40 h planning allowance including browser import |
| M5 First strategy study | M1–M4 | Explain historical strategy returns | Two-strategy backtest, saved runs, exports | 24–40 h |
| M6 Robustness and curve risk | M5 | Test stability of a finding | Horizon analysis and key-rate scenarios | 16–24 h |
| M7 Daily-use release | M5–M6 | Reproduce and communicate research | Reliable research desk and acceptance study | 12–20 h |

Default sequence: M1 → M2 → M3 → M4 → M5 → M6 → M7. M3 can follow M1 if early
real data improves motivation. M5 is the first useful historical research release;
TIPS, credit, macro dashboards, and advanced modeling are not prerequisites.

### M1 — Duration, convexity, and exact repricing

**Lessons:** Which bond loses more when yields rise? → When does duration give a poor estimate? Combine payment weights, Macaulay duration, modified duration, and DV01 in the first question. Use the same ten-year bond to judge convexity against exact repricing in the second. Dated risk and bump diagnostics belong to the Risk Explorer.

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

**Lessons, revised November 8, 2026:** hold to maturity/reinvestment → sell early. Settlement/coupon ownership is taught once in lesson 5. Lesson 6 follows the discount bond to redemption and then changes cash growth in the annual-coupon example. Lesson 7 combines sale price, coupon, and fees. Pull-to-par and reinvestment are selectable experiments on one page. The sale experiment changes exit yield and cost, with marking and complete ledgers available in the full calculator.

Keep `/tools/bond-return` as the complete workflow and transfer valid lesson scenarios into it. Existing return API profiles and saved input formats support earlier callers. Lesson routes may be consolidated. Show fixed assumptions and keep financial calculations in Python. Complete curved-term-structure roll-down in M4.

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

**Lesson:** How do you read a Treasury yield curve? Show two curves, the 2s10s spread, and its change. A source note explains observation dates, unknown exact publication times, and why a saved comparison pins a dataset. Axis choices, missing observations, the February series introduction, hypothetical revisions, refreshes, and exports belong to the History Viewer. Revisit information timing when M5 defines a trading decision.

The default pinned example is November 5/6, 2026, using November 1–7 coverage
(five published dates). Retain February 2025 as the historical series-introduction
example in the standalone viewer. A partial month must not mark future dates as known
nonpublication days. Lesson inputs and prose must agree with the named sample.

The standalone viewer additionally bundles October 2026 plus November through
November 7 (26 published rows). Client calendar navigation downloads Treasury months directly in the browser; cached complete months are reused, and the current month is
checked at most hourly. Preserve period-level source evidence when merging
months within a year. Update calendar availability on acquisition, but require
Compare to replace the displayed financial result. Lessons start from pinned
examples and allow month exploration with a visible notice when controls differ
from the written exercise. Reset restores the original November sample; the
hypothetical revision follows the selected date and source yield. Failed
or interrupted requests retain good snapshots, offer retry, and never manufacture
coverage. Future months are not requested. Explicit annual refresh remains the
way to check complete historical years for revisions.

Use logarithmic maturity spacing by default in the shared historical-curve chart,
with an explicit Linear choice and a linear yield axis. Label the spacing and
month/year ticks; switching axes must preserve observations and gaps. Deeper
missing-data policy choices belong in the strategy experiment in M5.

Start with one official Treasury nominal par dataset and a small pinned fixture,
then expand history. Preserve raw responses, source/series, observation date,
retrieval timestamp, rate type, original and normalized units, and content hash.
Record known release timing or mark it unknown. Keep raw revisions and define
normalization/duplicate policies. Missing rates must never become zero.

**Tool:** historical curve comparison, tenor changes, 2s10s spread, coverage
and data-quality tables. Snapshot-aware date calendars distinguish published rows,
missing rows within coverage, and dates outside cached coverage before comparison.
All valid dates remain selectable; calendar markers do not imply complete tenor
coverage. This is not yet a bond return calculator.

**Gate:** idempotent imports, fixture/source agreement, identifiable missing tenors
and nonpublication days, failed-refresh recovery, and offline cached use. Define
the valid sample intersection before strategy comparisons.

**Learner evidence:** explain why a constant-maturity par yield is neither a
security price nor necessarily the YTM of a particular bond.

### M4 — Discount curves and historical valuation

**Two lessons:** How do you price payments at different maturities? → Why can a bond change price on an unchanged curve? Derive discount factors from a small synthetic example, recover the next factor from a coupon bond, and reprice it. Then age one bond, derive a forward from adjacent discount factors, and distinguish that implied rate from a forecast. Put interpolation, source conventions, and short-end coverage in the curve tool and validation notes. Historical valuation depends on the feasibility gate below.

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

**One end-to-end study:** compare monthly renewed two-year and ten-year synthetic Treasury exposures. Follow one rebalance through sale, replacement, coupons, and costs, then interpret wealth and drawdown. Introduce availability, vintage, common dates, and synthetic prices at the decision each affects. Link source evidence and operating instructions from the relevant controls.

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

**Two questions:** Does the result survive a different holding horizon or sample? → Can duration-matched portfolios respond differently to a curve twist? Change one assumption at a time and inspect exact results. Teach overlapping windows, selection bias, and key-rate exposure through these experiments.

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
same calculations. Teach reopening, reproducing, and exporting a study through a guided Research Desk workflow. Add saved studies, run comparison,
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

`pricing/`, `risk/`, `analytics/`, `data/`, and `web/` now exist. Add the remaining modules when needed,
not empty architecture in advance.

| Layer | Responsibility | Milestone |
|---|---|---|
| `pricing/` | Existing schedules and quotation/pricing functions | Existing |
| `risk/` | Yield duration/convexity implemented; curve sensitivity later | M1 delivered; M6 planned |
| `analytics/` | Event ledger and holding-period returns; strategy metrics later | M2 delivered; M5 metrics planned |
| `data/` | Source adapters, normalization, snapshot metadata | M3 |
| `curves/` | Discount factors, interpolation, bootstrap, historical adapter | M4 |
| `research/` | Fixed strategies, run orchestration, reproducibility | M5 |
| `web/` | Lessons, tools, presentation, request validation | Existing; extend |

Use typed instrument, position, observation, curve, and run records as needed.
HTTP request models should not define the financial domain. Keep valuation,
payment, observation, and information-availability dates distinct.

Use versioned JSON export/import for saved comparisons. The website keeps Treasury raw responses and immutable normalized snapshots in browser IndexedDB, with stateless Python normalization and calculations. Existing on-disk observations can be exported read-only for browser import. Choose storage for future research studies when that workflow is implemented. Add pandas for time-series work when required.
DuckDB/Parquet are responses to measured volume, not initial prerequisites.

Extract lesson-specific templates/JS from current conditional pages as modules
arrive. Use one small curriculum registry for prerequisites, availability, and
roadmap labels. Preserve existing interfaces. Retain the framework and Python calculations. Prepare a single Docker service for HTTPS hosting, with browser-owned Treasury history. Accounts and cloud sync remain later work.

## 7. Definition of done

Every milestone delivers:

- **Calculation:** explicit conventions, independent example, identities,
  meaningful boundaries/invalid-input checks, API parity where exposed.
- **Education:** a concrete financial question, one primary explanation with its core derivation, a reproducible example, a focused experiment, and one changed-input question. Add pages only for distinct calculations or interpretations. Measure visible copy and check for repetition.
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

Before adding a course page, specify a financial question and an example whose answer changes a valuation, comparison, or interpretation. Introduce broader terminology as needed. The archived roadmap retains the expanded topic inventory.

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

The curriculum tightening and two M4 questions are delivered in the source application. Resolve the documented historical short-end coverage dependency before M5 coupon-bond strategies. Use the revised editorial rules for every future lesson. The learner completes the journal work independently.

1. Complete the M1 learner journal: predict, inspect payment weights, reconcile a
   shock row, and export/reload a comparison. Software does not answer these prompts.
2. Complete the M2 learner journal: independently reconcile the coupon-date and
   two-period examples, explain an early-sale return, and export/reload inputs.
3. Complete the M3 learner journal; begin M4 with pinned Fed data, documented
   units, published-output reproduction, and short-end support checks.
4. Keep saved comparison inputs distinct
   from future immutable historical research runs.

M2 supplies holding-period accounting; M3 supplies versioned par observations.
Synthetic discount-curve valuation and Fed history exploration are delivered.
Historical coupon-bond strategies and saved research studies retain future work.

**Post-M2 estimate review:** The original remaining M3–M7 component budgets sum
to **84–132 focused hours**. M2 has resolved the core event-ordering and cash
accounting design, but there is no measured source-ingestion or historical-curve
adapter work yet to justify narrowing those budgets. Retain them provisionally,
then re-estimate M4/M5 after M3's pinned official-data feasibility check. These
are planning allowances, not recorded time spent or delivery promises.

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
