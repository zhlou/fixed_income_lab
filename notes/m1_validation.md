# M1 validation — duration, convexity, and yield scenarios

Implemented November 1, 2026. Software and reference checks do not establish
learner completion. Reflection remains pending in [the learning journal](m1_learning_journal.md).

## Definitions and independent checks

Risk is with respect to annual nominal decimal YTM at fixed payment/settlement
dates. Regular-period prices use the original coupon pricer. Macaulay duration
is PV-weighted time; modified duration is −P′/P; dollar duration is −P′; positive
DV01 is −P′ × 0.0001. Convexity is P″/P, without a factor of one-half. Scenarios
are instantaneous price changes, not returns or forecasts.

| Check | Independent expectation | Tolerance / rationale |
|---|---|---|
| Regular zero coupon | Dmac = T; Dmod = T/q; C = T(T+1/m)/q², q = 1+y/m | Relative 1e-13 (duration absolute 1e-12); closed form vs weighted sum |
| Two annual payments at zero yield | 10 at year 1, 110 at year 2: price 120, duration 23/12, convexity 680/120 | pytest default relative 1e-6, exact arithmetic identities |
| Regular analytical vs central differences | Coupon 0%, 4%, 12%; annual through monthly; yield −1%, 0%, 5% | Duration relative 1e-7; convexity 3e-7 at ±0.5 bp, allowing truncation/cancellation |
| Bump convergence | Errors approximately quarter when h halves | Ratio 0.25 ±0.005 at 100, 50, 25 bp; before rounding dominates |
| CME price-bump example | Prices 108661.41, 108593.75, 108526.14 at 3.78%, 3.79%, 3.80%; published DV01 67.64 | Absolute $0.0051 for printed cents/tie rounding; implied duration 6.23 ±0.005 |
| Coupon-date settlement | Dated dirty-price risk matches regular-period analytical risk | Duration relative 1e-8; convexity 3e-7 |
| Final dated payment | P = 102/(1+yw/2); D = (w/2)/(1+yw/2); C = 2D² | Duration relative 3e-7; convexity 3e-5 using a ±10 bp diagnostic bump, including day before redemption |

The CME example validates arithmetic on its published prices, **not** reproduction
of that security by our settlement engine: the note does not supply enough
matching settlement information. Its rounded sensitivity inputs cannot serve as
an exact bond-pricing benchmark.

Sources checked November 1, 2026:

- [CME: Calculating the Dollar Value of a Basis Point](https://www.cmegroup.com/trading/interest-rates/files/Calculating_the_Dollar_Value_of_a_Basis_Point.pdf), Exhibit 2 and the modified-duration relationship.
- [CFA Institute: Yield-Based Bond Duration Measures and Properties](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/yield-based-bond-duration-measures-and-properties), conceptual context for own-yield sensitivity.
- [Existing Treasury reference checks](phase_1_validation.md) continue to validate the unchanged pricing engines.

The zero-coupon, two-payment, and final-fractional-period references above are
independent algebraic examples. New mathematics is implemented directly, without
using a reference pricing library as the calculation engine.

## Reproducible worked examples

At $100 face, 4% coupon, 5% nominal yield, semiannual payments:

| Maturity | Price (cents) | Macaulay | Modified | Convexity | DV01 (cents) |
|---|---:|---:|---:|---:|---:|
| 2 years | $98.12 | 1.941305 | 1.893956 | 4.573232 | $0.02 |
| 10 years | $92.21 | 8.255587 | 8.054231 | 77.111675 | $0.07 |

The ten-year +200 bp case has exact change −$13.52, first-order change −$14.85,
and second-order change −$13.43. Signed errors (estimate minus exact) are −$1.33
and +$0.09. Calculations retain full precision; display rounding is not used as
an input to further calculations. Scaling face scales dollar exposure, not
normalized duration or convexity.

## Dated model boundaries

Dated risk uses the original Actual/Actual coupon-period accrual and simple
first-fractional-period pricing with compound full periods. The website uses a
±0.5 bp central bump and displays ±1, ±0.5, and ±0.25 bp convergence diagnostics.
Dirty price is the normalizer. Accrued interest is fixed during the yield shock,
so clean and dirty dollar sensitivity agree, but their normalized sensitivities
need not. No regular-period Macaulay conversion is claimed between coupons.

The final-payment closed-form test uses a larger diagnostic bump to avoid loss
of second-difference precision extremely near redemption. The displayed
convergence table is diagnostic, not a universal accuracy guarantee. No stubs,
holiday shifts, ex-coupon rules, settlement lags, callable cash flows, or
nonparallel curve risk have been added.

## API, files, and interface

`POST /api/risk` is checked against the financial functions and cash-flow totals.
`POST /api/risk-study` validates a complete version-1 input snapshot, its kind,
and convention identifier. Regular and dated configurations round-trip exactly;
incompatible versions, conventions, missing inputs, and unsupported schedules
are rejected. Input files contain no computed prices; import recalculates them.

The risk interface shares the existing abort/request-sequence mechanism. Changed
or invalid inputs disable export; prior results remain explicitly labeled until
the latest valid calculation arrives. Import validation does not replace the
current comparison until successful. Import responses are invalidated if the
user edits the form while validation is pending.

Browser verification and final test results are recorded in `PROJECT_STATUS.md`.
Run numerical and API checks with `python -m pytest -q`.
