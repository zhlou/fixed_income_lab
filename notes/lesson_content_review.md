# Lesson content review — November 3, 2026

## Scope and teaching criteria

Reviewed all nine live lessons in `src/filab/web/content/`, the optional
`pricing.md` Python supplement, curriculum/navigation, relevant experiment
controls, and their Python calculations. Also read the three original teaching
notes and the Markdown cells of Notebook 01. The website Markdown remains the
canonical teaching material. Original notes and notebook are preserved as
historical learning artifacts: their week labels, implementation sequence, and
statements that dated pricing/bills are future work describe their original stage,
not the current website. Current availability is recorded in `PROJECT_STATUS.md`.

The review checked whether each lesson introduces its question and terminology
before equations, defines symbols and units, connects calculations to payments,
explains assumptions and boundary cases, guides a reproducible experiment, and
asks the learner to explain the result. This is an editorial and numerical review,
not evidence from a learner usability study or completion of personal reflection.

## Findings and changes

| Lesson | Clarity gap | Revision |
|---|---|---|
| 1. Bond basics | Settlement and nominal amounts appeared before explanation; experiment lacked a reading guide | Define terms, derive coupon division, add schedule predictions and revealed checkpoint explanations |
| 2. Present value | Nominal/effective rate definitions and summation notation were implicit; the rate section followed the closing checkpoint | Define conventions and symbols, move rate/reinvestment discussion before exercises, add experiment steps and common mistakes, retain full-precision calculations with cents in the payment table |
| 3. Pricing lab | Assumed readers understood the change to $100 face, the graph's calculation, and basis points | Explain units and axes, show the pricing sum and a numerical shock calculation, distinguish rounding from arithmetic discrepancies, add a transfer exercise |
| 4. YTM | Jumped from rate definitions to a root equation and software method | Rebuild around fixed receipts, three rate questions, trial yields, defined notation, and a one-payment algebra exercise; distinguish calculating YTM from realizing compound returns |
| 5. Settlement | Clean/dirty terms and fractional-period indexing needed more explanation; no full dated worked valuation | Define price components and day counts, explain why indexing starts at zero, calculate all five default payments, add quote-conversion practice and a face-scaling exercise |
| 6. Bills | Annualization and symbols needed explicit definitions; old phase wording and wrong appendix section | Define holding-period return and annualization, derive price from the quoted discount, define the year basis before use, qualify the chart-bend claim for a positive quote, add a transfer exercise and M1 link |
| 7. Macaulay duration | Weighted averages were assumed; “earlier cash has more present value” lacked a yield qualification | Start with a simple weighted-average example, define growth factor and timing symbols, calculate the final payment's weight/contribution, explain zero/negative-yield cases and which shared experiment panels to read |
| 8. Modified duration / DV01 | Calculus, tangent, decimal shock units, and numerical diagnostics were introduced too abruptly | Explain slope/derivative and the Macaulay conversion, distinguish sensitivity from waiting time, work through decimal-to-percent arithmetic, explain finite differences and cancellation |
| 9. Convexity | Second derivative, Taylor correction, weights, and error units needed bridges | Explain slope changes and the half factor, define weights and bump size, reconcile the +200 bp correction and signed error, distinguish model repricing from a market forecast |

All lessons now have an explicit goal. All nine provide a collapsed answer or
transfer explanation using the existing accessible answer component. Python
remains optional. No pricing, API, template, JavaScript, or CSS behavior was changed.
The only test-file edit corrects a reference in comments/docstrings.

## Reference checks

Sources revisited November 3, 2026:

- [TreasuryDirect pricing](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/): price/yield context and bill discount pricing.
- [Treasury notes](https://www.treasurydirect.gov/marketable-securities/treasury-notes/) and [Treasury bonds](https://www.treasurydirect.gov/marketable-securities/treasury-bonds/): stated issuance terms and semiannual payment frequency.
- [Treasury Appendix B](https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf): regular dated conventions and bill formulas. The linked PDF places bills in section **VI**, with short/long investment-yield examples in VI.D.1/2. Corrected the earlier V references in the lesson, validation table, and test comments.
- [CFA Institute duration overview](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/yield-based-bond-duration-measures-and-properties): distinction between payment timing, own-yield sensitivity, and dollar exposure. Only the publicly available overview was reviewed.
- [CME DV01 note](https://www.cmegroup.com/trading/interest-rates/files/Calculating_the_Dollar_Value_of_a_Basis_Point.pdf): price-bump and modified-duration approaches; retain the convention limits in `m1_validation.md`.

These support the conventions and interpretation. New worked arithmetic uses
explicit cash-flow sums and algebra, rather than treating a published overview
as a numerical benchmark. Existing published benchmark tests remain unchanged.

## Validation actually performed

- Full existing suite: **313 passed** on November 3, 2026.
- Independent finite cash-flow sums reproduced the zero/coupon prices, trial-YTM
  prices and solved-yield round trips, dated five-payment example, and bill
  conversion exercises. Numerical parity tolerance: absolute $1e-10 for prices
  and 1e-10 for decimal rates/normalized measures, well below displayed precision.
  Lesson price strings were checked to cents, YTM/bill yields to four decimals
  in percent, and duration/convexity figures and shock percentages to six decimals.
- Recomputed the Macaulay final-payment weight as 0.9417845027398023 and its
  time contribution as 1.8835690054796046 years. The other three contributions
  total 0.0577363817066439 years.
- Recomputed every row of the ten-year convexity example. At +200 bp, exact
  change is −14.667276584962263%, second-order change is −14.566228616545693%,
  and their signed difference is **+0.101048 percentage point** when rounded
  to six decimals. Full precision is retained before rounding.
- Browser verification of all nine lessons at **1440×900 and 390×900**: loaded
  numerical results, rendered formulas without KaTeX errors, no page or reading
  article width overflow, initially collapsed answers, keyboard Enter activation
  of all answer reveals, and optional Python/implementation expansion.
- Exercised the YTM $108 zero-yield input and reset at both widths, and confirmed
  the default dated dirty price is $98.88. Captured and visually inspected desktop
  and mobile views of the new YTM/settlement explanations and convexity text.
  Long new worked equations use multiple lines for narrow reading panels.
- All nine rendered lesson routes and their local lesson links resolve.
- No browser console errors. Reused the existing port-8000 server; no temporary
  server remained running. Checked whitespace with `git diff --check`.

## Preserved limits and next learning step

The regular-period and dated conventions are unchanged. Dated valuation uses
Actual/Actual coupon-period accrual, simple first-fractional-period discounting,
regular maturity-anchored coupons, and after-payment coupon-date settlement.
Stub coupons, holidays, ex-coupon rules, settlement lags, and auction-specific
intermediate rounding remain excluded. Price shocks remain immediate repricings,
not holding-period returns. M2 return accounting is still future work.

Learner reflection and transfer answers remain to be completed by the learner.
A useful next check is to attempt each transfer exercise without revealing its
answer, then explain any mismatch using cash flows, units, and the stated rate
convention.


# Curriculum tightening — November 8, 2026

## Result and crosswalk

Reviewed all sixteen live articles, the optional Python supplement, registry/navigation, experiment templates/JavaScript, API profiles, and the M4–M7 roadmap. The new reading order has seven core questions and a Treasury Bill Calculator. Core derivations remain inline. Longer dated pricing calculations are expandable, with diagnostics and data operations in tools.

| Previous lesson | Current home |
|---|---|
| 1 Basics, 2 Present value, 4 YTM | 1 Payments, price & yield |
| 3 Pricing lab, 7 Macaulay, 8 Modified duration/DV01 | 3 Duration & dollar risk, with additional comparisons in Risk Explorer |
| 5 Settlement, 10 Coupons/accrual | 5 Settlement & coupon ownership |
| 6 Treasury bill yields | Treasury Bill Calculator and its worked reference |
| 9 Convexity | 4 Convexity & error |
| 11 Pull-to-par, 12 Reinvestment | 6 Hold to maturity, with separate Approach to par / Coupon reinvestment examples |
| 13 Holding-period return | 7 Sell before maturity |
| 14 Par yields, 15 Timing, 16 Vintages | 2 Read a Treasury curve, with operational/source exercises in History Viewer |

Retired canonical lesson Markdown was removed. The existing numerical APIs and complete-input study formats continue to support earlier callers. Current internal links point directly to the new reading order. The optional implementation redirect remains. Journals retain their prompts and personal-entry space, with updated lesson/tool references. The original plan, notes, notebooks, and earlier validation records retain their historical evidence.

## Measured copy

Counted the whitespace-separated text from rendered `article.prose` elements, including mathematical notation and table text, excluding all `details` content. This matches the baseline method. Supplementary Python uses a different container and is excluded. These counts measure copy rather than reading or learning time.

| Current lesson | Visible words |
|---|---:|
| Payments, price & yield | 500 |
| Read a Treasury curve | 358 |
| Duration & dollar risk | 440 |
| Convexity & error | 406 |
| Settlement & coupon ownership | 322 |
| Hold to maturity | 491 |
| Sell before maturity | 403 |
| **Total** | **2,920** |

The original total was 17,468, giving an 83.3% reduction. The three old history lessons contained 2,497 visible words. The new history article contains 358. Time estimates totaling 415 minutes were removed pending a measured walkthrough.

Experiment copy was reviewed separately. Focused pricing has one input direction and the relevant price or yield control. Risk lessons expose the shock and, for duration, position size. The curve lesson shows its result before date controls and keeps source evidence collapsed. Maturity has two selectable bounded views. Sale exposes exit yield and fees. Complete ledgers, dated risk, bump diagnostics, saved datasets, and source exercises are accessible in the tools.

## Validation actually performed

- Full Python suite passed **516 tests**. Consolidated registry and route tests replace checks requiring retired page counts, routes, and headings. Financial and existing API regression tests remain.
- JavaScript date/month helpers passed **7 tests**.
- Explicit finite cash-flow sums reproduced two-/ten-year prices and first/second sensitivities, clean/dirty settlement, bill price/investment yield, price-to-YTM repricing, maturity wealth at 0%/3%/5% cash, and early-sale return. Absolute tolerance was **1e-10**, substantially below display precision. At 10 bp entry/exit costs the early-sale return is −0.5309240563%, shown as −0.5309%.
- Browser checks of all seven lessons at 1440×900, 390×900, and 320×900 confirmed live results, local KaTeX rendering, collapsed article answers/calculations, unique IDs, and no page-width overflow. Screenshots of every lesson at desktop and phone widths were captured under `/private/tmp`; selected pricing, curve, and maturity views were visually inspected and layout corrections verified.
- Additional checks at 1200×600 and 390×844 covered keyboard answer reveals and lesson picker/Escape, standalone tool layouts, radio-arrow input direction, input errors, cent rounding, delayed-response invalidation, coupon-date settlement, expandable formulas, and mobile maturity inputs/results.
- Verified price/yield switching and reset, 3% coupon cash growth producing $108.12, scenario handoff to the full Return Calculator, History Viewer reference/revision/reset, and the bill's $97.47 default price. History requests were blocked externally to exercise bundled observations offline. No uncaught browser errors were observed.
- Local links, packaged-resource routes, and whitespace were checked. The temporary local Uvicorn server was stopped after verification.

Learner exercise answers remain personal work. No completion-time or learner-usability study was performed. Source application validation does not record a deployment.

## Lesson 8 clarification — November 8, 2026

Defined cash-flow subscripts through the four promised payments and spot rates
through a single-payment purchase. The lesson now derives the semiannual
spot-rate/discount-factor conversion and pairs all four rates with factors and
payment PVs. It connects Treasury par quotes to coupon accounting before the
bootstrap example. References to lesson 1 fell from six to one opening link.
Continuous compounding stays in the expandable conventions calculation.
The rate conventions and par-yield relationship follow sections 2.1–2.2 of the
[Fed methodology](https://www.federalreserve.gov/pubs/feds/2006/200628/index.html).

Targeted checks verified the lesson route, table, collapsed details and remaining
recall link. All four spot rates round to the displayed four decimal places in
percent, with factor round trips agreeing within absolute 1e-14. Both note prices
and the displayed YTM were reproduced. All 24 formulas rendered with bundled
KaTeX. Visible article copy measures 735 whitespace-delimited words including
math and table text, excluding closed details. The experiment instructions still
assign the $101.40 → $100.37 calibration change and Reset restores $101.40.
This documentation check did not include a fresh browser layout review.

## Lesson 8 par and spot comparison — November 8, 2026

Added a worked comparison using the existing factors. A two-year single payment
gives a 5.3380% spot yield. Solving for the coupon that makes a two-year note worth
$100 gives a 5.2632% par yield. The explanation connects the difference to earlier
coupon dates and states the flat-curve boundary. The existing changed-input
question now asks for both yields after the calibration-price change. Lesson 1
has one opening recall link.

Targeted numerical, route and bundled-KaTeX checks passed, including the changed
case. All 32 formulas rendered. Visible article copy is 963 whitespace-delimited
words, including math/table text and excluding closed details. Sources,
tolerances and numerical results are recorded in
[the reference validation](phase_1_validation.md#lesson-8-par-and-spot-yields--november-8-2026).
These were documentation checks without a fresh browser layout review.
