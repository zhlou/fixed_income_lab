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
