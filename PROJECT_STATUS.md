# Fixed-Income Lab — Status and Progress

**Updated:** November 7, 2026 (America/Chicago)

## Current status

**Foundations implementation and independent reference validation are complete
for the regular-coupon educational model** (original Phase 1, now M0).
The local website has **sixteen interactive lessons**. **M1 risk, M2 return
accounting, and M3 historical observations are implemented and validated**,
including the Risk Explorer, Bond Return Calculator, and Treasury History Viewer.
**M4 discount curves is next.** Curve valuation and historical strategy research
remain planned.

The revised plan prioritizes the user's intended daily use: **researching bond
strategies and historical returns**. It brings return accounting forward, targets
a small two-strategy historical research release at M5, and places TIPS, macro,
credit, and advanced models after the nominal Treasury research core.

Software completion does not mean the learner has completed the reflection
questions or demonstrated the learning checkpoints.

## Completed work

### Month exploration inside history lessons — November 7, 2026

Lessons 14–16 now share automatic month loading with the standalone viewer.
They still start with pinned November examples; opening the pinned month and
Reset do not contact Treasury. A notice distinguishes the worked example from
custom dates or datasets. Reset restores November 5/6, the original snapshot,
Log spacing, and the published-sample revision setting. The February example in
lesson 14 remains selectable.

Lesson 16 describes the selected second date's original and hypothetical ten-year
yields using Python-generated scenario metadata. Missing observations cannot be
revised, and no source data are changed. Versioned script and CSS URLs ensure a
new deployment loads the matching browser assets. Validation and deployment
results are recorded in [M3 validation](notes/m3_validation.md). All **516 Python
cases and seven JavaScript cases** pass. Desktop/mobile, keyboard, offline error
and retry, reset, and an installed image with networking disabled were checked.
The update is live on `deepl.lan:8000`, including the lesson 16 October calendar
and dynamic revision description. The predecessor container is retained stopped
for rollback; no existing runtime cache was present. Temporary test servers were
stopped.


### Automatic Treasury month loading — November 7, 2026

The viewer now ships October 2026 (21 rows) and available November observations
(November 2–6, five rows), with acquired coverage through November 7. Both exact
responses, hashes, and UTC acquisition metadata are bundled, and the requested
months were persisted in the default runtime cache. The starter snapshot is
`56ce7185a76d063379c1b920524836387e36330f75f3a1ff189765a47f41e2b0`.

Opening or changing a calendar month in the standalone viewer triggers a local
monthly load. Complete cached months are reused; current-month checks have a
one-hour freshness window. Requests are debounced, serialized, deduplicated,
and protected against stale UI updates. Errors retain prior data and offer
Retry. New calendar availability does not replace the displayed comparison until
Compare is pressed. Lessons retain their frozen examples and make no external
requests. Annual refresh and immutable older snapshots remain available.

All **509 Python cases and seven JavaScript cases** pass. Live month acquisition,
offline errors and retry, desktop/mobile keyboard use, older datasets, and a
clean installed wheel with networking disabled were verified. See
[M3 validation](notes/m3_validation.md) for sources, tolerances, and recovery checks.


### Recent Treasury example — November 7, 2026

The default history viewer and M3 lesson dates are now November 5/6, 2026, using
a newly acquired official November response frozen through November 7. It has
five published rows (November 2–6) and reproduces the 2s10s spread narrowing from
38 to 35 bp. Later dates in the month stay outside cached coverage. Lessons
14–16, transfer arithmetic, and the hypothetical revision (+7 bp spread change)
now match those recent observations.

The February 2025 response remains a second bundled snapshot. Lesson 14 offers
visible Recent example / Series introduction choices so the missing 1.5-month
tenor is still demonstrated with real historical data. Its original snapshot ID
and +5 bp result are preserved. Both samples work without a writable runtime
cache. API catalog metadata supplies shared date defaults and sample labels;
the viewer's coverage summary describes the currently selected dataset.

All **486 Python tests** and **3 calendar helper tests** pass. Browser checks on
all three lessons at 1440, 390, and 320 pixels covered recent defaults, historical
sample selection, reset, the November 7 no-row case, complete/partial tenor
counts, and the +7 bp hypothetical revision. No formula, console, or horizontal
layout errors were observed. A clean installed wheel passed both frozen examples
and their benchmarks offline without creating a runtime database. The temporary
verification server was stopped. Sources, hashes, and checks are in [M3 validation](notes/m3_validation.md).

At this earlier checkpoint, automatic month fetching was assessed only, at the user's request. Treasury
supports monthly requests, but the current cache merges annual periods and stores
source metadata by year. A robust month loader needs period-level provenance,
request deduplication, loading/error states, and careful snapshot handling. Allow
8–16 focused development hours provisionally; this is an estimate, not a delivery
commitment. This estimate was superseded by the automatic-month implementation above.

### Published-date calendars — November 7, 2026

Both Treasury comparison date fields now have a snapshot-aware calendar showing
● published rows, — dates without a row inside coverage, and ? dates outside
cached coverage. Status labels update as a date is typed. Missing dates remain
selectable, and a published row does not imply every tenor is present. The
calendar reads only the selected immutable snapshot, including when switching
between cached datasets; no Treasury refresh occurs while choosing dates.

Calendar dialogs support keyboard day/week/month/year movement, explicit Tab
focus cycling, Escape and backdrop dismissal, and focus restoration. Gregorian
validation rejects impossible dates; month changes clamp to a real day. The
viewer and all three M3 lessons use the shared controls.

All **482 Python tests** and **3 Node calendar helper tests** pass. Browser checks
covered 1440, 390, and 320-pixel widths plus 320×480, both date fields, keyboard
navigation, missing-date selection, invalid typed dates, reset, and snapshot
switching. No horizontal overflow or console errors were observed. A clean
installed wheel served the calendars and +5 bp benchmark with sockets rejected.
The temporary verification server was stopped. See [M3 validation](notes/m3_validation.md).

### Log maturity axis and a focused M3 sequence — November 7, 2026

After committing the M3 baseline as `01ac172`, refined the Treasury viewer to
use a logarithmic maturity axis by default, with visible Log/Linear option cards.
Only the horizontal spacing changes; yields, spreads, tabulated values, and
missing-tenor gaps remain the same. The chart adapts its width and month/year
ticks to the available space. Reset restores Log spacing.

Folded the former missing-observations lesson into lesson 14 as “Which observations
can we compare?”, retaining the 1.5-month example, February 17 experiment, and
common-sample checkpoint. The standalone page is removed. The timing and
vintage lessons are now 15 and 16. Navigation, overview, prerequisites, and the
curriculum plan follow the three-lesson M3 sequence. Learner answers remain pending.

The full suite passes **479 tests** after consolidating the lesson cases and
adding merged-section and renumbering coverage. Browser checks at
1440, 900, 390, and 320 pixels confirmed readable axes, no horizontal overflow,
keyboard scale changes, unchanged rates/spreads, reset, and missing dates.
A clean installed wheel passed the revised offline checks.
The temporary server was stopped. See [M3 validation](notes/m3_validation.md).

### History placement in the lesson picker — November 7, 2026

The popup now shows Foundations → Risk → Returns → History across four columns
on wide screens, so History no longer wraps beneath Foundations. At 681–1000
pixels it uses two columns; phones retain one column in curriculum order.

All 17 lesson-picker tests passed. Browser checks at 1440, 900, 390, and 320
pixels confirmed the group positions and picker width. Keyboard activation
reached the final History lesson at 320 pixels; no console errors were observed.
The temporary verification server was stopped afterward.

### M3 historical observations — November 7, 2026

Delivered four lessons on par observations, missing data, information timing, and
vintages, with `/tools/treasury-history`. The bundled exact Treasury February
2025 XML response reproduces the 21 → 26 bp spread example offline. A separate
Python data layer preserves raw bytes, hashes, acquisition timestamps, original
percentage strings, decimal rates, and immutable normalized snapshots. Explicit
annual range refreshes activate only after all selected years validate. Older
versions remain readable; a refresh never silently switches an open comparison.

All **480 tests pass** on Python 3.12.16. Checks include source benchmarks, missing
versus zero, sample intersections, duplicates/revisions, failed and interrupted
refreshes, concurrent writers, API parity, and navigation. The installed wheel
served the sample and bundled assets with networking rejected. Browser checks
covered all four lessons at 1440 and 390 pixels, formulas, keyboard controls,
missing/outside-coverage dates, stale-input notices, reset, and a live 2025 refresh.
No JavaScript or formula errors were observed. Live 1990 and 2003 imports each
validated 250 rows; the 2025 import validated 249. Temporary verification data
stays outside the repository. The verification server was stopped after checks.

The [M3 validation record](notes/m3_validation.md) documents evidence, limits,
and the Fed fitted-curve feasibility assessment. The short end remains an M4
gate: allow M4 20–32 focused hours and M5 24–40 conditional hours, with remaining
M4–M7 at 72–116 provisional hours. The [M3 learning journal](notes/m3_learning_journal.md)
remains unanswered, alongside M1/M2 learner checkpoints.

### README changes preserve the Docker dependency cache — November 7, 2026

The real README is now copied after dependency installation, alongside source.
An empty README and source directory satisfy setuptools during the metadata-only
`--only-deps` step. The final application build reads the real README, preserving
its package description. README and source edits now leave the dependency layer
cached when `pyproject.toml` is unchanged. README build guidance is updated.

Two builds on `deepl` confirmed that simultaneous README and source edits reused
dependency layer `079f05753a1e`. Installed package metadata matched the complete
README in both images, including the temporary verification edit in the second.
`pip check` passed; an unprivileged offline container served ten pages/assets
and the known pricing API example. Temporary containers and the edited test
image were removed, retaining parent layers and the baseline verification image
`fixed-income-lab:readme-cache-check`. The running deployment was not replaced.
Validation targeted Docker packaging and cache behavior.

### Hover lesson picker — November 7, 2026

The header lesson counter now opens a picker after 120 ms of hover, with a
250 ms grace period when leaving the button or list. All thirteen lessons appear
under Foundations, Risk, and Returns, using the curriculum registry and marking
the current lesson. Clicking keeps it open. Enter/Space, Tab, Escape, outside
clicks, and the Course drawer support keyboard use and dismissal. Phones show
a compact counter and a full-width scrollable list. Small headers use arrows
for Previous/Next while retaining their accessible names.

All **442 tests passed** on Python 3.12.16, including all thirteen lesson picker
pages. Chrome checks covered hover timing, diagonal movement and a one-click
lesson jump, click persistence, focus preservation/restoration, keyboard links,
Course dismissal, and responsive layouts. Every lesson header fit at 390 and
320 pixels, and the final destination was reachable by touch. Short-window checks
at 1440×480, 390×600, and 320×480 also reached the final lesson, scrolling the
phone list as needed. No JavaScript, formula, or console errors were observed.
README navigation guidance is updated. The temporary local server was stopped.

### Docker dependency cache — November 5, 2026

The Dockerfile uses pip 26.2+ and its native `--only-deps ".[web,build]"`
option before copying source. Build tools are declared in the new `build`
extra in `pyproject.toml`, alongside the existing application and web dependencies.
There is no custom TOML parser in the Dockerfile. Setuptools reads metadata
with the real README and an empty source directory; the complete source arrives
before the final `--no-deps --no-build-isolation` application install. A source
change rebuilds the application wheel without resolving dependencies or
downloading build tools again. README or metadata changes invalidate the
dependency layer. The README links pip's documentation and explains refreshes.

Two verification builds succeeded on the existing `deepl` Docker engine. A
temporary source-only comment reused the same dependency layer (`ccf3c7d2fb1d`)
and rebuilt the application package; the checkout's source was not modified.
`pip check` found no broken requirements. An unprivileged test container with
networking disabled served ten pages/assets and reproduced the known bond price
through `/api/valuation`, using the installed package from outside `/app`.
Temporary containers and the source-variant image tag were removed afterward.
The baseline verification image remains available as
`fixed-income-lab:pip-deps-check`. The running deployment was not replaced. Validation targeted the
changed build and runtime packaging; financial and UI code are unchanged.

### M2 lesson progression revised — November 5, 2026

Lessons 10–13 now build from **Coupons, accrual & return → Pull-to-par &
maturity → Reinvestment & cash → Holding-period return & early sale**. Lesson
10 introduces return with one bond and coupon cash before the dated example.
Lesson 11 holds YTM fixed through maturity; early-sale controls and the repeated
yield-shock example move to the final lesson. Lesson 13 combines the prior
concepts with costs and keeping versus selling. Portfolio aggregation is an
optional extension in the full calculator.

Overview cards, sidebar entries, previous/next links, prerequisites, tool links,
the plan, README, and unanswered journal follow the new order. Lesson URLs,
financial calculations, saved inputs, and full-calculator interfaces are
preserved; former pull-to-par early-sale API requests remain supported.

All **429 tests passed** on Python 3.12.16. Browser checks covered all four
lessons at 1440×900 and 390×844, formulas, navigation, keyboard presets/radios,
reset, mobile input/results switching, costs, maturity boundaries, and a lesson
transfer into the full calculator. No formula errors, horizontal page overflow,
or browser warning/error logs were observed. See [M2 validation](notes/m2_validation.md).
The temporary local server was stopped. The remote Docker deployment needs a
rebuild/recreation to serve this source revision. Learner checkpoints remain pending.

### Focused M2 lesson experiments — November 3, 2026

Lessons 10–13 now expose only the controls and examples relevant to their
financial question. Lesson 10 compares price change with return while varying
exit YTM and costs; lesson 11 follows coupon/accrual through a nearby date
window; lesson 12 isolates additional wealth from cash growth; lesson 13 compares
discount/premium convergence and early sale. Fixed assumptions are stated in
the input panel. Lesson guides use the visible controls and examples.

The full calculator remains at `/tools/bond-return`, including the four general
cases, arbitrary supported dates, quotes, a second position, costs, and files.
Each lesson can transfer its current validated inputs to that page. Shared
Python accounting/pricing and shared browser workspace navigation are retained.
Lesson APIs reject unrelated controls/scenarios. In lesson 13, price curves stop
before redemption; terminal cash and zero remaining face appear separately.

All **424 tests passed**, including 26 new focused-lesson cases. Desktop/short-
window/mobile browser checks covered only-relevant controls and presets,
complete charts, independent scrolling, date errors, conditional early-sale YTM,
keyboard interaction, resets, stale-response protection, and exact transfer to
the full calculator. Full-tool quote rounding, two positions, export/import,
and original numerical API parity also passed. No JavaScript/formula errors,
external asset requests, or unexpected console errors were observed. See
[M2 validation](notes/m2_validation.md). Learner reflection remains pending.

### M2 controls and chart layout — November 3, 2026

Reworked the M2 lesson workspace after use revealed that the long input form and
plot moved together. At desktop widths, inputs and results now have separate
scroll areas within the experiment; scrolling to a lower control leaves the
chart in place. Input sections expand individually and summarize their settings.
Reset and a one-click **View chart** action remain at the input column's foot.
All four example buttons remain visible in the compact toolbar; only save/load
actions expand. On smaller screens the examples and view switch stay together
while scrolling the experiment. Short desktop windows
retain the complete plot, axes, and curve labels.

Below 1200 pixels, an **Edit inputs / Results & chart** switch replaces the long
controls-before-results stack. It preserves all input values and makes returning
to the chart one tap. Errors reveal the relevant collapsed section. The shared
layout applies to lessons 10–13 and the standalone return calculator.

All **398 tests passed**. Chrome checks covered 1600/1440/1200×900,
1200/1600×600, 1024/768×900, 390×844, and 320×640. Checks confirmed an unchanged
plot position while scrolling/changing a lower input, independent result scrolling,
complete chart visibility, responsive switching, keyboard disclosures/radios,
quote rounding, comparison positions, import/export, reset, errors, and all four
M2 opening examples. No JavaScript or unexpected console errors were observed;
expected 422 responses came from invalid-input checks. Financial calculations
and curriculum content are unchanged. See [M2 validation](notes/m2_validation.md).

### M2 returns and cash accounting — November 3, 2026

Added `filab.analytics` with a deterministic dirty-price cash/position ledger:
opening purchases, every eligible coupon, final redemption once, early/horizon
sales, explicit cash growth, and closing valuations. Beginning wealth includes
entry costs; ending wealth includes credited cash. One-way costs are basis points
of face on purchases and sales. Settlement is after payment on coupon dates;
the existing regular dated pricing conventions remain in force.

Four separate lessons and `/tools/bond-return` explain price versus return,
coupons/accrual, cash reinvestment, and pull-to-par. The calculator supports
one/two-position aggregation, fixed or one-change hypothetical yield paths,
clean purchase quotes committed to cents, mark/liquidation, cash-policy comparison,
complete scenario-input export/import, and full-precision ledger export. The
domain/API additionally supports explicit step paths and early sales. Cash defaults
to 0%; optional annual effective interest uses Actual/365 Fixed separately from
the bond's Actual/Actual coupon-period accrual.

All **398 tests passed** on Python 3.12.16, including the independent annual
two-period ledger and nine OTS/OCC published return scenarios. Checks cover
cash/face conservation, payment eligibility and order, fees once, redemption once,
early-sale cash growth, report-grid independence, aggregation, financial boundaries,
API parity, saved inputs, and lesson navigation. The existing upstream
Starlette/httpx deprecation warning remains. See [M2 validation](notes/m2_validation.md)
for references, tolerances, browser checks, and limits.

M2 is a deterministic hypothetical experiment, without market history or strategy
backtests. Curved-term-structure roll-down remains in M4. Learner reflection is
pending in [the M2 journal](notes/m2_learning_journal.md). The existing remote
Docker deployment must be rebuilt/recreated to serve this source release.

### Docker health check removed — November 3, 2026

Removed the built-in periodic homepage health check and updated the Docker run
documentation. The image no longer schedules localhost requests; hosting-platform
probes can be configured separately if needed. Rebuilt `fixed-income-lab:local`
on `deepl` and confirmed that its health-check configuration is absent.

A temporary container passed homepage, lesson, risk-tool, local formula-asset,
and valuation API checks, then was removed. Recreated the existing `naughty_newton`
container with its original port 8000 mapping and verified that it runs without
a health check. The website remains available at `http://deepl.lan:8000`.
Validation was limited to the changed Docker configuration and startup behavior;
the financial and application code did not change.

### Local Python 3.12 environment — November 3, 2026

Installed Homebrew Python **3.12.16** and recreated the project's `.venv` with it
to match Docker's Python 3.12 runtime. Reinstalled the editable package with both
`web` and `dev` extras, including notebook tools. The previous Python 3.9.6
environment and its dependency inventory are backed up outside the checkout at
`/private/tmp/filab-python39-backup.1LMfoS/`; this is a temporary local recovery
copy, not a durable project artifact.

Updated README setup instructions and repository guidance to use
`python3.12 -m venv .venv` explicitly. Activating `.venv` now selects Python
3.12.16. Package metadata retains its existing Python 3.9+ compatibility floor;
this change standardizes the working runtime.

All **313 tests passed** under Python 3.12.16, and `python -m pip check` found no
broken requirements. NumPy, SciPy, Matplotlib, JupyterLab, ipykernel, and ipywidgets
imported successfully; the worked bond example reproduced $981.19. A temporary
Uvicorn server passed 19 page/asset checks (including all nine lessons) and eight
API checks, including the known price and invalid-input rejection, then was
stopped. The test run emitted the same upstream Starlette/httpx deprecation
warning as the container verification. Financial calculations, lesson content,
and original notebook artifacts are unchanged.

### Docker runtime — November 3, 2026

Added a Python 3.12 slim image that installs the packaged application with its
`web` extra, includes all lesson and formula assets, runs as an unprivileged
user, and serves on container port 8000 without reload. The initial homepage
health check was subsequently removed; the image no longer polls the website.
`.dockerignore` limits uploads to installation
inputs and excludes local environments, Git history, tests, notebooks, and caches.

The image needs no runtime bind mounts or volumes. Build/run commands preserve
the selected Docker context; the README explains remote-host port publishing,
SSH tunneling, rebuilding, status/log inspection, and cleanup. This adds a runtime
option for the existing M0/M1 website; curriculum and financial conventions are
unchanged.

Initial validation on the selected `deepl` engine (`ssh://deepl.lan`, Linux/amd64),
before removal of the health check:

- `docker build --tag fixed-income-lab:local .` succeeded, uploading a 1.715 MB
  context from the macOS/arm64 client. No source bind mounts or volumes were used.
- All **313 tests passed locally** and **313 passed inside the container** against
  the installed package as the unprivileged user. Tests were copied with
  `docker cp`; only the disposable verification container received `pytest` and
  `httpx`. The runtime image excludes test and notebook dependencies.
- HTTP checks passed for 19 pages/assets (all nine lessons, overview, standalone
  tool, API docs/schema, and bundled scripts/styles/fonts) plus eight API checks,
  including a known price and invalid-input rejection. Resources resolved from
  the installed package. Docker reported the container healthy.
- A fresh container with `--network none` served 17 lesson/tool/asset URLs and
  seven numerical APIs successfully and became healthy. A client HTTP request
  through an SSH tunnel to the remote published port returned 200.
- Temporary containers and the tunnel were stopped after verification. The
  `fixed-income-lab:local` image remains available on the remote engine.

The client currently falls back to the legacy Docker builder and emits its
deprecation notice because Buildx is absent. The container test run also emitted
one upstream Starlette/httpx test-client deprecation warning; all checks passed.
Dependencies remain unlocked under the existing `pyproject.toml` policy. No UI
or financial calculation changes were made, so no new visual or reference-price
benchmark review was required.

### Lesson clarity review — November 3, 2026

Reviewed and revised all nine canonical website lessons, and reviewed the optional
Python supplement plus the original notes and notebook. Added explicit learning
goals, definitions before formulas, guided experiments, and worked steps for YTM,
settlement, payment weights, and risk approximations. Foundation exercises now
use the existing keyboard-accessible answer reveals. Reordered the effective
annual rate discussion before the final checkpoint, clarified units and negative
yield boundaries, corrected the Treasury bill appendix reference, and replaced
outdated phase wording with M0/M1 navigation.

All **313 tests passed**. Independent arithmetic checks reproduced lesson prices,
yield solutions, dated settlement, bill quotations, and duration/convexity examples.
Browser checks on all nine lessons at **1440×900 and 390×900** covered formulas,
page/reading-panel width, keyboard answer reveals, optional code, live results,
and YTM input/reset. No formula-rendering or browser console errors were observed.
The existing local server was reused. Original learning artifacts remain preserved;
learner reflection is still pending. See [the review record](notes/lesson_content_review.md).

### Lessons and experiments

| Lesson | URL | Available experiments |
|---|---|---|
| 1. Bond Basics | `/lessons/bond-basics` | Coupon and principal cash-flow timelines |
| 2. Present Value & Bond Pricing | `/lessons/present-value` | Discounted payments, compounding conventions, and reinvestment comparisons |
| 3. Bond Pricing Lab | `/lessons/bond-pricing-lab` | Maturity, coupon, and payment-timing comparisons; exact yield-shock repricing |
| 4. Yield to Maturity | `/lessons/yield-to-maturity` | Solve yield from price; compare coupon rate, current yield, and YTM |
| 5. Settlement & Accrued Interest | `/lessons/settlement-and-accrued-interest` | Actual settlement dates, clean/dirty prices, dated YTM solving, and pull-to-par |
| 6. Treasury Bill Yields | `/lessons/treasury-bill-yields` | Discount quotations, investment yields, and the half-year convention change |
| 7. Cash-flow timing & duration | `/lessons/macaulay-duration` | Present-value weights, zero/coupon comparisons, Macaulay duration |
| 8. Modified duration & DV01 | `/lessons/modified-duration-dv01` | Yield sensitivity, face scaling, dated numerical checks |
| 9. Convexity & approximation error | `/lessons/convexity` | Exact vs first/second-order repricing and signed shock errors |
| 10. Coupons, accrual & return | `/lessons/coupons-and-return` | Simple return and dirty-price accounting across a coupon date |
| 11. Pull-to-par & maturity | `/lessons/pull-to-par` | Fixed-YTM discount/premium convergence and final redemption |
| 12. Reinvestment & cash | `/lessons/reinvestment-and-cash` | Zero-interest/explicit cash and the two-period ledger |
| 13. Holding-period return & early sale | `/lessons/holding-period-returns` | Integrated early sale, costs, and keeping versus selling |
| 14. Par yields & security quotes | `/lessons/par-yields-and-quotes` | Published curves, 2s10s, and comparable observations |
| 15. Observation, publication & retrieval | `/lessons/observation-and-publication` | Observation dates and acquisition evidence |
| 16. Revisions & vintages | `/lessons/revisions-and-vintages` | Published observations versus a hypothetical revision |

Each lesson has an overview card, sidebar entry, and previous/next navigation.
Python examples are optional and collapsed. Original notes and Notebook 01
remain preserved; website Markdown is the source for lesson content.

### Financial calculations

- Regular fixed-coupon schedules, zero-coupon pricing, and coupon-bond pricing.
- Price-to-YTM root finding, including zero and negative implied yields.
- Dated regular schedules, end-of-month handling, and leap-day accrual.
- Accrued interest and clean/dirty price conversion.
- Dated YTM solving from either a clean quote or the full dirty price.
- Treasury bill actual/360 discount pricing and 365/366 investment-year bases.
- Simple short-bill annualization and the longer-bill coupon-equivalent quadratic.
- Fixed-YTM clean/dirty price paths showing coupon resets and approach to maturity.
- Closed-portfolio return accounting with coupons, redemption, sales, cash, and fees.
- Explicit effective cash growth, step-YTM scenarios, and aggregation of positions.

Pricing calculations live in `src/filab/pricing/`. FastAPI pricing endpoints are
`/api/valuation`, `/api/rates`, `/api/experiments`, `/api/yield`,
`/api/settlement`, and `/api/bills`; each accepts POST requests. API rates
are decimals, while browser controls display percentages. See `/docs` for
request and response schemas.

Return accounting lives in `src/filab/analytics/`; `/api/returns`,
`/api/return-ledger`, and `/api/return-study` expose the calculator, explicit
portfolio ledger, and complete input-snapshot validation. Risk functions remain
in `src/filab/risk/`. The [README](README.md) documents these interfaces.

### Interface decisions and recent improvements

- Place experiments and explanations side by side at desktop widths of 1200px
  and above, with independent scrolling and most of the width for the experiment.
  The header lesson picker opens on hover or click; narrower screens stack the
  sections with direct links between them. Risk charts precede detailed measures.
- Keep the desktop page within the viewport and contain positioned formula
  accessibility content inside its panel, preventing blank outer-page scrolling.
  Add Overview, Previous, Next, and the lesson position to the top bar.
- Give distinct financial concepts their own lessons; YTM is a separate page.
- Show discrete choices as visible radio option cards, rather than dropdowns.
- Order payment frequencies **Annual → Semiannual → Quarterly**, followed
  by Monthly where available. Semiannual remains the default selection.
- Display purchase-price inputs to two decimal places, with one-cent steps;
  round typed prices when committed. Preserve calculation precision elsewhere.
- Label assumptions and distinguish immediate repricing from holding-period return.
- Define a DV01 lesson yield move as a change in YTM with fixed coupons and
  principal; contrast coupon rate with YTM before deriving sensitivity.
- Explain why the Treasury bill yield formula changes at half a year:
  six months is one period in the semiannual coupon-bond benchmark.
  Lesson 6 includes the two growth formulas, a numerical comparison,
  an explanation beside the chart, and a dotted half-year marker.

## Validation and model limits

The latest M3 test run on November 7, 2026 passed **486 tests**. Coverage includes historical data/snapshot checks, focused lesson boundaries, returns,
cash/position accounting, published horizon scenarios, and the existing pricing
identities, yield round trips, dated settlement, coupon boundaries, leap
years, bill conventions, API validation, and lesson navigation.

Independent checks use published Treasury examples for regular and reopened
bond prices, accrued interest, and short/long bill quotations. QuantLib is
not required. Details, source links, and tolerances are recorded in
[Phase 1 validation](notes/phase_1_validation.md).

Previously recorded desktop/mobile browser checks covered the six lessons, visible choices,
calculations, disabled states, resets, keyboard navigation, and layout.
The payment-option reorder was checked in rendered HTML; the latest bill
explanation, formulas, and half-year marker were also checked in the browser.

The earlier planning audit used source/tests only. The subsequent M1 implementation
was verified in a browser at desktop and 390-pixel mobile widths: calculations,
face scaling, dated mode, invalid dates, export/import, reset, keyboard radio and
chart controls, mobile navigation, and rendered formulas. No browser console errors
were observed. Mobile pages stayed within viewport width. Temporary verification
servers are stopped after checks; normal use still requires starting the server.

The November 2 lesson layout update passed all **313 tests** and browser checks
on all nine lessons at 1440, 1200, 1024, and 390-pixel widths. Checks covered
independent reading scroll, graph width, formulas, course navigation and Escape,
keyboard radio selection, recalculation/reset, section links, optional Python,
and the overview/standalone tool. No horizontal page overflow or browser console
errors were observed. The existing local server was reused.

Follow-up browser checks covered all nine lessons at 1440×900, 1200×600,
390×844, and 320×640: desktop document height matches the viewport, wheel and
section-link navigation cannot scroll the outer page, both panels still reach
their final content, and mobile retains normal page scrolling. Header links,
first/last lesson destinations, keyboard activation, and expanded Python examples
were checked. The existing desktop/mobile interaction checks and 313 tests passed.

Dated bonds use Actual/Actual coupon-period accrual and simple discounting
over the first fractional period, followed by compound full periods.
Settlement on a coupon date is after payment. The issue/accrual start date
must lie on the regular maturity-anchored coupon grid.

Stub coupons, holiday adjustments, ex-coupon rules, market settlement lags,
and auction-specific intermediate rounding are outside this model. The bill
investment-year basis is an explicit input. Historical Treasury par observations are now available; discount-curve valuation
remains in M4.

## Running the project

From the project root, using the existing Python 3.12 environment:

```bash
source .venv/bin/activate
python --version  # Expect Python 3.12.x.
python -m uvicorn filab.web.app:app --host 127.0.0.1 --port 8000
```

Open [the local website](http://127.0.0.1:8000). Reuse an existing server if
available; otherwise start one with the command above. Stop it with Ctrl+C
when finished; restart it after Python code changes.

Alternatively, build `fixed-income-lab:local` with the root `Dockerfile` and run
it on the selected Docker engine. With the current remote `deepl` context, the
published port is on `deepl.lan`; an SSH tunnel makes it available to the client.
See [Run with Docker](README.md#run-with-docker) for complete commands, port
choices, and container lifecycle instructions.

An earlier high-CPU issue came from bare `--reload` recursively polling the
project, including approximately 5,947 Python files in `.venv`. The watcher
and an extra test server were stopped. Normal startup now omits reload.
For development, restrict automatic reload to application source:

```bash
python -m uvicorn filab.web.app:app --reload --reload-dir src/filab --reload-delay 1 --host 127.0.0.1 --port 8000
```

Run the numerical and web tests with:

```bash
python -m pytest -q
```

## M1 delivered

- Independent `filab.risk` functions for regular-period analytical Macaulay/modified
  duration and convexity; dollar duration and positive-magnitude DV01.
- Numerical dated dirty-price sensitivity using the existing settlement convention,
  with explicit exclusion of a textbook Macaulay conversion between coupons.
- `/tools/bond-risk`, `/api/risk`, and `/api/risk-study`: two-bond comparisons,
  exact shocks, approximation errors, PV weights, bump diagnostics, and versioned
  complete-input export/import. Invalid or stale inputs cannot be exported.
- Three separate lessons with prediction prompts, worked examples, derivations,
  collapsed transfer answers, and reflection questions.
- Shared control templates and a curriculum registry; milestone-based website
  roadmap replaces the 12-week promise.
- [Validation record](notes/m1_validation.md) and an unanswered
  [learner journal](notes/m1_learning_journal.md). Software completion is recorded;
  the learner's reflection and transfer exercises remain pending.

## Next milestone

Build **M4: Discount curves**, beginning with the Fed source/short-end feasibility
gate described in [M3 validation](notes/m3_validation.md). Complete the learner's
M1, M2, and M3 reflection independently; software checks do not answer the journals.

## Revised roadmap and planning audit

| Milestone | Deliverable | Status |
|---|---|---|
| M0 Foundations | Existing six lessons and pricing | Software/reference checks complete; learner checkpoint unverified |
| M1 Interest-rate risk | Duration, convexity, risk explorer | Software validated; learner checkpoint pending |
| M2 Return accounting | Deterministic cash/position ledger and return calculator | Software validated; learner checkpoint pending |
| M3 Historical observations | Versioned data and curve history viewer | Software validated; learner checkpoint pending |
| M4 Discount curves | Curve valuation and validated historical adapter | Next; short-end feasibility gate open |
| M5 Strategy research | Two synthetic Treasury strategies, saved runs, exports | Planned; first historical research release |
| M6 Robustness | Horizon analysis, curve scenarios, key-rate risk | Planned |
| M7 Daily use | Research desk, reproducibility, backup/recovery | Planned |

The roadmap has distinct learning, educational-site, and workbench acceptance
criteria. M1 comparison inputs and M2 return ledgers/input snapshots are implemented;
M3 observations/snapshots are delivered; saved historical research studies and
strategy modules remain future work. The 108–170 hour
budget in the plan was the provisional pre-M1 estimate, not recorded time spent.
The post-M3 review allows 72–116 focused hours for M4–M7, provisionally until
the Fed adapter and short-end feasibility gate are validated.

The [original plan](notes/fixed_income_lab_plan_original_2026-11-01.md) is preserved
with its detailed credit curriculum and advanced research topics. These remain
extensions. Hosting, accounts, broker execution, and real-time quotes remain deferred.

The planning audit passed the original 221 tests. M1 adds 92 cases, including
closed-form risk identities, CME price-bump arithmetic, convergence, dated
boundaries, API parity, complete configuration validation, and lesson integration.
See the M1 validation record for sources, tolerances, and remaining limitations.

The [project plan](fixed_income_lab_plan.md) contains the full curriculum;
the [README](README.md) contains setup and interface details.
