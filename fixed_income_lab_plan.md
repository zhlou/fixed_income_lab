# Fixed-Income Lab
## A Learning-Driven Quantitative Research Project

**Duration:** 12 weeks for the Treasury core, followed by a planned 5–6 week credit and corporate bond extension and open-ended research\
**Effort:** Approximately 5–8 hours per week  
**Primary language:** Python  
**Primary objective:** Learn fixed-income theory through mathematical derivation, interactive experiments, and historical data analysis, with optional Python implementation examples.

---

## 1. Project Vision

Build a personal interactive learning website and quantitative research environment for understanding the U.S. Treasury market, interest-rate dynamics, inflation, and bond investment strategies, then extending those foundations to credit risk and corporate bond valuation.

The project will gradually evolve from a simple bond-pricing library into a research laboratory capable of answering questions such as:

- Why do bond prices fall when yields rise?
- How are bond yield, coupon rate, current yield, and total return related?
- Why do long-duration bonds respond differently to changes in interest rates?
- What determines the shape of the Treasury yield curve?
- What are par yields, spot rates, and forward rates, and how do they relate?
- How do duration, convexity, and yield-curve shape affect portfolio returns?
- How much of bond return comes from coupon income, price movements, and roll-down?
- What is the difference between nominal yields, real yields, and inflation expectations?
- How does the Federal Reserve influence different parts of the yield curve?
- Can historical market behavior help evaluate different bond investment strategies?
- How do credit ratings, default risk, recovery, and liquidity affect corporate bonds?
- How do we price a corporate bond and separate interest-rate risk from credit spread risk?

### Guiding Principles

1. **Learn the theory before using a library.** Implement important calculations independently before relying on QuantLib or other financial packages.
2. **Prefer experiments to passive reading.** Each mathematical concept should lead to a numerical experiment or visualization.
3. **Use real data early.** Working with actual historical yields, conventions, and market observations is part of the educational value.
4. **Build incrementally.** Every phase should produce a useful standalone component. Avoid building a large application framework in advance.
5. **Separate financial theory from empirical assumptions.** Bond-pricing identities are different from statistical models predicting future interest rates.
6. **Validate before expanding.** Each phase ends with numerical tests, independent comparisons, or empirical checks.

---

## 2. Technical Architecture

Use a local, lab-first website backed by a small Python package. Each lesson
has its own page with interactive charts, controls, numerical tables, and
explanations. Python implementation examples are available in expandable
sections. FastAPI serves Jinja templates and numerical JSON endpoints; plain
JavaScript renders responsive SVG charts. Markdown holds lesson content,
and locally bundled KaTeX renders formulas without a CDN.

Keep financial calculations in Python, using the existing pricing functions
as the source of truth. API inputs use decimal rates; controls display
percentages. Label rate conventions, settlement assumptions, and the
difference between immediate repricing and holding-period returns.
Present discrete control choices as visible radio option cards rather than
dropdowns, with clear selected and disabled states and keyboard navigation.

```text
fixed-income-lab/
├── README.md
├── pyproject.toml
├── src/
│   └── filab/
│       ├── data/
│       │   ├── treasury.py
│       │   └── fred.py
│       ├── instruments/
│       │   ├── bond.py
│       │   └── tips.py
│       ├── pricing/
│       │   ├── cashflows.py
│       │   ├── yield_math.py
│       │   └── discounting.py
│       ├── web/
│       │   ├── app.py            # Lesson routes and calculation API
│       │   ├── content/          # Markdown lessons
│       │   ├── templates/        # Shared Jinja layout
│       │   └── static/           # CSS, JS, SVG and local formula assets
│       ├── curves/
│       │   ├── bootstrap.py
│       │   └── fitting.py
│       ├── risk/
│       │   ├── duration.py
│       │   └── scenarios.py
│       └── analytics/
│           ├── returns.py
│           └── backtest.py
├── notebooks/                  # Preserved optional reference experiments
├── tests/
├── data/
└── notes/
```

### Recommended tools

- **NumPy and SciPy:** Numerical calculations and optimization.
- **pandas:** Time-series analysis and data transformations.
- **DuckDB:** Historical market-data storage and analytical queries.
- **FastAPI, Uvicorn, and Jinja:** Local Python-backed lesson website.
- **Markdown and bundled KaTeX:** Lesson content and mathematical notation.
- **Plain JavaScript and SVG:** Responsive, accessible interactive charts and controls.
- **Matplotlib / Jupyter:** Optional research and preserved reference experiments.
- **pytest:** Validation.
- **QuantLib:** Independent pricing reference, introduced after implementing basic pricing manually.

The local educational website is the primary learning interface from the
initial migration onward. Production hosting, accounts, cloud synchronization,
and arbitrary browser-executed Python are deferred. Resolve resources relative
to the package so moving the checkout does not require application edits.

### Website migration status

- The website has six lessons, each with its own page:
  1. **Bond Basics:** understand the promised payments.
  2. **Present Value and Bond Pricing:** discount payments, understand rate
     conventions, and calculate price.
  3. **Bond Pricing Lab:** experiment with coupon, maturity, and yield.
  4. **Yield to Maturity:** solve yield from price and compare yield measures.
  5. **Settlement and Accrued Interest:** dated cash flows, clean/dirty prices,
     dated YTM solving, and pull-to-par experiments.
  6. **Treasury Bill Yields:** discount quotations, investment yields, and
     short- versus long-bill conventions.
- Python implementation examples live in an optional, collapsed **Under
  the hood** section in Lesson 2. There is no separate implementation lesson.
  The former implementation URL redirects to this section; navigation and
  lesson numbering use the six-lesson sequence.
- The first three existing Markdown notes and Notebook 01 supply the
  initial content. Preserve these originals as reference artifacts.
- Website Markdown becomes the content source for website lessons.
- The separate Yield to Maturity lesson solves YTM from price, compares coupon rate,
  current yield, and YTM, and verifies the result in a discounted payment
  table. The reusable `yield_to_maturity` function supports regular coupon
  schedules, including zero coupons and negative implied yields. Dated
  settlement and Treasury bill quotations have separate Python functions
  and separate lesson pages.
- Lesson 4 has its own overview card, sidebar entry, and previous/next
  navigation. Its price input defaults to $98.12, rounds to two decimal
  places, and uses one-cent increments; calculations retain full precision.
  The dated price solver follows the same input-rounding convention.
- The home page and sidebar expose available lessons; the remaining
  12-week curriculum is a roadmap, with future modules labeled coming later.
- Website setup: `python -m pip install -e '.[web,dev]'`, then
  `python -m uvicorn filab.web.app:app --host 127.0.0.1 --port 8000`.
- For Python development, optionally add `--reload --reload-dir src/filab
  --reload-delay 1`. Keep reload restricted to source files so the polling
  watcher does not scan the virtual environment. Normal lesson use needs no
  reload watcher; stop the local server with Ctrl+C when finished.
- No JupyterLab, Node.js, database, account, or hosting is needed to run
  the website. Future data ingestion stays in the Python research layer.

### Learning notes

Maintain one short Markdown note for each major financial concept, containing:

1. Definition and intuition.
2. Mathematical derivation.
3. A numerical example.
4. Optional code implementing the concept, presented under the hood.
5. Common misconceptions and limitations.

These notes inform separate website lessons. Pair each lesson with an interactive experiment and optional Python implementation; preserve original notes as reference artifacts.

---

# Part I — Bond Mathematics

## Phase 1: Bonds, Cash Flows, and Yield
**Weeks 1–2**

### Learning objectives
Understand how Treasury securities work and how bond prices relate to interest rates.

### Concepts to study
- Treasury bills, notes, and bonds.
- Face value, coupon rate, maturity, and redemption.
- Zero-coupon versus coupon-bearing securities.
- Present value and the time value of money.
- Simple versus compound interest.
- Yield to maturity (YTM).
- Current yield versus YTM.
- Bond-equivalent yield and discount yield.
- Clean price versus dirty price.
- Accrued interest.
- Coupon payment frequencies and day-count conventions.

### Mathematics
Start with pricing a fixed-rate bond:

$$
P = \sum_{t=1}^{n} \frac{C_t}{(1+y/m)^{mt}}
$$

For regularly spaced coupon payments, where:
- $P$ is the present value.
- $C_t$ is the cash flow at time $t$, including principal at maturity.
- $y$ is the annual nominal yield.
- $m$ is the coupon frequency.

Understand the assumptions behind this formula and how actual dates affect calculations.

### Implementation
Build:
- A fixed-coupon bond cash-flow generator.
- A zero-coupon bond pricer.
- A coupon-bond pricer given YTM.
- A YTM solver given price.
- An accrued-interest calculator.
- Clean-price and dirty-price conversion.

Implement the root-finding logic with SciPy, but write the pricing function yourself.

### Experiments
1. Compare 2-year, 10-year, and 30-year bond prices at different yields.
2. Compare a premium bond, discount bond, and par bond.
3. Change the coupon rate while holding maturity and YTM constant.
4. Compare zero-coupon and coupon-bearing bonds with identical maturity.
5. Investigate how a bond approaches par as maturity approaches.

### Validation
- Verify that a bond issued at par has coupon rate approximately equal to YTM under matching conventions.
- Confirm price decreases as YTM increases for an ordinary fixed-rate bond with positive cash flows.
- Compare several prices and accrued-interest calculations against QuantLib or a published example.

### Deliverable
**Website Module 01: Bond Pricing Fundamentals** — Six lessons: Bond Basics; Present Value and Bond Pricing; Bond Pricing Lab; Yield to Maturity; Settlement and Accrued Interest; Treasury Bill Yields. Each has a distinct financial learning objective; implementation examples are optional under-the-hood material in Lesson 2.

### Implementation status
Phase 1 software and published-reference validation are complete for the
regular-bond model. The six lessons expose the planned experiments;
`notes/phase_1_validation.md` records sources, numerical tolerances, and
repeatable checks. No assertion is made that the learner has completed the
reflection checkpoint.

Dated schedules use Actual/Actual coupon-period accrual, unadjusted dates,
and Treasury-style simple discounting for the first fractional period.
Settlement on a coupon date is after payment. Irregular first coupons,
holiday adjustments, ex-coupon rules, and market settlement lags remain
outside this educational model. Bill investment yields use an explicit
365/366-day basis and the longer-bill quadratic when applicable.

The next implementation milestone is **Phase 2: Duration, Convexity, and
Interest-Rate Risk**. Keep the existing pricing functions as the reference
for exact repricing.

### Learning checkpoint
Be able to explain why two bonds with the same maturity and YTM can have different interest-rate sensitivity.

---

## Phase 2: Duration, Convexity, and Interest-Rate Risk
**Weeks 3–4**

### Learning objectives
Understand why some bonds are much more sensitive to rate changes than others.

### Concepts to study
- Macaulay duration.
- Modified duration.
- Dollar duration.
- DV01 / PV01.
- Convexity.
- First- and second-order price approximations.
- Duration differences between zero-coupon and coupon bonds.
- Duration changes as time passes.
- Reinvestment risk versus price risk.
- Holding-period return versus yield to maturity.

### Mathematics
Understand the first-order relationship:

$$
\frac{\Delta P}{P}\approx-D_{\mathrm{mod}}\Delta y
$$

Then extend it:

$$
\frac{\Delta P}{P}\approx-D_{\mathrm{mod}}\Delta y+\frac{1}{2}C(\Delta y)^2
$$

where $C$ is a convexity measure consistent with the yield convention.

Derive duration from the derivative of bond price with respect to yield.

### Implementation
- Analytical modified-duration calculator.
- Numerical duration using finite differences.
- Convexity calculator.
- DV01 calculator.
- First- and second-order bond price approximations.

### Experiments
1. Compare approximate and exact price changes for yield shocks of 25, 50, 100, and 200 basis points.
2. Compare the duration of low-coupon and high-coupon bonds.
3. Measure how duration evolves as a bond approaches maturity.
4. Investigate whether a 10-year zero-coupon bond is riskier than a 10-year coupon bond.
5. Measure how convexity affects the error in duration-only approximations.

### Validation
- Compare analytical and numerical duration.
- Verify finite-difference convergence as perturbation decreases, before floating-point error dominates.
- Compare exact repricing against duration and convexity approximations.

### Deliverable
**Website Module 02: Bond Risk Explorer** — Interactive charts of price, duration, and convexity under yield scenarios.

### Learning checkpoint
Explain why a bond fund with duration of seven years does not necessarily lose exactly 7% when its quoted yield rises by one percentage point.

---

# Part II — Understanding the Yield Curve

## Phase 3: Historical Treasury Yield Data
**Week 5**

### Learning objectives
Understand what Treasury yield datasets actually represent.

### Concepts to study
- Yield curve and term structure.
- Constant-maturity Treasury yields.
- Par yield curve.
- Zero-coupon / spot curve.
- Forward curve.
- On-the-run versus off-the-run securities.
- Differences between observable prices and estimated curve values.
- Bid/ask prices and market quotation conventions.
- Missing trading days and historical-data revisions.

### Data acquisition
- [U.S. Treasury Interest Rate Statistics](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics)
- [Treasury historical CSV archives](https://home.treasury.gov/interest-rates-data-csv-archive/)
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)

Acquire daily nominal Treasury par yields at available constant maturities, Treasury bill rates, historical effective federal funds rates, and optionally Treasury real yields.

### Implementation
Develop an ingestion pipeline that:
1. Downloads source data.
2. Stores original files without modification.
3. Normalizes observation dates, maturities, and units.
4. Records source metadata and acquisition timestamps.
5. Preserves the original rate type.
6. Loads normalized observations into DuckDB.
7. Validates missing values and duplicate records.

Do not label a par-yield observation as a zero rate.

### Experiments
- Visualize the yield curve on selected historical dates.
- Plot the historical 2-year/10-year spread.
- Compare periods of normal, flat, and inverted yield curves.
- Build a heatmap of yields by observation date and maturity.

### Deliverable
**Website Module 03: Treasury Yield Curve History** — Historical curve pages plus a repeatable ingestion pipeline.

### Learning checkpoint
Explain why the published 10-year constant-maturity Treasury yield is not necessarily the exact YTM of a specific bond you can buy.

---

## Phase 4: Spot Rates, Forward Rates, and Curve Construction
**Weeks 6–7**

### Learning objectives
Understand how a whole yield curve determines the present value of future cash flows.

### Concepts to study
- Discount factors.
- Spot rates.
- Forward rates.
- Par rates.
- Bootstrapping.
- Yield-curve interpolation.
- Continuously compounded rates.
- Nelson–Siegel and Nelson–Siegel–Svensson models.
- Arbitrage-free discounting intuition.
- Model fitting error and numerical stability.

### Mathematics

$$
P=\sum_i CF_iD(t_i)
$$

where $D(t)$ is a discount factor. For continuously compounded zero rates:

$$
D(t)=e^{-z(t)t}
$$

The continuously compounded forward rate between $t_1$ and $t_2$ is:

$$
f(t_1,t_2)=\frac{\log D(t_1)-\log D(t_2)}{t_2-t_1}
$$

### Implementation
- Discount-factor representation.
- Price calculator using a discount curve.
- Simple bootstrapping from consistent synthetic market instruments.
- Interpolation over discount or log-discount factors.
- Nelson–Siegel fitting and optionally Nelson–Siegel–Svensson.

Use published Treasury and Federal Reserve curves as benchmarks; recognize that a par-curve transformation may not reproduce the Federal Reserve's independently fitted zero curve.

### Experiments
1. Construct a zero curve from synthetic coupon-bond prices.
2. Convert it into forward rates.
3. Compare interpolation methods.
4. Examine fitted yields and residual errors.
5. Investigate instability with sparse observations.
6. Compare Nelson–Siegel and spline curve shapes.

### Validation
- Reprice synthetic calibration instruments.
- Compare interpolated yields with observations.
- Inspect plausibility of discount factors and implied forwards.
- Evaluate out-of-sample fitting error where possible.

### Deliverable
**Website Module 04: Term Structure Construction** — Interactive par, spot, and forward curve construction.

### Learning checkpoint
Explain why a rising yield curve does not necessarily mean future realized short-term interest rates will rise.

---

# Part III — Portfolio Returns and Risk

## Phase 5: Bond Holding-Period Returns
**Week 8**

### Learning objectives
Understand the sources of bond investment returns.

### Concepts to study
- Coupon income.
- Price appreciation and depreciation.
- Accrued interest.
- Total return and holding-period return.
- Carry, roll-down, and pull-to-par.
- Reinvestment assumptions.
- Mark-to-market accounting.
- YTM versus realized return.

### Implementation
Create a bond portfolio simulator with purchase date, purchase price, cash-flow schedule, periodic valuation, coupons received, reinvestment assumptions, and sale/maturity events.

Distinguish coupon cash flows, clean-price movement, and changes in accrued interest. Introduce reinvestment income separately when modeled.

### Experiments
1. Buy a 10-year Treasury and hold it for one year under an unchanged yield curve.
2. Repeat with a parallel 100-basis-point rate increase.
3. Repeat with steepening and flattening curves.
4. Compare a short Treasury ladder with one intermediate-duration bond.
5. Compare hold-to-maturity outcomes with selling after one year.

### Deliverable
**Website Module 05: Where Bond Returns Come From** — Interactive return decomposition.

### Learning checkpoint
Explain why a 10-year Treasury yielding 5% does not guarantee a 5% return over the next year.

---

## Phase 6: Nonparallel Yield-Curve Risk
**Week 9**

### Learning objectives
Move beyond the assumption that all yields change together.

### Concepts to study
- Parallel shifts.
- Steepening and flattening.
- Level, slope, and curvature.
- Key-rate duration.
- PCA and historical yield-change covariance.
- Portfolio sensitivities by maturity.
- Duration-neutral strategies.

### Implementation
- Yield-curve shock generator.
- Exact cash-flow repricing using shocked discount curves.
- Key-rate duration estimates.
- PCA of historical yield changes.
- Portfolio sensitivity visualization.

### Experiments
1. Parallel shift versus bear steepening.
2. Same total duration, different key-rate exposures.
3. Historical PCA factor shocks to hypothetical portfolios.
4. Identify dominant maturity exposures.

### Deliverable
**Website Module 06: Yield Curve Risk Laboratory** — Interactive nonparallel curve shocks and exposure comparisons.

### Learning checkpoint
Explain how two portfolios with identical duration can respond differently to changes in the yield curve.

---

# Part IV — Inflation and Monetary Economics

## Phase 7: TIPS, Inflation, and Real Yields
**Week 10**

### Learning objectives
Understand inflation-linked bonds and real versus nominal rates.

### Concepts to study
- Nominal versus real interest rates.
- Fisher equation and CPI inflation.
- TIPS principal indexation, indexation lag, coupons, maturity principal protection.
- Real yield and real duration.
- Breakeven inflation.
- Inflation risk premium and TIPS liquidity effects.

### Mathematics

$$
y_{\mathrm{nominal}}\approx y_{\mathrm{real}}+\pi
$$

and the exact compound-rate relationship:

$$
1+y_{\mathrm{nominal}}=(1+y_{\mathrm{real}})(1+\pi)
$$

Learn why the observed nominal-minus-TIPS yield spread is not a pure forecast of inflation.

### Data acquisition
Treasury real curves, CPI index levels, nominal Treasury yields, and Federal Reserve inflation-compensation estimates.

### Implementation
- TIPS principal indexation simulator.
- TIPS cash-flow generator.
- Approximate real-duration analysis.
- Nominal/real yields and breakeven visualization.

### Experiments
1. Nominal Treasuries versus TIPS under hypothetical inflation paths.
2. Rising real yields and TIPS price declines.
3. Historical nominal versus real yields in inflationary periods.
4. Why TIPS can lose market value during high inflation.

### Deliverable
**Website Module 07: Inflation and TIPS** — Interactive inflation, indexation, and real-yield experiments.

### Learning checkpoint
Explain why higher inflation does not automatically result in positive short-term TIPS fund returns.

---

## Phase 8: Monetary Policy, Expectations, and Term Premium
**Week 11**

### Learning objectives
Understand the economic forces behind yield-curve movements.

### Concepts to study
- Federal funds rate and policy transmission.
- Overnight versus long-term yields.
- Expected future short-term rates and expectations hypothesis.
- Term premium, inflation expectations, and risk compensation.
- Tightening, easing, and yield-curve inversion.
- Fiscal supply and Treasury market dynamics.
- Correlation versus causal evidence.

### Data acquisition
Fed funds, Treasury yields, inflation indicators, New York Fed ACM term-premium estimates, selected Federal Reserve curve models.

### Implementation
Historical macro dashboard with policy rates, yield curves, term-premium estimates, nominal and real yields, and inflation indicators.

### Experiments
1. Yield behavior in historical tightening cycles.
2. Periods when long yields rose despite falling short rates.
3. Changes in 10-year yields versus modeled term premiums.
4. Yield-curve inversion and later economic weakness, with attention to definitions and sample size.

### Deliverable
**Website Module 08: What Moves Treasury Yields?** — Historical macroeconomic dashboards and explanations.

### Learning checkpoint
Explain how long-term Treasury yields can rise while the Fed cuts its policy rate.

---

# Part V — Integrated Research

## Phase 9: Historical Bond Strategy Laboratory
**Week 12**

### Objective
Integrate all preceding components.

### Strategies
- Short Treasury ladder.
- Intermediate Treasury exposure.
- Long-duration Treasury exposure.
- Bullet versus barbell portfolios.
- Constant-maturity strategies.
- TIPS versus nominal Treasury allocation.

### Implementation
Build a small, transparent synthetic Treasury backtester with historical valuation dates, cash flows, curve lookup, transactions, cash balances, coupon income, market valuation, total returns, configurable rebalancing, and transaction costs.

Avoid look-ahead bias. Distinguish simulated prices from actual security-level observations.

### Research experiments

**A. Duration versus investment horizon:** When did longer duration help or hurt over 1-, 3-, and 5-year horizons?

**B. Curve steepening:** Compare maturity structures under bear and bull steepening.

**C. Inflation sensitivity:** Compare nominal and TIPS exposure under real-rate and inflation shocks.

**D. Risk-adjusted returns:** Compare total return, volatility, drawdown, and duration exposure.

### Final deliverable
**Website Module 09: Fixed-Income Research Workbench** — Integrated historical data, pricing, risk, scenarios, returns, inflation, and strategy comparisons.

---

# Part VI — Credit Risk and Corporate Bonds
**Planned extension: approximately 5–6 weeks after the Treasury core**

This is a planned learning track, not an implemented website feature. Basic
credit analysis and noncallable corporate bond valuation are intermediate
material; structural credit models and embedded options remain advanced.
The 12-week Treasury core and its completion criteria remain intact.

### Prerequisites and sequencing

Start after Phase 4 for ratings and basic spread pricing, using Phase 2 risk
measures. Complete Phases 5–6 before credit return and portfolio experiments.
The default schedule places the full track after Phase 9. It adds four modules
with separate lesson pages, overview cards, sidebar entries, and previous/next
navigation. Each lesson includes intuition, defined symbols, a derivation or
conceptual mechanism, a reproducible example, an interactive experiment,
misconceptions, and reflection questions; Python examples remain optional.

## Phase 10: Credit Fundamentals and Credit Ratings
**Approximately 1 week**

### Learning objectives
Understand what a bondholder is promised, what can prevent payment, and what
a credit rating does and does not tell an investor.

### Concepts to study
- Business risk, leverage, interest coverage, cash flow, and refinancing risk.
- Issuer versus issue ratings; agency-specific rating scales and outlooks.
- Investment grade versus high yield, including agency-specific boundaries.
- Upgrades, downgrades, watch lists, fallen angels, and rising stars.
- Seniority, secured versus unsecured debt, guarantees, and covenants.
- Default, recovery, and loss given default.
- Ratings as credit opinions rather than guarantees, prices, or precise
  default probabilities; limitations and delays in rating changes.

### Implementation and experiments
- Build a rating-scale comparison with source dates and agency definitions.
- Use a hypothetical capital structure to show payment priority and recovery
  under explicitly stated asset-value and waterfall assumptions.
- Compare hypothetical issuers with different leverage and interest coverage;
  do not assign an agency rating mechanically from a single financial ratio.
- Follow a synthetic downgrade scenario and distinguish a credit event from
  the separate market response in yields and prices.

### Validation and deliverable
Check rating definitions against the agencies' own documentation and verify
that the simplified waterfall conserves available assets and respects claims.
**Website Module 10: Credit Fundamentals and Ratings.**

### Learning checkpoint
Explain why two bonds from the same issuer can have different ratings and
why a highly rated bond can still lose market value.

## Phase 11: Pricing Noncallable Corporate Bonds
**Approximately 1–2 weeks**

### Learning objectives
Price a plain fixed-rate, noncallable corporate bond using explicit benchmark
and spread conventions, and understand what the quoted spread measures.

### Concepts to study
- Promised cash flows versus payments actually received.
- Treasury benchmark spreads, maturity matching, and benchmark choice.
- Yield spread versus Z-spread; why a single-benchmark yield difference is
  generally different from a spread applied across the spot curve.
- Discounting promised cash flows with a benchmark curve plus a specified
  spread convention; solving a Z-spread from a dirty price.
- Credit compensation, liquidity, and other spread components; the full
  observed spread is not an expected default loss.
- Clean/dirty prices, accrued interest, day counts, and settlement conventions.

### Implementation
- Reuse Phase 4 discount curves and the existing cash-flow pricing layer.
- Add constant-spread pricing and a price-to-Z-spread solver, initially using
  a continuously compounded spread applied to benchmark discount factors.
- State benchmark curve, rate units, coupon frequency, face-value units,
  settlement, and accrual conventions alongside every example.
- Begin with synthetic regular schedules. Do not silently apply the current
  Treasury accrual and fractional-period conventions to market corporate
  bonds; add and validate any required corporate conventions explicitly.

### Experiments
1. Price the same promised payments at different credit spreads.
2. Compare Treasury-rate increases with spread widening, both separately
   and together, holding all other scenario inputs fixed.
3. Compare a benchmark yield spread with a Z-spread on a sloped curve.
4. Solve a spread from price and reproduce the original dirty price.

### Validation and deliverable
Test zero-spread equivalence to benchmark-curve pricing, price/spread round
trips, and falling prices as spreads increase for positive promised payments.
Validate an independent published noncallable example with matching
conventions, recording source and numerical tolerance before claiming
market-convention support.
**Website Module 11: Corporate Bond Pricing Lab.**

### Learning checkpoint
Explain why a corporate bond's YTM is a promised-cash-flow yield rather than
a guaranteed realized return, and why its spread is not just default risk.

## Phase 12: Default, Survival, and Recovery
**Approximately 1 week**

### Learning objectives
Understand how default changes payments and how a simplified credit model
connects survival probabilities, recovery assumptions, and price.

### Concepts to study
- Conditional default probabilities, survival probabilities, and hazard rates.
- Historical (real-world) versus pricing-implied (risk-neutral) probabilities.
- Recovery of par versus other recovery conventions and payment timing.
- Expected loss versus compensation for bearing credit risk.
- Limits of inferring default probabilities from a spread or rating.

### Implementation and experiments
- Implement a simplified constant-hazard model with risk-neutral survival,
  a benchmark discount curve, and recovery of par at explicitly specified
  default payment times on a discrete grid.
- Calculate survival-weighted promised payments and recovery payments
  separately; do not also apply a full credit spread to these expected
  payments and count default compensation twice.
- Vary hazard and recovery separately; compare zero-default and zero-recovery
  boundaries and inspect sensitivity to the recovery payment grid.
- Contrast the model price with Phase 11 spread pricing and explain why a
  fitted hazard is model-dependent rather than an observed forecast.

### Validation and deliverable
Check survival/default probability consistency, convergence as the grid is
refined, zero-hazard equivalence to benchmark pricing, and independent
numerical examples with documented recovery assumptions and tolerances.
**Website Module 12: Default and Recovery Explorer.**

### Learning checkpoint
Explain why a historical default rate cannot simply replace a risk-neutral
hazard rate in a market-pricing model.

## Phase 13: Credit Spread Risk and Corporate Bond Returns
**Approximately 1–2 weeks**

### Learning objectives
Separate interest-rate exposure, spread exposure, default losses, and income
when evaluating corporate bond investments.

### Concepts to study
- Spread duration, spread DV01, and spread convexity under stated conventions.
- Benchmark-rate shocks versus spread shocks and their joint effect.
- Rating migration, default events, liquidity, and issuer concentration.
- Investment-grade versus high-yield behavior without treating a rating group
  as a homogeneous investment or a spread as a return forecast.
- Coupon income, reinvestment, price movement, and recovery in total returns.

### Implementation and experiments
- Add finite-difference spread sensitivities and exact joint repricing.
- Extend the holding-period simulator with synthetic spread paths, rating
  transitions, and explicit default/recovery events. Stop contractual coupons
  and principal payments after default and avoid double-counting recovery.
- Compare equal-duration Treasury and corporate positions under isolated
  rate shocks, spread widening, and combined scenarios.
- Compare holding to maturity with selling after a downgrade; holding to
  maturity does not remove default risk.
- Use labeled synthetic scenarios first. Historical extensions must preserve
  point-in-time ratings, defaulted and delisted securities, acquisition
  metadata, and missing observations; avoid survivorship and look-ahead bias.

### Validation and deliverable
Compare sensitivity estimates with exact repricing, reconcile cash balances
and total returns, and check no-default and default-event boundary cases.
Any empirical rating transition or default study must state its source,
sample period, cohort definition, and treatment of withdrawn ratings.
**Website Module 13: Credit Risk and Return Laboratory.**

### Learning checkpoint
Explain how falling Treasury yields can coincide with a corporate bond loss,
and distinguish an immediate price shock from a holding-period return.

### Credit-track completion criteria

Be able to interpret ratings and capital-structure priority; price a regular
noncallable corporate bond under explicit curve/spread conventions; explain
a survival/recovery model and its probability measure; calculate spread
sensitivity; and reconcile a credit holding-period return. Record independent
financial benchmarks in a dedicated credit validation note when implemented.
Software completion and learner reflection checkpoints are separate.

---

# Part VII — Advanced Research Directions

## A. Stochastic Interest-Rate Models
**Difficulty: Advanced**

Learn Vasicek, Cox–Ingersoll–Ross, mean reversion, short-rate dynamics, Monte Carlo, Hull–White, and risk-neutral pricing fundamentals.

Experiments: simulate yield paths; vary parameters; compare historical distributions; contrast real-world and risk-neutral probabilities.

## B. Dynamic Term Structure Models
**Difficulty: Advanced**

Learn dynamic Nelson–Siegel, state-space models, Kalman filtering, yield-factor forecasting, affine term structure models, and term-premium estimation.

Experiments: estimate latent factors, test against forecasting baselines, and decompose expected rates and term premiums.

## C. Bond ETF Mechanics
**Difficulty: Intermediate–Advanced**

Learn constant-duration portfolios, index construction, rebalancing, holdings turnover, distribution yield versus SEC yield, fees, ETF NAV versus market prices, and tracking error.

Compare representative short-, intermediate-, and long-Treasury ETFs and TIPS funds. Understand why holding a fund differs from holding a bond to maturity.

## D. Portfolio Optimization
**Difficulty: Advanced**

Learn duration targeting, key-rate constraints, liability matching, immunization, limitations of mean-variance optimization, robust optimization, and scenario-based portfolios.

Research question: How to construct a portfolio if short rates may fall but long rates may stay elevated?

## E. Advanced Credit Models and Callable Corporate Bonds
**Difficulty: Advanced; optional after the credit track**

Extend Phase 12 to structural models and richer reduced-form models, including
calibration limitations and historical versus risk-neutral dynamics. Study
call provisions, yield to call and yield to worst, interest-rate trees,
effective duration, and option-adjusted spreads (OAS). Explain the issuer's
exercise incentive and why a callable bond cannot be valued reliably by
ignoring the embedded option. Compare Z-spread with model-dependent OAS and
validate callable prices against independent references before adding them
to the corporate bond lab. CDS and other credit derivatives remain outside
the planned introductory track.

---

# Learning Resources

## Books

1. **Bruce Tuckman and Angel Serrat — *Fixed Income Securities: Tools for Today's Markets*.** Primary text for pricing, duration, yield curves, forwards, and term-structure models.
2. **Frank J. Fabozzi — *Bond Markets, Analysis, and Strategies*.** Practical reference for instruments, conventions, portfolios, and risk.
3. **John C. Hull — *Options, Futures, and Other Derivatives*.** Use selectively for advanced interest-rate derivatives and stochastic modeling.
4. **Darrell Duffie — *Dynamic Asset Pricing Theory*.** Optional advanced reference, unnecessary for the core project.

## Online references and datasets

- [U.S. Treasury Interest Rate Statistics](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics)
- [Treasury CSV Archives](https://home.treasury.gov/interest-rates-data-csv-archive/)
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)
- [Federal Reserve Yield Curve Models](https://www.federalreserve.gov/data/yield-curve-models.htm)
- [New York Fed Treasury Term Premia](https://www.newyorkfed.org/research/data_indicators/term-premia-tabs)
- [QuantLib Python documentation](https://quantlib-python-docs.readthedocs.io/)

Use books as references during each phase, rather than reading them cover to cover first.

---

# Learning Method

For each major concept:

1. **Study:** Open the lesson page, read the explanation, and derive key mathematical relationships.
2. **Inspect or implement (optional):** Open the lesson’s Under the hood section to inspect the Python implementation or extend it yourself. Coding is supplementary, not a prerequisite for the financial lesson.
3. **Experiment:** Vary browser controls and inspect Python-calculated charts and tables.
4. **Validate:** Compare with independent calculations, known examples, or established libraries.
5. **Explain:** Answer the lesson reflection questions and write a short Markdown note in your own words.
6. **Extend:** Challenge an assumption and design an experiment.

### Suggested weekly allocation

| Activity | Share |
|---|---:|
| Reading and mathematical derivation | 30% |
| Interactive lesson experiments | 35% |
| Validation and historical data analysis | 25% |
| Documentation and reflection | 10% |

These shares are guidelines, not strict quotas.

---

# Scope Management

## Core MVP includes

- [x] Local Python-backed lesson website with separate lesson URLs
- [x] Interactive controls, charts, numerical tables, and optional Python examples

- [x] Cash-flow-based bond pricing
- [x] YTM calculation
- [x] Dated settlement, accrued interest, and clean/dirty price conversion
- [x] Treasury bill discount and coupon-equivalent yield conventions
- [x] Phase 1 independent reference validation
- [ ] Duration and convexity
- [ ] Historical Treasury ingestion
- [ ] Discount factors and yield curves
- [ ] Basic bootstrapping and curve fitting
- [ ] Holding-period returns
- [ ] Nonparallel rate shocks
- [ ] TIPS and real-yield analysis
- [ ] Integrated historical research website module

## Planned credit extension (after the Treasury core)

- [ ] Credit fundamentals, ratings, seniority, and covenants
- [ ] Regular noncallable corporate bond curve/spread pricing and Z-spread solving
- [ ] Default, survival, and recovery modeling
- [ ] Spread sensitivities, rating migration, and credit holding-period returns
- [ ] Independent credit pricing validation and interactive lessons

## Explicitly defer

- [ ] Production hosting and deployment
- [ ] User accounts and cloud synchronization
- [ ] Broker account integration
- [ ] Real-time trading data
- [ ] Live individual corporate bond quotes and comprehensive security-specific conventions
- [ ] Callable corporate bond pricing and OAS (optional advanced research)
- [ ] Derivatives pricing
- [ ] Comprehensive ETF holdings replication
- [ ] Forecasting actual bond-market returns
- [ ] Machine-learning trading strategies

---

# Project Completion Criteria

The core project is successful when you can:

1. Price a Treasury security from cash flows and explain conventions and assumptions.
2. Derive and compute duration and convexity and test approximation errors.
3. Explain and construct par, spot, and forward rate representations.
4. Reprice hypothetical portfolios under yield-curve scenarios.
5. Calculate holding-period returns and identify their sources.
6. Explain nominal yields, real yields, breakeven inflation, and term premiums.
7. Acquire, normalize, and analyze historical Treasury data.
8. Create reproducible interactive website experiments on portfolio behavior under rate environments.
9. Distinguish mathematical identities, assumptions, empirical observations, and forecasts.
10. Navigate the lesson website, reproduce the numerical examples, and explain the behavior of its interactive experiments.

**Success is measured by what you understand and validate, not by how much code you write.**
