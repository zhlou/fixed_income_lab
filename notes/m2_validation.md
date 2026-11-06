# M2 return accounting validation

**Date:** November 3, 2026 (America/Chicago). **Learner checkpoint:** pending;
see [the unanswered journal](m2_learning_journal.md).

## Delivered model and accounting contract

`filab.analytics.holding_period_ledger` buys one or more fixed face-dollar
positions at a common opening date. The browser exposes one or two; the explicit
ledger API accepts up to twenty. Every position has a fixed regular coupon
schedule and a hypothetical step-YTM path starting on the purchase date. Later
points apply on their entered date and carry forward; no future value fills an
earlier date. An optional early sale is available in the Python/explicit API.
No signals, historical market observations, or strategy backtest are included.

Opening capital is dirty purchase value plus entry costs. There are no external
flows afterward. On a subsequent event date the ledger grows existing cash,
credits coupons, redeems principal, makes sales and charges exit costs, then
values surviving holdings. Opening purchases occur after that date's payments.
An existing owner selling on a coupon date receives the coupon first. Maturity
credits the last coupon and redeems principal once; remaining face becomes zero.

`mark` retains surviving bonds at the horizon. `liquidate` sells them after
payments; bonds already redeemed are not sold. Fees are one-way basis points of
face amount on purchases and sales; no fee applies to a mark or redemption.
Cash is retained at zero interest by default, or grows at an explicit annual
effective rate using `(1+r)**(actual_days/365)`. No receipt earns for time before
its receipt date. Cash continues to grow after an early sale or maturity if the
horizon is later. The model rejects borrowing needed to pay a fee.

The identities are:

- Ending wealth = remaining dirty bond value + credited cash.
- Period return = ending wealth / opening capital − 1, with no annualization.
- Profit = terminal clean recovery − purchase clean + terminal accrued recovery
  − purchase accrued + coupons + cash interest − entry/exit costs. Terminal
  recovery includes sale proceeds, redemption principal, or retained bond marks.
- Cash = opening capital + ledger cash changes; each face balance follows its
  purchase and its one sale or redemption. Valuation rows move neither.

The dated pricer remains unchanged: regular maturity-anchored coupons,
Actual/Actual coupon-period accrued interest, simple first fractional discounting,
then compound whole periods. Trade and settlement dates coincide in this model.
Stubs, holidays, ex-coupon rules, market settlement lags, taxes, defaults, short
sales, leverage, cash withdrawals, and additional bond reinvestment are excluded.
Cash and bond day counts differ intentionally. Fixed YTM is not curved-term-structure
roll-down. See [Phase 1 validation](phase_1_validation.md) for pricing benchmarks.

## Authoritative references

Pages checked November 3, 2026:

- [FINRA: Return and Rate of Return](https://syndication.finra.org/content/key-concepts-return-and-rate-return)
  supports the distinction between dollar earnings, value changes, costs, and
  percentage return. Our closed-portfolio identity is derived directly.
- [TreasuryDirect: Buying a Treasury Marketable Security](https://www.treasurydirect.gov/marketable-securities/buying-a-marketable-security/)
  and [pricing](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/)
  support accrued settlement amounts, coupon/yield premium-discount relationships,
  and principal redemption. Model-specific settlement ordering remains explicit.
- [CFA Institute: Interest Rate Risk and Return](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/interest-rate-risk-and-return)
  distinguishes horizon proceeds and reinvestment from the purchase YTM.
  Realized terminal-wealth compounding needs matching reinvestment assumptions;
  solving the promised-payment IRR itself does not require actual reinvestment.
- [OTS Examination Handbook 540, Appendix A, hosted by OCC](https://www.occ.gov/static/ots/exam-handbook/ots-exam-handbook-540aa.pdf),
  January 2010, Table 1 on page 5, supplies an independent horizon-return table.
  It is used as an arithmetic benchmark, not as current regulatory guidance.
- [SEC: Selling Before Maturity](https://www.investor.gov/introduction-investing/investing-basics/glossary/bonds-selling-maturity)
  supports the early-sale price-risk discussion.

## Independent examples and tolerances

### Two annual periods, hand calculation

Face $100, annual coupon $4, annual YTM 5%, issue/purchase November 15, 2025,
maturity/horizon November 15, 2027. Both annual intervals have exactly 365 days.
No costs. Compute these without the financial library before comparing:

| Quantity | Expected |
|---|---:|
| Purchase price, `4/1.05 + 104/1.05**2` | 98.140589569161 |
| Ending wealth at zero interest | 108.00 |
| Ending wealth at effective 5% cash, `4*1.05 + 104` | 108.20 |
| Extra cash interest | 0.20 |
| Whole-period return at zero interest | 0.1004621072088725 |
| Whole-period return at 5% cash | 0.1025 |

Price, receipts, and cash growth use $1e-12 absolute tolerance on the sparse
hand ledger; the return identity uses 1e-14 absolute. A dense daily valuation
grid must reproduce sparse results within $1e-10; partitioning cash growth can
change floating-point summation, but must not create payments or material interest.

### Published horizon-return benchmark

OTS Table 1: 20-year 9% coupon bond purchased at $109.90 per $100 face, three-year
horizon, end yields 6/8/10%, reinvestment rates 4/5/6%. Use semiannual coupons.
Solve purchase YTM from the published **rounded purchase price**, rather than
overwriting that amount with an unrounded 8% price.

| Nominal semiannual cash reinvestment | End YTM 6% | End YTM 8% | End YTM 10% |
|---|---:|---:|---:|
| 4% | 13.36% | 7.78% | 3.06% |
| 5% | 13.44% | 7.87% | 3.16% |
| 6% | 13.53% | 7.97% | 3.26% |

These printed figures are reproduced as annual compounded returns
`(ending_wealth / purchase_price)**(1/3) - 1`. This interpretation is an inference
verified by the table's arithmetic; the surrounding prose also discusses a
separate bond-equivalent conversion. The website continues to report the entire
period's return, not either annualized measure.

Convert each cash assumption to annual effective `(1+r_nominal/2)**2-1` for
our cash account. Use dates November 15, 2025–November 15, 2028, maturity
November 15, 2045. Calendar coupon periods and the leap year introduce a small
convention difference from equally spaced textbook half-years. All nine outputs
agree within **0.00005 decimal return** (0.005 percentage point), half the last
printed percentage precision. This benchmark does not claim identical cash
clocks at greater precision.

### Coupon-date and early-sale checks

For $100 face, 4% coupon, 5% nominal YTM, semiannual, issue November 15, 2025,
maturity November 15, 2028, purchase November 14, 2026, sell November 16, 2026:

- Purchase clean 98.11628118246018; accrued `2*183/184` = 1.9891304347826086;
  dirty 100.1054116172428.
- Receive $2 on November 15. Sale dirty 98.13223648263877; ending wealth
  100.13223648263877, profit 0.02682486539598, return 0.0002679661864691.
- Clean change 0.00490557642168 + accrued change −1.97808071102570 + coupon 2
  reconciles profit. Buying on November 15 instead receives no opening coupon.

For the same bond purchased November 15, 2026 and sold May 15, 2027 after a
step to 7% YTM: purchase 98.11901289599513; sale
`2/1.035 + 2/1.035**2 + 102/1.035**3` = 95.79754452862954;
ending wealth after the $2 coupon = 97.79754452862954; return
−0.0032763106545551. At fixed YTM, hold to November 15, 2028 instead: four $2
coupons + principal = $108, return 0.1007041022159343. These are hypothetical
scenarios, not forecasts or observed historical results.

Normal-scale accounting residuals use $1e-10 absolute tolerance. Price/quote
round trips allow $1e-9 where a numerical yield solve is involved. Dollar
displays round only at presentation; committed clean purchase quotes are cents
per $100 face. Quotes with more than two decimal places are rejected by the API.

## Checks performed

- Full Python 3.12.16 suite: **398 passed**, including 53 ledger cases and 32 M2
  web/API cases. One existing upstream Starlette/httpx deprecation warning.
- Independent two-period arithmetic, nine published scenarios, opening-date coupon
  exclusion, coupon-before-sale ordering, final redemption once, early-sale cash
  growth, fees once, mark/liquidation, zero/negative yields, all four frequencies,
  zero coupons, face scaling, weighted aggregate returns, cash/face conservation,
  step-path timing, invalid inputs, numerical API parity, and complete versioned
  input validation.
- JavaScript syntax and `git diff --check` passed.
- Chrome checks on all four new lessons at 1440×900, 1200×900, 1024×900,
  390×900, and 320×900 verified rendered formulas, collapsed answers/optional
  Python, expected example results, contained horizontal table scrolling, and
  no page/reading/experiment horizontal overflow. Desktop outer document height
  remained within the viewport. Screenshots at desktop/mobile widths were inspected.
- Standalone calculator checks covered pointer selection of visible option cards,
  keyboard frequency/cash selection, chart arrow keys/Escape, clean quotes rounded
  to cents, disabled controls, two-position aggregation, cash/cost changes, input
  export/import, full-precision ledger export, incompatible import preservation,
  invalid dates, disabled stale exports, reset to each lesson's original case,
  rapid input changes with delayed replies, and mobile Course navigation/Escape.
  Expected 422 responses came from deliberately invalid dates/files; no JavaScript,
  formula, or unexpected console errors occurred. New lesson requests used only
  localhost resources, with no external requests.
- Existing nine-lesson browser regression checks passed at 1440×900 and 390×900:
  formulas, answer reveals, optional code, YTM entry/reset, dated default values,
  and page/reading widths. No browser console errors were observed.

Browser scripts and screenshots were temporary verification artifacts under
`/private/tmp/filab-m2-qa/`; they are not durable repository resources. A temporary
localhost server was used because no existing listener was available, and was
stopped after verification. The remote Docker image/container was not rebuilt;
its existing M0/M1 deployment requires a rebuild/recreation to serve M2.

## Interface and reproducibility boundary

Four separate lesson pages, the overview cards/sidebar/navigation, and
`/tools/bond-return` share the calculation. `POST /api/returns` adapts one/two
positions and a fixed/one-change yield path. `POST /api/return-ledger` accepts
explicit positions, dated step paths, optional early sales, and valuation dates.
`POST /api/return-study` validates complete input snapshots under
`dated-return-ledger-v1`. Input export/import reproduces assumptions; full ledger
export includes results and hypothetical price provenance. This is not an
immutable historical research-run system. No new dependency or online data
source is required for normal operation.

## Follow-up: controls and chart usability — November 3, 2026

The initial M2 layout put the full input form and results in one scrolling
experiment. Changing a lower input could move the chart out of sight. The
revised desktop lesson gives the input column and results independent scrolling,
with no outer experiment scroll range. Grouped native disclosures summarize
current assumptions. A compact toolbar provides examples and file actions;
the input footer retains Reset and View chart. A short-window presentation
keeps the complete SVG chart and its curve legend visible. Smaller screens
switch between inputs and results without changing the scenario.

Verification used the final source on a temporary localhost server:

- **398 pytest cases passed**; JavaScript syntax and `git diff --check` passed.
  No financial implementation, source benchmark, or curriculum change was made.
- Desktop sizes: 1600×900, 1440×900, 1200×900, 1200×600, and 1600×600.
  The entire SVG fit within the results pane. Opening Cash & trading costs,
  scrolling its inputs, and changing the fee to 10 bp left the chart's vertical
  position unchanged. Independently scrolling results did not move inputs;
  View chart returned results to the plot. The outer experiment/document had
  no vertical scroll range; no horizontal page overflow occurred.
- Narrow sizes: 1024×900, 768×900, 390×844, and 320×640. Edit inputs exposed
  grouped controls; View chart restored the results and updated return in one
  click. Values and selections persisted. No horizontal page overflow occurred.
- Native disclosure keyboard activation, frequency radio arrows, cents on quote
  commit, two-position results, complete input export/import, reset, examples,
  and standalone controls passed. An invalid date in a collapsed section reopened
  that section and disabled stale exports. Expected 422 responses were handled;
  no JavaScript, formula, or unexpected console errors were observed.
- All four M2 lesson opening cases still matched their established results.
  Desktop, short-window, and mobile screenshots were inspected. Temporary
  artifacts are under `/private/tmp/filab-m2-layout/`; they are not repository
  dependencies or permanent deliverables. The verification server was stopped.

The remote Docker deployment requires a rebuild/recreation to serve these
template and asset changes. Learner reflection remains pending.

### Example buttons kept visible

The four scenario buttons are now a permanent group above the workspace, rather
than a disclosure that closes after selection. On smaller screens they share
a sticky header with the input/results switch. File actions retain their own
Save / load disclosure. Scenario selection preserves keyboard focus on desktop
and returns to results on smaller screens; the example buttons remain available.

Targeted validation: 32 M2 web/API tests passed, JavaScript syntax and diff checks
passed. Browser checks cover visibility before/after selecting every example,
independent input scrolling, the complete chart in short windows, narrow-screen
scrolling and view switching, keyboard activation, and Save / load with Escape.

## Focused lesson experiments — November 3, 2026

The lesson pages now use `return_lesson.html` and the bounded
`/api/lesson-returns/{slug}` adapter. The dedicated full calculator retains its
general controls, examples, files, and existing numerical interfaces. Both use
the same ledger and pricing conventions; browser navigation/error visibility is
shared. Each lesson displays only relevant examples and controls, plus explicit
fixed assumptions. Lesson text and experiments were revised together.

| Lesson | Financial controls | Derived view and boundary |
|---|---|---|
| 10 | Exit YTM, one-way cost, mark/liquidate | Price-only percentage uses dirty purchase price; investment return uses opening capital including entry fee. A sale's comparator is its pre-sale dirty price, not a zero remaining position. |
| 11 | Purchase/valuation near November 15, coupon rate | Keep and mark the bond, compare dirty value with total wealth, and show clean/accrual/cash rows. Zero-cost marked wealth matches the old hypothetical sale example. |
| 12 | Effective cash rate, coupon, first-coupon/maturity/post-maturity horizon | Chart the additional wealth versus zero-interest cash; the table shows both wealth totals and returns. Both cases use identical prices and positions. |
| 13 | Coupon, purchase YTM, maturity/pre-maturity/early-sale horizon; early-sale yield when applicable | Plot clean/dirty marks before redemption, or the pre-sale mark at an early exit. Record terminal cash and remaining face separately. |

All financial arithmetic remains in Python. Return comparison curves reconcile
to the existing result; cash differences compare two independently processed
ledgers. The 2026–2028 pull-to-par case includes leap day: its final pre-maturity
price is 730 actual days after purchase, and redemption is on day 731. It is
still four regular semiannual payment periods. No cash or coupon day-count
convention has changed.

**424 tests passed** under Python 3.12.16, with the same upstream Starlette/httpx
warning. The 26 new cases cover worked-case/full-API parity, rejection of
unrelated controls/scenarios, the two price/return denominators, entry/exit costs,
coupon-date eligibility, date-window bounds, independent two-period cash growth,
negative cash interest, first-coupon and post-redemption horizons, premium/discount
signs, zero remaining face at redemption, and pre-sale versus remaining values.
Established normal-scale tolerances remain $1e-10 for ledger wealth and cash
differences; independent regular price-return ratios use 1e-13 absolute.

Chrome checks passed on all four lessons at 1440×900, 1200×600, 1600×600,
390×844, and 320×640. Checks verified exact sets of enabled controls, only related
examples, formulas, complete short-window plots, independent input scrolling,
responsive switching, conditional exit yield, keyboard presets/radios, reset,
invalid dates, disabled pending/invalid transfers, and delayed-response protection.
The full-calculator link restored coupon, frequency, cash rate, and horizon
exactly, reproducing the lesson's wealth. The full tool still passed quotes to
cents, adding a position, and complete file export/import. No external requests,
JavaScript/formula errors, or unexpected console errors occurred; deliberately
invalid dates returned 422. Desktop/mobile screenshots were inspected. Temporary
artifacts are under `/private/tmp/filab-focused-returns/`, and the temporary
verification server was stopped afterward.

The calculator link uses the existing version-1 complete input snapshot in a URL
fragment, validated by `/api/return-study`. It does not import arbitrary full
calculator scenarios back into a bounded lesson. Rebuild/recreate the remote
Docker container to serve the new source. Learner checkpoints remain unfilled.

A deliberate 503 during full-tool recalculation also passed: the transfer kept
the stale-result notice and disabled input/ledger exports, without claiming
successful restoration. All focused input panels visibly label the experiment
as hypothetical.

## Lesson progression revision — November 5, 2026

The current sequence is 10 coupons/accrual and simple return; 11 fixed-YTM
pull-to-par and maturity; 12 cash reinvestment; 13 integrated holding-period
return and early sale. Lesson 10's worked example now values the bond still
held, matching its experiment. With no exit costs, this has the same wealth as
the earlier hypothetical sale. The 7% exit-yield example is taught once, in
lesson 13. Pull-to-par exposes only maturity and the day before maturity, with
discount/premium examples; its old early-sale API requests remain compatible.
Pricing, ledger arithmetic, conventions, and full-calculator inputs are unchanged.

Existing authoritative references and benchmark tolerances above continue to
apply; no new external source verification was needed for this reordering.
Independent arithmetic checks reproduced the introductory hypothetical example:
$99 remaining bond + $2 cash − $100 purchase = $1 profit, or 1%. The revised
zero-coupon transfer exercise gives $100/1.05² = $90.702947845805 at purchase,
$100/1.05 = $95.238095238095 after one year at fixed yield, a 5% one-year marked
return, and a 10.25% two-period return at redemption. Compare these derived
values with the existing regular-period price identities at $1e-10 absolute
price tolerance and 1e-13 absolute return tolerance. They are hypothetical
examples, not additional published market benchmarks.

**429 tests passed** on Python 3.12.16. Five added cases check that prerequisites
precede their lessons and that all four visible discount/premium and
maturity/pre-maturity combinations use fixed yield, zero cash interest, and the
correct held/redeemed status. Navigation checks now assert the new lesson
numbers and both previous/next destinations. Existing worked cases, full-API
parity, saved studies, and the former pull-to-par early-sale case still pass.
The existing Starlette/httpx deprecation warning remains.

Browser checks at **1440×900** and **390×844** covered all four pages, their
numbers, formulas, controls, charts, and absence of horizontal page overflow.
Keyboard coupon/premium/cash presets, horizon radio selection, coupon reset,
and mobile input/results switching worked. A premium bond remained held on
the day before maturity with its final payment still in value; redemption
instead left zero face. In lesson 13, 10 bp costs charged $0.10 each at purchase
and sale; keeping the mark removed only the sale cost. Transferring the final
lesson to the full calculator restored the −0.327631% early-sale case and the
same $97.80 ending wealth. The sidebar displayed the new order. No KaTeX errors
or browser warning/error logs were observed; desktop/mobile screenshots were
inspected. The temporary verification server was stopped after checks.

The remote Docker container requires a rebuild/recreation for this source
revision. The journal prompts were reordered but remain unanswered; these
checks establish software behavior, not learner mastery.
