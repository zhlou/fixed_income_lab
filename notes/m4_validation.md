# M4 validation — November 8, 2026

## Source acquisition and reconstruction

Official [Fed nominal curve page](https://www.federalreserve.gov/data/nominal-yield-curve.htm),
[CSV](https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv), and
[GSW methodology, sections 2–5 and Table 1](https://www.federalreserve.gov/pubs/feds/2006/200628/index.html).
Acquired 2026-11-08T23:02:04.308145+00:00. Exact parent SHA-256
`3130a6f0c7af3bf85d3b6076db19085a45c09932745a56cc3c45b60f496c4051`. Parent file has 16,668,595 bytes,
17,058 dated rows, 100 columns and nine preamble lines, covering 1961-06-14 to
2026-10-30. Full raw acquisition is retained at `/private/tmp/filab-fed-m4.csv`
in this validation environment. It is a temporary local record. The repository
preserves exact source lines for six dates, the preamble/header, and acquisition
metadata in the packaged `fed-sample.csv` and `fed-sample.json`. Each excerpt is
identified by the parent hash. Published October 30 one-year zero yield is 4.3905%.

Source yields and betas are percentage points per annum, taus years. Normalize
yields/betas by dividing by 100; retain taus. `NA`, empty cells and `-999.99`
sentinels become missing, including the inactive pre-1980 TAU2. Before 1980,
BETA3 is zero and the Nelson–Siegel term omits TAU2. From 1980 use Svensson.
Missing rows remain in the dataset. A row with no model data displays No data.

GSW gives z(t) = beta0 + beta1 A(t/tau1) + beta2[A(t/tau1)-exp(-t/tau1)]
+ beta3[A(t/tau2)-exp(-t/tau2)], A(x)=(1-exp(-x))/x. D(t)=exp(-t z(t)).
Use expm1 for the loading near zero. Instantaneous forwards follow the analytic
GSW formula. Semiannual par yield is 2(1-D(T))/sum(D(k/2)).

Source nodes have four decimal places in percentage points. The absolute
comparison tolerance is 5.1e-7 in decimal rates (0.000051 percentage points),
half a source increment plus a numerical margin. Audit every published zero,
instantaneous-forward and par node through the historical maximum. All 16,309
model-bearing rows were evaluated; 749 rows contain missing model data.
16 rows exceed rounding tolerance. Global maxima, including those rows, follow.

| Series | Date | Years | Maximum absolute decimal-rate error | Basis points |
|---|---|---:|---:|---:|
| Zero | 2013-10-16 | 6 | 0.000003796498729707193 | 0.0379649873 |
| Instantaneous forward | 2013-10-16 | 29 | 0.00001561076784589721 | 0.1561076785 |
| Par | 2011-08-03 | 30 | 0.0005919783700808132 | 5.9197837008 |

Dates exceeding tolerance are 2002-01-16, 2003-05-20, 2003-05-21, 2004-08-13,
2007-10-09, 2008-05-28, 2008-07-16, 2008-08-04, 2009-10-26, 2009-11-03,
2009-11-04, 2011-08-03, 2013-10-16, 2013-11-22, 2018-02-08 and 2018-10-10.
The cause of these source inconsistencies remains unverified. The adapter keeps
published values, reports the error, and blocks parameter-based valuation on
affected dates. A larger tolerance would hide discrepancies in the acquisition.

## Short-maturity decision and historical bounds

GSW excludes bills and coupon securities shorter than three months, warns about
shortest-maturity behavior, and publishes nodes beginning at one year. The
published one-year par yield indirectly checks its model's exact half-year
factor. That identity provides no independent validation of the entire subyear
interval needed by calendar-dated or aging notes. M4 therefore conservatively
supports historical payments from one year through the last contiguous complete
published node. This is the Lab's support policy. D(0)=1 alone does not validate
an interpolated historical short end.

Apply GSW's historical maximum bounds of 7 years before 1971-08-16, 10 before
1971-11-15, 15 before 1981-07-02, 20 before 1985-11-25, then 30. Missing published
nodes can shorten the supported range. No extrapolated historical price is
reported. Every nonzero payment is checked, including principal.

The following is a **hypothetical sensitivity diagnostic**, using October 30,
2026 parameters and $100 face, 4% semiannual notes. Calendar curve times use
ACT/365 Fixed, separately from Actual/Actual coupon accrual. Newly issued notes
have regular coupons six months later. One-month-aged notes use a regular
maturity-anchored schedule with EOM handling.

Compare unrestricted fitted discount factors with an explicit log-linear bridge
from D(0)=1 to fitted D(1) for all subyear payments. Longer payments use the same
fitted curve in both calculations. Both totals are hypothetical model outputs.

| Original years | Age months | Payments checked | Unsupported payment dates (ACT/365F years) | Fitted-formula dirty price | Bridge dirty price | Difference / $100 |
|---|---:|---:|---|---:|---:|---:|
| 2 | 0 | 4 | 2027-04-30 (0.498630) | 98.8700962123 | 98.8687599025 | 0.0013363098 |
| 2 | 1 | 4 | 2027-03-31 (0.416438), 2027-09-30 (0.917808) | 99.2551817449 | 99.2534991901 | 0.0016825548 |
| 10 | 0 | 20 | 2027-04-30 (0.498630) | 92.4947160091 | 92.4933796993 | 0.0013363098 |
| 10 | 1 | 20 | 2027-03-31 (0.416438), 2027-09-30 (0.917808) | 92.9015785779 | 92.8998960231 | 0.0016825548 |

These small differences on one date leave independent short-end validation open.
**Decision** — historical coupon-note prices and M5 strategy support remain
conditional on validating every required horizon. The Explorer exposes affected
payments with unavailable PVs and total price. A zero-coupon principal within
the supported interval can be valued. All historical prices are model-derived
synthetic values using a current revised vintage; exact historical publication
times and point-in-time release archives are unavailable.

## Independent arithmetic and checks

Half-year synthetic factors 0.99, 0.97, 0.94, 0.90 imply $101.40 for the 6%
calibration bond and $97.60 for the 4% note. At six months after payment, remaining
price is $99.80, coupon cash $2 and wealth $101.80. At one year, price $100.92,
coupon cash $4 and wealth $104.92. Calibration price $100.37 implies D(2)=0.89
and initial note price $96.58. At maturity remaining price is zero and payments
received total $108. The six-month forward from six months is 4.12371134020619%.
Independent decimal arithmetic and automated tests use 1e-12 absolute dollar
and 1e-14 factor/rate tolerances for these small synthetic examples.

Synthetic curves interpolate log factors, accept negative-rate factors above
one, and reject extrapolation. Flat curves match the existing regular-period
pricer under matching coupon-time conventions. Dated tests verify after-payment
ownership and clean + accrual = dirty. ACT/365F curve discounting can differ from
the existing dated YTM model's simple first-fractional-period convention.

Execution results are recorded below after final verification. Software checks
leave learner reflection and transfer exercises pending.


## Final software verification

- Python 3.12 suite passed **543 tests**, including 23 dedicated M4 cases and
  registry-driven page/navigation coverage. Seven JavaScript date/month helper
  tests passed. The existing upstream Starlette/httpx deprecation warning remains.
- Chrome checks covered both lessons and the Explorer at 1440×900, 390×900 and
  320×900, with no horizontal document overflow or uncaught page errors. Formula
  rendering, collapsed answers, calibration changes, resets and keyboard calendar
  arrows/Enter were checked. Screenshots were inspected.
- The actual 16.7 MB official CSV imported successfully, with external source
  access blocked in the browser. Duplicate imports reused the saved version;
  reload retained it; a separate profile contained only bundled data. A revised
  byte stream saved another version, and the earlier imported version reopened
  with its original hash. Browser CSV export reproduced the full parent SHA-256.
  No import silently replaced an open comparison.
- Malformed files, an interrupted normalization request, and an explicitly aborted
  IndexedDB write transaction preserved prior datasets/results. Disabling browser
  storage retained the bundled example. Delayed synthetic responses followed by
  Reset retained the reset result. Invalid calibration prices were rejected.
- A wheel was built and installed into a separate temporary target. From a different
  working directory, with external socket connections rejected, 15 page/asset
  checks, the packaged raw sample, synthetic prices and historical numerical APIs
  passed. Runtime dependencies came from the existing Python environment.

The two added articles contain **313 and 347 visible words** respectively using
rendered whitespace-delimited text, including math/table text and excluding closed
answers. Experiment instructions were reviewed separately. The calibration lesson
starts at time zero and the aging lesson at six months. These counts do not measure
learning time. The seven-lesson core is retained, with a link updated to the new
material.

The regular maturity-anchored calendar rule can prevent a newly issued coupon-note
example on February 28 in a leap year when its intended even-year maturity is
month-end. The Explorer reports the unavailable regular grid and keeps the
historical curve visible. It does not create a stub. Zero-coupon principal
valuation remains available at supported maturities. This boundary is tested.

Historical coupon-bond backtests still require short-end validation, and
point-in-time research requires historical release evidence. Deployment and
learner reflection remain separate follow-up actions.
