# M3 validation — November 7, 2026

## Official benchmark and provenance

Source: [Treasury February 2025 nominal par observations](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202502&type=daily_treasury_yield_curve),
[XML interface](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed), and
[methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology).
The exact monthly response is packaged with acquisition metadata. Its SHA-256 is
`fe8797ee059916e82db163bccf88ebffd80458de000024963e0a784aed187443`;
retrieved at `2026-11-07T16:46:53Z`. The bundled normalized snapshot is
`0cc891c2abf9e5793c54012eaa8344ba3e8eeeab522b8c57eda4dfc54b525651`.
It has 19 published rows covering the requested month. Ten rows lack the
1.5-month tenor; that series starts February 18. All 19 rows support 2s10s.

| Benchmark | February 14 | February 18 | Change |
|---|---:|---:|---:|
| Two-year par yield | 4.26% | 4.29% | +3 bp |
| Ten-year par yield | 4.47% | 4.55% | +8 bp |
| Ten-year minus two-year | 21 bp | 26 bp | +5 bp |
| 1.5-month par yield | Missing | 4.41% | Undefined |

These independently published table values agree with the raw XML. Differences
are calculated from source decimal percentage strings using Decimal. The
benchmark basis-point results are exact at the published precision; normalized
binary float rates are checked within `1e-15` absolute decimal-rate tolerance,
far below one source rounding increment (`0.0001` decimal yield). No extra
precision is inferred. Reverse comparisons negate changes; identical dates have
zero changes only where the observations exist.

The hypothetical revision exercise adds 10 bp to the second-date ten-year rate.
On the default dates its spread is 36 bp and its spread change +15 bp. Those are
explicitly hypothetical, and the stored source snapshot remains unchanged.

## Automated and runtime checks

The Python 3.12 suite passes **480 tests**, including the prior financial and web
regressions. One upstream Starlette/httpx TestClient deprecation warning remains.
New checks cover null/absent versus genuine zero, common-date intersections,
exact-date coverage states, source/schema failures, duplicate rows, idempotent
retrievals, changed values, old-snapshot reopening, multiple-year merging,
failed-range atomicity, read-during-refresh behavior, process interruption before
publication, concurrent writer exclusion, API parity, and asynchronous job success
and failure. Refresh input validation rejects inverted/future ranges and arbitrary
source URL fields.

A live UI refresh of 2025 retrieved **249 rows** (January 2–December 31), retained
the pinned open comparison, and offered an explicit switch. Selecting the new
snapshot showed full-year coverage and 31 missing 1.5-month rows. Reset reopened
the pinned sample. The bundled month and annual response agree on the benchmark.

Live imports of 1990 and 2003 each validated 250 rows under the same normalizer,
including the historical missing-tenor patterns. These were additional source
probes, not a download or performance test of the entire archive.

An application wheel was built and installed with `--no-index --no-deps` into an
isolated target outside the checkout. Running from `/tmp` confirmed the installed
package path, all four M3 lessons, the viewer, overview, scripts/styles, KaTeX
script/font, catalog, and +5 bp comparison. Both socket connection entry points
were patched to reject networking throughout the offline runtime check. Existing
web dependencies were provided by the development environment; this verifies
application packaging and offline runtime, not a fresh dependency download.

## Browser checks

All four lessons were checked at 1440×900 and 390×844. No horizontal page overflow,
KaTeX rendering errors, or JavaScript console errors were observed. Checks covered
missing and outside-coverage dates, default reset, explicit year refresh and
snapshot switching, stale-input notices, keyboard submit, revision radio activation,
and Enter/Escape lesson-picker behavior. A source revision is simulated only in
the labeled lesson exercise; storage revisions are verified by automated tests.
The temporary verification server was stopped. Preview: `/tmp/filab-m3-desktop.png`.

## Model and operating limits

The source is the official nominal par feed; its indicative market inputs are
not executable prices. No interpolation, filling, security valuation, cash return,
or historical strategy result is added. A no-row weekday is labeled a
nonpublication/source gap, not confidently assigned to a holiday calendar.
Acquisition and observation times stay distinct; exact publication time is null.
Source feed `updated` timestamps remain in raw bytes without being treated as
historical information-availability evidence.

Refreshes fetch requested annual files sequentially, with a 45-second per-request
timeout and 4 MB response cap. The candidate is published only after every year
validates. Raw files and acquisition metadata survive validation failures.
Snapshot identity includes coverage and normalizer version; differing feed
metadata alone does not create a revision. A SQLite transaction switches the
active pointer, and POSIX file locks serialize writers. Refresh-job progress is
process-local, so a server restart loses the job status but preserves completed
snapshots. Resume by reopening the catalog and retrying. No full-archive runtime
or physical power-loss recovery claim is made.

## M4 historical-curve feasibility and estimates

The [Federal Reserve nominal-curve page](https://www.federalreserve.gov/data/nominal-yield-curve.htm)
describes daily fitted curves from 1961, using Nelson–Siegel before 1980 and
Svensson afterward. This is a staff research off-the-run coupon-security curve;
it excludes bills and recent on-the-run issues. Updates are typically weekly,
with delay, revision, and methodology-change risk. Its current vintage is not a
historical release archive.

The [GSW paper, definitions, estimation sample, and Table 1](https://www.federalreserve.gov/pubs/feds/2006/200628/index.html)
distinguishes continuously compounded spot/forward yields from coupon-equivalent
par yields. Published nodes begin at one year; the fit excludes sub-three-month
coupon securities and warns about shortest-maturity behavior and extrapolation.
Early history also has shorter maximum supported maturities. Parameters alone
therefore do not establish valid valuation for every short coupon horizon.

**Assessment:** promising adapter, with a short-end feasibility gate still open.
M4 must pin a current response, confirm parameter units and historical bounds,
reproduce published yields, and explicitly validate or reject discounting before
the first supported node. Treasury par observations must stay separate. No Fed
CSV ingestion, parameter reconstruction, or short-end valuation was implemented
or numerically validated in M3.

**Re-estimate (planning judgment, not logged work):** allow M4 **20–32 focused
hours**, including a 4–8-hour initial source/short-end gate beyond the previous
16–24-hour allowance. Keep M5 **24–40 hours**, conditional on that gate, and
re-estimate after the adapter works. M6/M7 remain 28–44 combined; remaining
M4–M7 allowance is **72–116 hours**. No historical backtest date is promised.
The original M3 16–24-hour budget was provisional; this session is not a measured
learning-time log. Learner reflections remain pending in the M3 journal.
