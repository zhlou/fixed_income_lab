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

## Automated and runtime checks — initial four-lesson release

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

## Browser checks — initial four-lesson release

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


## Maturity-axis and curriculum refinement — November 7, 2026

Committed the original M3 worktree and navigation fix as `01ac172` before this
refinement. The current course has sixteen lessons: lesson 14 includes the
missing-data checkpoint, while timing and vintages are lessons 15 and 16. The
standalone missing-observations page is removed. The 1.5-month introduction,
absent February 17 row, distinction for dates outside cached coverage, common-
sample check, and unanswered journal prompts remain.

History charts now default to logarithmic maturity spacing from one month to
thirty years. A visible Linear option uses the original zero-to-thirty-year
spacing. The yield axis, source observations, API calculations, and gap policy
are unchanged. Labels use familiar month/year units and adjust to panel width;
resizing and changing the scale redraw locally without fetching new observations.
Reset restores the pinned dates and Log spacing.

Validation performed:

- **479 pytest cases passed** on Python 3.12 after removing two obsolete lesson
  cases and adding the merged-section/renumbering case. The existing
  Starlette/httpx deprecation warning remains. JavaScript syntax checking passed.
- Browser checks at **1440, 900, 390, and 320 pixels** found no horizontal page
  overflow or formula errors. Month/year ticks adapt to available width and
  remain readable. No JavaScript console errors were observed.
- Default and linear charts both contain 27 markers: thirteen on February 14
  and fourteen on February 18. The table contents and all marker y coordinates
  agree exactly before and after switching scales. The spread remains +5 bp.
- On the logarithmic chart, the 1→2-year and 5→10-year horizontal distances
  both measured about 116.935607 pixels in the desktop viewer (agreement within
  1e-10 pixels, allowing floating-point drawing precision). This checks the
  ratio interpretation independently of the axis label.
- Keyboard radio selection, reset to Log, and the February 17 preset worked.
  The preset leaves only fourteen second-date markers and excludes all
  two-date changes.
- A wheel built from a clean source copy and installed outside the checkout
  served the three M3 lessons, viewer, assets, 16-lesson
  overview, and original +5 bp benchmark with socket connections rejected.
  The retired standalone Markdown is absent from the clean wheel. Existing
  environment dependencies supplied the web runtime.

The temporary verification server was stopped after checks. Preview:
`/tmp/filab-log-maturity.png`. Learner reflection remains pending. The Fed
short-end feasibility gate and M4/M5 estimates above are unchanged.

The consolidation uses ordinary lesson routing and Markdown rendering. No
retired-lesson redirect or heading-specific renderer is retained. The full
479-test suite was rerun after this cleanup.


## Published-date calendar checks — November 7, 2026

The shared date controls use a local annotated calendar and typed ISO dates.
`GET /api/history/snapshots/{snapshot_id}/dates` returns only the selected
snapshot ID, coverage intervals, and sorted published-row dates. Read requests
never import or refresh source data. Metadata remains pinned even if a newer
snapshot changes the observation-date set. Frontend request sequencing prevents
a late response from replacing a newer selection's availability labels.

Published-row presence is independent of tenor completeness: February 14 is
marked published despite its absent 1.5-month tenor. In the pinned February
calendar, 19 dates have rows and 9 do not. The 42-cell month view additionally
shows fourteen adjacent-month dates outside this sample's coverage. Those three
states use distinct symbols and text, alongside color. No date is silently moved
or excluded from selection because of its availability state.

Checks performed:

- **482 pytest cases passed**, including the new metadata API, cache-only reads,
  partial-tenor rows, unknown snapshot IDs, changed observation-date sets in a
  new snapshot, and calendar-control integration. The same upstream TestClient
  deprecation warning remains.
- **3 Node helper tests passed**, covering valid/invalid ISO Gregorian dates,
  leap years including 1900/2000, month/year clamping and bounds, discontinuous
  coverage intervals, missing rows, and unloaded metadata.
- Browser checks at 1440×900, 390×844, 320×844, and 320×480 verified dialog
  containment, readable markers, two field labels, selected-day focus, keyboard
  arrow/Home/End/Page Up/Page Down navigation, Tab/Shift+Tab containment, Escape,
  backdrop dismissal, and focus restoration. The short dialog scrolls vertically
  and keeps its Close control available. No horizontal overflow was observed.
- Selecting February 17 shows an immediate no-row label and produces the same
  unavailable comparison as before; the first curve disappears while February
  18 retains fourteen markers. Typing March 3 in the pinned sample immediately
  reports outside coverage. February 30 is rejected. Reset restores the example.
- In the full 2025 snapshot March 3 is published; switching back to the pinned
  month changes its label to outside coverage. Opening a calendar, typing, and
  navigating months do not acquire additional Treasury data.
- A clean wheel installation outside the checkout served the new calendar script,
  viewer, three lessons, dates API, and original +5 bp comparison with socket
  connections rejected. Browser console checks reported no JavaScript errors.

The interactions follow the [W3C date-picker keyboard pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/),
using a native modal dialog, one day in the grid's Tab sequence, and explicit
focus cycling for browsers that otherwise skip buttons. The browser accessibility
tree exposes the dialog name, full dates, and availability descriptions. These
were browser and keyboard checks, not a full assistive-technology compatibility
review. The temporary server was stopped. Preview: `/tmp/filab-published-dates.png`.


## Recent default example — November 7, 2026

Added the official [November 2026 Treasury table](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202611&type=daily_treasury_yield_curve)
and [monthly XML response](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202611)
as the primary pinned example. Acquired at `2026-11-08T01:03:31.919610Z`
(November 7 in America/Chicago); raw SHA-256:
`a7f1e33d97317dbcdf577ec8236c81c736ec0a3db4b4da89ce839c25e38b99b4`.
The snapshot ID is
`37c7e5eac17863e453a25c2e4221a215bcf499bfac378747fa0d9fa75a636ac2`.
Coverage is explicitly November 1–7, not the whole future month. The five
published dates are November 2, 3, 4, 5, and 6; all fourteen tenors are present.

| Benchmark | November 5 | November 6 | Change |
|---|---:|---:|---:|
| Two-year par yield | 4.46% | 4.51% | +5 bp |
| Ten-year par yield | 4.84% | 4.86% | +2 bp |
| Ten-year minus two-year | 38 bp | 35 bp | −3 bp |

The XML matches the published table. Source percentages are retained exactly;
decimal normalization is checked within `1e-15` absolute rate units, and the
published basis-point differences are exact Decimal arithmetic. The revised
transfer case uses November 4's 4.58%/4.90% yields (32 bp spread), widening +6 bp
to November 5 even though both yields fall. The hypothetical +10 bp ten-year
revision on November 6 gives 45 bp and a +7 bp change from November 5.

The February fixture and its original snapshot ID remain available as the
series-introduction example. Original financial benchmarks above still apply.
Lesson 14 switches explicitly between both named bundled datasets; reset restores
November. Default inputs and labels come from the fixture metadata, avoiding
independent template/JavaScript date defaults. Imported snapshots retain all
covered years outside the requested annual refresh range, including the recent
bundled period.

Checks: **486 pytest cases** and **3 Node helper tests** passed. Targeted history
checks also passed after consolidating shared metadata. Browser checks at 1440,
390, and 320 pixels found no horizontal overflow, formula errors, or console
errors across all three M3 lessons. Recent defaults show −3 bp and 28 markers;
Series introduction shows +5 bp and 27 markers, preserving the blank tenor.
The November calendar shows five published dates, two dates without a row, and
35 cells outside coverage. The no-row preset retains only the fourteen November
6 markers, and reset restores November 5/6 and the recent sample. The revised
hypothetical exercise reproduces +7 bp. A clean wheel installed outside the
checkout served both examples, date metadata, lessons/assets, and the −3/+5 bp
benchmarks with socket connections rejected and no runtime database created.
The temporary browser verification server was stopped. Preview:
`/tmp/filab-recent-treasury.png`.

### Automatic month fetching — feasibility estimate only

The [official XML interface](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed)
supports `field_tdr_date_value_month=YYYYMM`, and the new pinned response verifies
that route. No API key was needed for the public request. The existing URL builder
and normalizer can support a month adapter.

The larger work is the current store's annual replacement and year-keyed source
metadata. Month loading must retain the raw/hash/retrieval evidence for every
contributing period and preserve old comparison IDs. A calendar month change can
load new data in the background; the displayed comparison should retain its
original snapshot until the user compares the new inputs. Keep lesson examples
frozen for reproducible exercises.

A provisional **8–16 focused development hours** covers:

- Monthly acquisition, coverage merging, and provenance: 3–6 hours.
- Calendar loading/error state, request debounce/deduplication, and cache hits:
  2–4 hours.
- Offline/failure recovery, current/future/empty-month rules, stale responses,
  and UI validation: 3–6 hours.

This is a planning judgment based on the current source and code review, not
measured implementation time. At that checkpoint, monthly auto-fetching was not implemented; the user requested
the assessment only. The subsequent implementation is recorded below.


### Automatic monthly loading and October–November starter — November 7, 2026

The user subsequently requested implementation. Acquired the official monthly
XML endpoints for `202610` and `202611`, preserving exact response bytes as
`treasury-cache-202610.xml` and `treasury-cache-202611.xml` plus JSON metadata.
The frozen teaching fixtures were preserved separately.

| Period | UTC retrieval | SHA-256 | Coverage and rows |
|---|---|---|---|
| October 2026 | 2026-11-08T02:13:36.102713Z | `85da7370e7dfa1e26145a4b05441df8dcf09a9e429f7dae773574d61394dd391` | October 1–31; 21 rows, latest October 30 |
| November 2026 | 2026-11-08T02:13:38.190660Z | `a7f1e33d97317dbcdf577ec8236c81c736ec0a3db4b4da89ce839c25e38b99b4` | November 1–7; five rows, latest November 6 |

Sources: [October XML](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202610),
[November XML](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202611),
[October published table](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202610),
and [monthly feed documentation](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed).
The retrieval dates above are November 7 in America/Chicago. Acquisition time is
not an individual observation's publication time.

Independently checked October 30 in the published table: 2-year **4.56%**,
10-year **4.94%**, spread **38 bp**. Against November 6 (4.51% / 4.86%, 35 bp),
the changes are **−5 bp / −8 bp**, and spread change **−3 bp**. Decimal source
strings give exact integer basis-point benchmarks; decimal-rate checks retain
absolute tolerance `1e-15`. These are par observations, not investment returns.

The 26-row starter snapshot is
`56ce7185a76d063379c1b920524836387e36330f75f3a1ff189765a47f41e2b0`.
Its coverage is October 1–November 7. Persisted both source responses and this
snapshot in `~/.local/share/fixed-income-lab`, with a readback confirming 21 + 5
rows. A fresh package provides the same dataset without a runtime database.
The lesson November and February snapshot IDs and benchmarks remain intact.

The independent store now overlays inclusive periods, splitting source coverage
when needed and preserving a unique response reference for contributing dates.
Older year-keyed snapshot metadata remains readable. A successful monthly check
is cached separately from immutable snapshot provenance, so identical data do not
force repeated hourly requests or rewrite the original retrieval time. A newer
annual source takes precedence over an older month check. Candidate view and
working-cache snapshots commit atomically; cross-process file locking serializes
writers and rechecks cache availability to avoid duplicate acquisitions.

The standalone client debounces month navigation and typed dates, serializes
loads, deduplicates identical pending months, and discards stale results after
navigation, reset, or dataset changes. Requests use the same-origin server rather
than relying on Treasury browser CORS. Complete historical months are reused;
the current month is checked after one hour or explicit forced Retry. Future
months are rejected without acquisition. A valid empty monthly feed establishes
coverage without rows; malformed responses and timeouts do not establish new
coverage. Cached partial months remain partial after offline failures. Lesson
calendars remain cache-only. Calendar updates never replace an open financial
comparison; Compare explicitly chooses the updated snapshot.

Checks performed:

- **509 Python cases and seven Node cases pass.** New coverage includes monthly
  source merging, idempotency, revisions and older snapshots, annual/monthly
  source precedence, empty responses, stale current-month checks, partial offline
  fallback, interrupted acquisition, concurrent-client deduplication, strict API
  inputs, job reuse, and Python/API parity. Node cases cover debounce, ordering,
  cancellation, stale success/error responses, and forced retry.
- Live browser navigation fetched uncached September 2026 (21 additional rows)
  into a temporary verification cache; markers and coverage updated to 47 rows,
  while the November curves retained their original snapshot until Compare.
  An October 30 / November 6 comparison reproduced 38 → 35 bp. The extra September
  data were verification-only and were not added to the bundled or user cache.
- Browser checks at 1440×900, 390×844, and 320×480 covered cached months, future
  December, Page Up/Down, Tab/Shift+Tab, Escape, focus retention and restoration,
  older dataset selection, immediate coverage summary, reset, and exact-date
  comparison. The compact dialog fit at 304×456 with vertical scrolling and no
  horizontal overflow. No console errors were observed.
- A temporary server with acquisition disabled reproduced an uncached-month
  error, visible Retry, repeated failure, and reset while a request was pending.
  Previous curves and cached dates survived. Lessons 14/15 retained the frozen
  −3 bp exercise; lesson calendar navigation produced no month-loading state.
- A clean wheel installed outside the checkout passed with socket connections
  rejected: all 26 starter rows, both lesson benchmarks, four pages, calendar
  assets and metadata, and a cached October load without a runtime directory.
  A final UI-only summary/focus refinement was verified on a fresh local origin.

The upstream Starlette/httpx deprecation warning remains. Browser preview:
`/tmp/filab-auto-month-calendar.png`. Temporary servers were stopped after checks.
Learner reflections remain unanswered. The earlier 8–16-hour estimate was a
planning estimate, not measured implementation time.


### Month exploration in lessons and deployed release — November 7, 2026

The user approved enabling the shared month loader in lessons 14–16. Lessons
still open on the pinned November 5/6 snapshot. Opening that pinned month and
Reset suppress acquisition, preserving offline reproducibility. Other months
can be explored directly from either calendar or typed date field. A live notice
marks dates or a dataset that differ from the selected worked example. The
written explanation retains its published benchmark. Reset cancels pending UI
updates and restores the November dataset, dates, Log axis, recent example
choice, and published revision setting. Lesson 14's February worked example
still reproduces +5 bp with its missing 1.5-month observation.

The +10 bp hypothetical proposal is calculated in the independent Python data
module. The comparison API returns `revision_scenario`: selected second date,
original and proposed percentage strings/decimal rates, assumption in basis
points, and whether it was applied. The lesson description uses this evidence
instead of a hardcoded November date. Missing rows and missing ten-year yields
produce no revision; a genuine zero remains a usable observation. The proposal
and the hypothetical comparison never alter the immutable source snapshot.

On October 30, the existing source benchmark of 4.94% becomes a **hypothetical
5.04%**, exactly +10 bp. The API case with November 6 first gives spreads
35 → 48 bp and a +13 bp hypothetical change. Browser testing with November 5
first gives 38 → 48 bp and +10 bp. The original default November scenario remains
38 → 45 bp and +7 bp. This extends the prior benchmark/identity checks; it adds
no source observation or valuation convention.

First-party CSS and JavaScript now use content hashes in their URLs. Hashes are
computed at server startup and served by the same local static routes. Upgrading
the container therefore requests the scripts that match the new HTML/API;
vendored KaTeX and all offline resources remain local.

Validation performed:

- **516 Python tests and seven Node tests pass.** Added checks cover arbitrary
  revision dates, immutable originals, missing rows, outside coverage, missing
  tenors versus genuine zero, versioned asset contents, and loading bundled
  October onto a lesson snapshot with acquisition forbidden. API parity checks
  account for the separately labeled scenario metadata.
- Browser checks at 1440×1000, 390×844, and 320×480 covered all three lessons,
  October loading, a live uncached September load in lesson 15, February sample
  selection, exact dates, reset, missing October 31, and dynamic hypothetical
  results. At 320×480 the calendar fit at 304×456, with working Page Down, Tab,
  Escape, and no horizontal overflow. No formula or console errors were observed.
- A temporary acquisition-disabled server reproduced lesson errors, visible Retry,
  cached curves remaining intact, and Reset while a retry was pending. The
  canceled response did not replace the restored pinned sample or notice.
- Rebuilt `fixed-income-lab:lesson-history` on the existing `deepl` engine; the
  dependency layer remained cached. An unprivileged installed-image probe with
  `--network none` served all three lessons, verified each versioned asset hash,
  loaded October from bundled data, retained the five-row pinned snapshot, and
  reproduced the hypothetical +13 bp API case. `pip check` passed. The disposable
  probe container was removed.
- Deployed image `a417eaeea5834f0cb2d5e36065d3ca18f05a1977d06c8131bcd59834b94e097e`
  as container `gracious_mcnulty` (`42724e4c402f`), preserving its existing port
  8000 mapping, user, bridge network, and restart policy. The previous container
  had no runtime cache to copy. It is retained, stopped, as
  `gracious_mcnulty-before-lessons-c992a5d6`; its image also has the rollback tag
  `fixed-income-lab:before-lesson-history`.
- Verified the actual `http://deepl.lan:8000/lessons/revisions-and-vintages` in the
  browser: October has 21 published rows, the exploration notice appears, the
  October 30 hypothetical reads 4.94% → 5.04%, and the spread result is +10 bp
  with November 5 first. The new script URL includes its content hash, and the
  console is clear. Preview: `/tmp/filab-lesson-history-live.png`.

Temporary local verification servers were stopped. The running deployment still
has no persistent volume, matching its prior configuration; README Docker volume
guidance applies to preserving future downloads across container replacement.
Learner reflections remain unanswered.


## Browser-owned history and visitor wording — November 8, 2026

This update supersedes the earlier web refresh/cache behavior. The original
acquisition and financial validation records above describe their dated releases.
The reusable on-disk SnapshotStore remains available for research scripts.

- Python 3.12.16 passed 525 tests. New coverage checks stateless normalization and
  comparison, raw-source/snapshot agreement, malformed imports, size bounds,
  cached-month overlays, retired web jobs, and read-only legacy export/import.
  The suite emits one existing Starlette/httpx deprecation warning.
- The February reference still gives 21 → 26 bp, with a +5 bp spread change.
  The pinned November reference still gives 38 → 35 bp, with a −3 bp change.
  These are exact differences of the published percentage strings in Decimal,
  with no new benchmark tolerance or financial convention.
- Seven Node calendar/loader tests passed strict dates, movement, availability,
  debounce, serialization, stale responses, reset, failure, and retry.
- Headless Chrome inspected all sixteen question headlines and three tools at
  1440×900 and 390×900, plus the landing page at 320×900. Formula markup rendered
  without KaTeX errors. No horizontal document overflow or uncaught JavaScript
  errors were observed. Keyboard Enter activated the tools anchor on mobile.
- Browser tests blocked Treasury to exercise No data with one available curve.
  Successful downloads used intercepted XML from the bundled fixture. To avoid
  using an already bundled month, one test shifted fixture date years to 2019.
  Those dates were synthetic test input, never empirical observations or bundled
  teaching data. Source hashes were computed from the actual test response bytes.
- Two isolated browser profiles against the same final Docker instance demonstrated private caches. Reload reused a
  saved month without another Treasury download. Export/import reproduced +5 bp
  in the other profile. A failure after the first successful annual response
  left the selected version and saved dataset list intact. An aborted IndexedDB write transaction also preserved saved snapshots and showed No data for the affected month. October exploration
  from a pinned November lesson reused bundled responses with Treasury blocked.
- A clean installed wheel in Docker served the landing page, lesson, new script,
  and stateless −3 bp comparison with --read-only and --network none. No runtime
  Treasury cache directory was created. The verification containers, local server, and SSH tunnel were stopped after checks.

The direct Treasury success path has been validated with intercepted responses.
Live CORS permission from a future public origin remains unverified. The intended
fallback for an inaccessible month is No data. Browser snapshots are lost when
site data is cleared, so portable exports include the original response bytes.
