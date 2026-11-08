# Fixed-Income Lab

Interactive lessons and tools for understanding bond payments, prices,
interest-rate risk, returns, and published Treasury yields. Start with a bond’s
payments or open the Treasury Bill Calculator, Bond Risk Explorer, Bond Return
Calculator, or Treasury History Viewer. Seven core lessons connect explanations to worked examples and
experiments. Python examples are optional.

A hosted installation gives visitors one shared website. Inputs and downloaded
Treasury datasets belong to each visitor’s browser. The same application can
also run on your computer using the instructions below.

## Start the website

Use Python 3.12 locally to match the Docker runtime. On macOS with Homebrew,
install it with `brew install python@3.12`; see the
[Homebrew formula](https://formulae.brew.sh/formula/python@3.12).

From your checkout’s project root:

```bash
python3.12 -m venv .venv  # Only when creating a new environment.
source .venv/bin/activate
python --version  # Should report Python 3.12.x.
python -m pip install -e '.[web,dev]'
python -m uvicorn filab.web.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. The local environment and Docker image use Python
3.12; package metadata still permits Python 3.9 or newer. If port 8000 is in use,
choose another with `--port`. Stop the server with Ctrl+C.
JupyterLab and Node.js are not required to run the website. The `web` extra
alone is sufficient for website use; `dev` adds tests and the original
notebook tools.

For an existing environment created with another Python version, deactivate it,
move `.venv` outside the checkout as a backup, and recreate it with the commands
above. Running `venv` over the old directory does not provide a clean dependency
reinstall. Reopen an active notebook kernel after the switch so it uses the new
interpreter.

The server stays running while you use the local website and should be
idle between requests. Stop it with Ctrl+C when finished. Restart it after
Python code changes.

For development, enable automatic Python reload only within the source tree:

```bash
python -m uvicorn filab.web.app:app --reload --reload-dir src/filab --reload-delay 1 --host 127.0.0.1 --port 8000
```

Avoid bare `--reload` from the project root: the polling reloader can scan
thousands of Python files in `.venv` repeatedly and consume CPU while idle.
The development command above watches only application source files.

## Run with Docker

The image uses Python 3.12, installs the package with its `web` dependencies,
and includes lesson Markdown, templates, JavaScript, CSS, and local KaTeX fonts.
It runs as an unprivileged user and listens on container port 8000 without reload.
The image does not configure a periodic health check; configure probes through
the hosting platform if needed. Python, Node.js, and a virtual environment are
not required on the Docker client machine. Internet access is
needed to download the base image and dependencies during the build; the website
works offline afterward. Dependency versions follow the files in `requirements/`.
A fresh build can pick up newer releases within their declared version ranges.

The dependency lists live in `requirements/base.txt`, `web.txt`, `dev.txt`, and
`build.txt`. Setuptools reads these files through `pyproject.toml`, so existing
commands such as `pip install -e '.[web,dev]'` use the same declarations.
Use PEP 508 requirement lines in those files, with optional comments and blank
lines. Setuptools reads each group directly from its file. `MANIFEST.in` includes
these files in source distributions for the supported setuptools versions.

Docker copies the base, web, and build requirement files first and installs them
in a cached layer. It copies `pyproject.toml`, the development requirements,
README, and application source afterward. Edits to package data, project metadata,
test settings, development dependencies, or source therefore reuse the installed
runtime dependencies. Changes to the base, web, or build requirement files
invalidate that layer. Keep the build tools in `requirements/build.txt` compatible
with `[build-system].requires`. To refresh allowed versions explicitly, rebuild
with `docker build --no-cache`.

From the checkout root, build and run using the **currently selected Docker
context**:

```bash
docker context show
docker context inspect --format '{{.Endpoints.docker.Host}}'
docker build --tag fixed-income-lab:local .
docker run --detach --name fixed-income-lab \
  --publish 127.0.0.1:8000:8000 \
  fixed-income-lab:local
```

The final `.` sends the local build context to the engine. `.dockerignore`
limits the upload to installation inputs, excluding the virtual environment,
Git history, notebooks, tests, caches, and local configuration. Source is copied
into the image and installed normally; no runtime bind mounts or volumes are
needed. With a remote engine, bind-mount paths refer to the **engine's filesystem**,
not this checkout on the client; see
[Docker's bind-mount documentation](https://docs.docker.com/engine/storage/bind-mounts/).
Rebuild the image and recreate the container after source changes. First-party
JavaScript and CSS URLs include content hashes, so changed assets are fetched
after an upgrade. The hashes are computed at server startup; restart the local
server after editing assets during development. The engine
chooses its own native image architecture; there is no hard-coded macOS/ARM or
Linux/x86 platform.

The published `127.0.0.1:8000` belongs to the **Docker engine host**, as described in
[Docker's port-publishing documentation](https://docs.docker.com/engine/network/port-publishing/).
For a remote Docker engine, open an SSH tunnel from your computer in a separate terminal. Replace `user@server.example` with the engine host:

```bash
ssh -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:18000:127.0.0.1:8000 user@server.example
```

Open [the container website](http://127.0.0.1:18000) or
[its API documentation](http://127.0.0.1:18000/docs) on the client. Replace
`user@server.example` with your server’s SSH destination. Port 18000
on the client avoids conflicting with a local server on port 8000; change that
first port if needed. Stop the tunnel with Ctrl+C. With a local Docker engine,
the same container command is reachable directly at
[http://127.0.0.1:8000](http://127.0.0.1:8000) without a tunnel.

Inspect container status and logs, then stop and remove it when finished:

```bash
docker ps --filter name=fixed-income-lab
docker logs fixed-income-lab
docker stop fixed-income-lab
docker rm fixed-income-lab
```

Run the build and start commands again to use updated source. If port 8000 on
the engine is occupied, change the middle port in `--publish` (for example,
`127.0.0.1:8001:8000`) and the tunnel destination port to match. Keep the
container's final port at 8000. Images and containers live on the selected
engine; no registry push or local Docker daemon is required.

The Dockerfile supports both the legacy builder and BuildKit.

## Lessons

The course has seven core lessons followed by two discount-curve lessons in one reading order. Each has a worked calculation and a focused experiment, with the core derivation in the article and one changed-input question.

| Page | Financial question |
|---|---|
| `/lessons/present-value` | What does this bond pay, and what is it worth? Switch between price from yield and yield from price. |
| `/lessons/par-yields-and-quotes` | How do you read a Treasury yield curve? Reconcile two curves and their 2s10s spread change. |
| `/lessons/modified-duration-dv01` | Which bond loses more when yields rise? Connect payment weights, duration, and dollar exposure. |
| `/lessons/convexity` | When does duration give a poor estimate? Judge both approximations against exact repricing. |
| `/lessons/settlement-and-accrued-interest` | What do you actually pay between coupon dates? Reconcile clean, accrued, and dirty prices. |
| `/lessons/reinvestment-and-cash` | What do you earn by holding to maturity? Select approach to par or coupon reinvestment. |
| `/lessons/holding-period-returns` | What do you earn if you sell early? Combine proceeds, coupons, and costs. |
| `/lessons/discount-factors` | How do you price payments at different maturities? Recover a factor from a calibration bond. |
| `/lessons/curve-roll-down` | Why can a bond change price on an unchanged curve? Reconcile remaining payments and coupon cash. |
| `/tools/discount-curves` | Inspect discount factors, payment values, and fitted Fed history. |
| `/tools/treasury-bills` | Translate bank discount quotes into price, period return, and coupon-equivalent yield. |
| `/tools/bond-risk` | Compare other bonds and dated risk, inspect numerical checks, and save inputs. |
| `/tools/bond-return` | Inspect complete cash/position ledgers and keep, sell, or combine positions. |
| `/tools/treasury-history` | Explore history, source evidence, missing-data examples, hypothetical revisions, and saved datasets. |

The core uses a continuing $100-face, 4% semiannual note. An annual-coupon example isolates reinvestment over two exact years. Python is optional and collapsed. Retired lesson URLs return 404. The former implementation URL redirects to the first lesson's optional Python section. Lesson time estimates were removed pending a measured walkthrough.

On desktop windows at least 1200 pixels wide, lessons place the experiment on the
left and the explanation on the right. Each side scrolls independently, so the
chart stays in place while you read. The experiment receives most of the width.
Hover over the lesson position in the header to choose from the same nine-lesson reading order shown on the homepage and sidebar.
The counter pads both numbers to two digits, showing **Lesson 05 of 07** on desktop and **05 of 07** on phones.

Click to keep the picker open, or use Enter/Space
and Tab by keyboard. Escape closes it. On phones, tap the compact lesson position
button to open a scrollable lesson list. **Course** opens the full navigation.
Narrower windows stack the sections with links between them. The top bar also
provides Overview, Previous, and Next; previous/next links sit at the end of the explanation.
On desktop, only the two content panels scroll, keeping the header in view.
Discrete controls use visible option cards so every choice is shown without
opening a dropdown. Use Tab and arrow keys to select an option by keyboard.
Change a control to recalculate in Python. Exact values accompany the
charts, and Python examples can be expanded in each lesson. All formula
assets are bundled locally; an internet connection is needed for initial
installation, not for using the lessons afterward.

Browser controls display percentages; JSON endpoints accept decimal rates.
`POST /api/valuation`, `POST /api/rates`, and `POST /api/experiments` expose
the calculations. Valuation also returns `ytm`, `coupon_rate`, and `current_yield` for the displayed rate comparison. `POST /api/yield` solves for annual nominal YTM given
`price`, `face_value`, `coupon_rate`, `maturity_years`, and `frequency`.
Price and face value use the same dollar units; rates are decimals. It also
returns current yield, the repriced bond, the pricing residual, and a
discounted payment table. The YTM lesson uses $100 face and compares
coupon rate, current yield, and YTM, including negative implied yields.
Its price input rounds to two decimal places and moves in one-cent increments.
`POST /api/settlement` accepts ISO issue/settlement/maturity dates, coupon,
face, and either YTM (`mode="price"`) or clean/dirty price (`mode="yield"`,
`price_type="clean"` or `"dirty"`). It returns dated payments, accrual day
counts, clean/dirty prices, YTM, and a fixed-yield price path. The website
uses $100 face and semiannual coupons.

`POST /api/bills` accepts `discount_rate`, `days_to_maturity`, `year_days`
(365 or 366), and `face_value`, returning price and convention-labeled yields.
Interactive API documentation is available at `/docs`.
Prices use the selected face value; comparison charts use $100 face.

The regular-period pricing and risk lessons assume valuation immediately after a coupon payment, with matching payment/compounding frequencies. The first lesson fixes semiannual frequency. General frequency and instrument choices remain available through the numerical APIs and the Risk Explorer.

Lesson 5 adds actual settlement dates, clean/dirty prices, and accrued interest. Dated pricing uses Actual/Actual coupon-period accrual, simple first-fractional-period discounting, regular maturity-anchored schedules, and after-payment coupon-date settlement. Stub coupons, holidays, ex-coupon rules, and settlement lags are excluded. The bill calculator makes the 365/366 investment basis explicit and uses the coupon-equivalent quadratic beyond half a year.

## Bond Risk Explorer (M1)

Open `/tools/bond-risk` to compare two hypothetical bonds at the same face value,
yield, and payment frequency. Change coupon/maturity independently. The explorer
shows Macaulay and modified duration, dollar duration, DV01, convexity, payment
weights, and exact versus approximate shocks of ±25, ±50, ±100, and ±200 bp.
Errors are signed estimates minus exact changes, in dollars and percentage points.
These are immediate repricings, not holding-period returns.

Regular mode uses analytical derivatives, checked numerically. Dated mode keeps
the existing settlement pricer, normalizes by dirty price, and uses a ±0.5 bp
central bump; the table also shows ±1 and ±0.25 bp. No textbook Macaulay conversion
is asserted for dated pricing. Dollar duration means −dP/dy per unit decimal yield;
DV01 is that positive magnitude times 0.0001. Negative yields are supported within
the bounded controls. Dates and model exclusions are displayed beside the inputs.

`POST /api/risk` accepts `mode` (`regular` or `dated`), `face_value`, decimal `ytm`,
`frequency`, `coupon_rate`, `maturity_years`, `comparison_coupon_rate`,
`comparison_maturity_years`, `issue_date`, `settlement_date`, `maturity_date`,
`comparison_maturity_date`, and integer `shock_bp`. Defaults reproduce the lessons.
Each of the two returned `bonds` contains `risk`, `cashflows`, `convergence`,
`points`, `scenarios`, and the highlighted `selected` shock.

**Export comparison** downloads JSON with `schema_version: 1`,
`kind: "filab-bond-risk"`, `conventions: "nominal-yield-risk-v1"`, and complete
`inputs`. **Import comparison** validates the complete snapshot through
`POST /api/risk-study` before restoring inputs and recalculating. Incompatible
files leave the comparison unchanged. This saves assumptions, not frozen outputs
or historical research runs. These scenario inputs are local and independent of the M3 historical-data feed.

## Bond Return Calculator (M2)

Open `/tools/bond-return`. Start with **Across a coupon**, **Hold to maturity**,
**Sell after a yield rise**, or the annual-coupon **Two-period check**. Buy from
a YTM assumption or a clean quote per $100 face, with quotes committed to cents.
Accrued interest is added before scaling to the position's face amount. Add
Bond B to aggregate two positions with the same purchase/horizon dates and cash
policy. Each position keeps its own coupon, maturity, face amount, and implied
purchase yield when using quotes.

Lessons 6–7 use focused views of the shared return ledger.

| Experiment | Adjustable controls | Chart emphasis |
|---|---|---|
| Lesson 6, Approach to par | Coupon, purchase YTM, maturity/day-before horizon | Clean/dirty price convergence and redemption |
| Lesson 6, Coupon reinvestment | Annual effective cash rate | Extra wealth relative to 0% cash on the annual-coupon example |
| Lesson 7, Sell early | Exit YTM and cost per trade | Price change and coupon-inclusive return |

At desktop widths of 1200 pixels or more, the input column and results scroll
independently. **View chart** remains beneath the controls. Short desktop windows
fit the complete plot and curve labels. The dedicated full calculator retains
all controls, grouped into expandable sections, plus four general examples and
input/ledger export and import.

On narrower screens, **Edit inputs / Results & chart** switches between the
controls and results while preserving the scenario. The input footer offers the
same one-tap return to the chart. Each lesson's relevant example buttons stay
visible above its workspace; the full tool shows all four general examples.
On smaller screens, the examples and view switch stay together while scrolling.
**Full calculator** carries the lesson's current validated inputs into
`/tools/bond-return` through a versioned scenario URL fragment, validated by
`POST /api/return-study` before restoration. Pending or invalid inputs disable
this transfer. The full tool's **Save / load** expands separately.

Choose fixed YTM or one dated change, then either keep/mark surviving bonds or
sell them at the horizon. The hypothetical step change applies on its date and
stays fixed afterward. All intervening coupons and redemptions are processed
even when the plot samples fewer dates. The chart and tables connect remaining
dirty bond value, credited cash, and total wealth.

The return is **ending wealth / beginning wealth − 1 over the entire period**,
without annualization. Opening capital includes dirty purchase amounts and
entry costs. Coupons are already in cash, so they are not added again to wealth.
One-way costs are basis points of face on each purchase/sale; a mark or principal
redemption has no trading fee. Same-date order is cash growth → coupons →
redemption → sales/costs → valuation. Opening-date purchases occur after payment
and receive no coupon on that date. There are no external flows, withdrawals,
taxes, leverage, or further bond purchases.

Cash is held at 0% by default. An optional annual **effective** cash rate uses
Actual/365 Fixed compounding and is independent of nominal bond YTM. It grows
all receipts, including sale/redemption proceeds if received before the horizon.
The comparison table changes only this cash assumption. The existing dated bond
pricing conventions and exclusions still apply. These are hypothetical scenarios,
not market observations, forecasts, or curved-term-structure roll-down estimates.

`POST /api/returns` accepts `start_date`, `end_date`, `issue_date`,
`maturity_date`, `face_value`, `coupon_rate`, `frequency`, `purchase_method`
(`yield` or `clean`), `price` (clean per $100 face), `start_yield`, `yield_path`
(`fixed` or `shock`), `shock_date`, `end_yield`, `cash_policy` (`zero` or `interest`),
`cash_rate`, `cost_bp`, and `end_treatment` (`mark` or `liquidate`). Optional
`include_comparison: true` adds `comparison_face_value`, `comparison_coupon_rate`,
`comparison_maturity_date`, and `comparison_price`. Rates are decimal fractions;
`cost_bp` is a number of basis points. Defaults match the coupon-date lesson.
The response includes `result` (ledger, valuation path, positions, wealth,
return, components, and residuals), `cash_comparison`, solved purchase yields,
complete `inputs`, and a convention version. `/docs` describes every field.

`POST /api/lesson-returns/{slug}` accepts an `example` identifier and a `controls`
object for the four original M2 experiment profiles. Those API identifiers remain supported after lesson consolidation. The lesson controls are listed in the table
above; Python supplies the fixed assumptions and calls the shared ledger.
For example, lesson 7 uses `/api/lesson-returns/holding-period-returns` with
`{"example":"yield-rise","controls":{"end_yield":0.07,"cost_bp":10}}`.
Lesson dates are constrained to its teaching window; unrelated controls and
examples are rejected. The response contains complete transferable `inputs`,
the shared `result`, and lesson-specific metrics, curves, and numerical rows.
Rates remain decimal fractions. Existing full-calculator APIs and their bounds
are preserved. For compatibility, the pull-to-par API still accepts its former
`early-sale` example, `early_sale` horizon, and `end_yield`; the lesson page
offers fixed-yield scenarios, with early exits taught in lesson 7.

`POST /api/return-ledger` exposes the domain workflow: common `start_date` and
`end_date`, `cash_rate`, `cost_bp`, `end_treatment`, optional `valuation_dates`,
and a `holdings` list. Each holding supplies a unique `label`, `face_value`,
`coupon_rate`, `issue_date`, `maturity_date`, `frequency`, dated `yields`
(`date`, `ytm`), and optional `sale_date`. Paths must begin at purchase and have
unique increasing dates within the horizon; no future backfill is allowed.

**Export inputs** saves complete assumptions under `schema_version: 1`,
`kind: "filab-bond-return"`, and `conventions: "dated-return-ledger-v1"`.
**Import inputs** validates the entire scenario through `POST /api/return-study`
before restoring it. **Export ledger** additionally saves full-precision results
and hypothetical price provenance. Invalid or stale inputs disable exports.
These files reproduce deterministic experiments; they are not immutable historical
research runs. The [M2 journal](notes/m2_learning_journal.md) provides unanswered
prompts for reconciling a ledger yourself.

## Project layout

```text
Dockerfile                 Self-contained Python web runtime on port 8000
.dockerignore              Minimal build context for local or remote engines
src/filab/pricing/          Reusable pricing calculations
src/filab/risk/             Yield derivatives and comparison scenarios
src/filab/analytics/        Cash/position event ledger and holding-period returns
src/filab/web/curriculum.py Published lessons and milestone registry
src/filab/web/app.py        Lesson routes and numerical API
src/filab/data/             Treasury source adapter, snapshots, bundled fixture
src/filab/web/content/      Website lesson Markdown
src/filab/web/templates/    Shared page templates
src/filab/web/static/       CSS, JavaScript, SVG and vendored KaTeX
tests/                     Pricing and website tests
notes/                     Preserved original definitions and derivations
notebooks/                 Preserved original learning experiments
```

The website Markdown is the source for website lessons. Original notes and
Notebook 01 remain available as reference artifacts. The [project
plan](fixed_income_lab_plan.md) evaluates the existing implementation and defines
milestones for learning, educational lessons, and a historical research workbench.
M1 duration/convexity, M2 return accounting, and M3 historical observations are
implemented. Seven core lessons are followed by M4 discount-factor and aging lessons.
M4 synthetic valuation and the fitted Fed history explorer are available. Historical
coupon-bond valuation retains an open short-maturity coverage gate ahead of M5. Saved research studies
and historical strategy returns remain planned.
The website roadmap now shows milestone availability without week-based promises.
Application resources resolve relative to the package, not the working
directory. After moving a checkout, recreate its virtual environment or
reinstall the editable package if its scripts still reference the old path.

## Validation

```bash
python -m pytest -q
```

The suite checks existing financial identities plus web routing, worked
examples, table totals, compounding equivalence, invalid inputs, and local
assets. Install `web` and `dev` to run the full suite; web tests skip when
FastAPI is absent.

YTM checks include price/yield round trips, independent one-period and
zero-coupon formulas, zero and negative yields, payment frequencies, and
invalid prices. Dated pricing, accrued interest, and bill quotation checks use published
Treasury examples. See [Phase 1 validation](notes/phase_1_validation.md) for
sources, tolerances, and model limits. M0–M3 software is complete; learner
reflection remains separate. See [M1 validation](notes/m1_validation.md),
[M2 validation](notes/m2_validation.md), [M3 validation](notes/m3_validation.md),
and the intentionally unanswered
[M1](notes/m1_learning_journal.md), [M2](notes/m2_learning_journal.md), and
[M3](notes/m3_learning_journal.md) journals.

## Original Python and notebook workflow

```python
from filab.pricing import price_coupon_bond

price = price_coupon_bond(
    face_value=1000, coupon_rate=0.04, ytm=0.05, maturity_years=2
)
print(f"${price:.2f}")  # $981.19
```

The existing [Notebook 01](notebooks/01_bond_pricing_fundamentals.ipynb)
can still be opened with `python -m jupyterlab`. Node.js is optional for the JavaScript helper tests. Install it through your preferred package manager if you want to run those checks.

## Bundled software

KaTeX 0.16.22 is vendored under `src/filab/web/static/vendor/katex/`,
including its MIT license and fonts. JavaScript handles presentation;
financial calculations run on the Python server.

## Treasury history

The Treasury History Viewer compares nominal constant-maturity **par yields** on
exact dates. Prices and bond returns require different inputs and calculations.
The application includes October–November 2026 starter history, a pinned
November 5–6 lesson example (38 → 35 bp), and the February 2025 example
(21 → 26 bp). Bundled examples work without access to Treasury.

The browser requests additional months when you navigate a calendar or type a
date. **Load or refresh selected years** requests an inclusive year range from
1990 through the current year. The browser contacts Treasury directly using its
official XML feed. This requires Treasury to allow cross-origin browser requests.
If access is blocked, offline, or unsuccessful, the period shows **No data**.
The available date’s values remain visible in a two-date comparison. Unavailable
two-date changes display dashes. A download failure never establishes that
Treasury published no row on a date. The server makes no Treasury requests.

Successful downloads are validated and normalized in Python through stateless
HTTP requests. Raw response bytes, SHA-256 hashes, browser-reported UTC retrieval
timestamps, original percentage strings, decimal rates, coverage, and immutable
snapshots are saved in IndexedDB. Complete historical months are reused. The
current month is checked at most hourly, with explicit retry available. A year
range is saved in one browser transaction only after every year validates.
Existing saved versions survive failed downloads and storage failures.

**Choose a saved dataset** reopens a version in the same browser. A completed
range download offers **Open refreshed snapshot** to switch explicitly.
**Export selected dataset** saves a versioned JSON archive including raw sources.
**Import dataset** validates and restores an archive, including on another device.
Clearing site data removes downloaded history. If browser storage is unavailable,
bundled examples remain readable. No visitor cache is shared with another browser.
An archive or stateless request is limited to 32 MB, a source response to 4 MB,
and a normalized snapshot to 15,000 rows. An archive contains at most 100 snapshots
and 500 raw responses.

The curve lesson starts from a pinned example. **Reset example** restores the original dates,
dataset, Log maturity axis, and published-observation setting. Log/Linear changes
horizontal spacing only. Source publication times remain unknown, and the
hypothetical +10 bp revision in the standalone viewer is calculated separately in Python.
Calendar buttons support keyboard navigation, typed Gregorian dates, and live
availability labels. Missing dates remain selectable.

### Migrate an existing server cache

The website now reads only bundled data from the server. Existing SQLite caches
and the `filab.data.store.SnapshotStore` Python interface remain available to local
research scripts. To transfer an old cache into browser storage, run this read-only
export command, then import its output in the viewer:

```bash
python -m filab.data.browser "$HOME/.local/share/fixed-income-lab" treasury-history.json
```

The exporter opens SQLite read-only and preserves raw files. The destination
must be a new file. Keep the original cache as a backup. `FILAB_DATA_DIR` applies
to local research scripts, while the website uses browser storage everywhere.
A public installation never exposes a pre-existing server cache.

### History interfaces

| Endpoint | Behavior |
|---|---|
| `GET /api/history/snapshots` | Bundled catalog, date defaults, current year/month |
| `GET /api/history/bundled-archive` | Bundled snapshots and raw source files |
| `GET /api/history/snapshots/{id}` | One bundled normalized snapshot |
| `GET /api/history/snapshots/{id}/dates` | Bundled coverage and published dates |
| `GET /api/history/compare` | Existing bundled comparison by snapshot ID |
| `POST /api/history/normalize` | Normalize browser-provided base64 XML onto a supplied snapshot using `year`, optional `month`, and `retrieved_at` |
| `POST /api/history/overlay` | Overlay a supplied cached month onto a supplied snapshot |
| `POST /api/history/compare` | Compare supplied `snapshot`, `first`, `second`, optional `hypothetical_revision` |
| `POST /api/history/validate-archive` | Validate a versioned snapshots/raw archive before browser import |

The former `/refresh`, `/month-load`, `/refresh/{job_id}`, and `/jobs/{job_id}`
interfaces return HTTP 410 with migration guidance. There are no server refresh
jobs or persisted visitor datasets. See `/docs` for complete request schemas.

## Prepare a shared HTTPS deployment

Build the Docker image and run one service behind your hosting platform’s HTTPS
reverse proxy. Forward traffic to container port 8000. Bind that port to loopback
if the proxy runs on the same host, using the Docker command above. Use a
host-managed certificate and redirect HTTP to HTTPS. Set an upstream request-body
limit of 32 MB and a response timeout of at least 60 seconds. Configure request
rate limits and worker concurrency for the chosen host’s capacity.

The application needs no persistent volume, Treasury credentials, scheduled
refresh, or account service. It can run with a read-only filesystem:

```bash
docker run --detach --name fixed-income-lab \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  --publish 127.0.0.1:8000:8000 fixed-income-lab:local
```

For a deployment smoke check, open the landing page and a pinned history lesson,
compare November 5–6, open two separate browser profiles, and verify that a dataset
saved in one is absent from the other. Block Treasury and verify **No data** for an
uncached date while the bundled example remains usable. Choose the host and public
URL when ready to publish.

Optional JavaScript helper checks:

```bash
node --test tests/history_dates.test.cjs tests/history_months.test.cjs
```


## Discount Curve Explorer (M4)

Open `/tools/discount-curves`. Synthetic mode recovers D(2) from a two-year
6% calibration bond, values the $100-face 4% semiannual note, and ages its
payments on an unchanged curve. Curve nodes use exact coupon-period years,
linear interpolation in log discount factors, D(0)=1, and positive factors.
Negative rates may imply factors above one. Extrapolation is rejected.

Fed history starts with the exact October 29–30, 2026 rows, plus isolated source
validation dates. Use **Download Fed CSV**, save the official file, and choose
**Import Fed CSV**. Select the saved dataset version, choose dates, and press
**Compare dates**. Imports are bounded to 24 MB and 26,000 dated rows. The
verified acquisition contains 17,058 rows and 16,668,595 bytes. Missing values
remain missing. Local imports record their import time and raw SHA-256 identity;
the original source acquisition time is unknown. Imports retain exact raw bytes
and normalized rows in browser IndexedDB. Identical bytes reuse a version;
revised bytes create another version. Export selected raw CSV transfers the
original file to another browser. An open result keeps its dataset identity.

The Fed file response inspected during implementation omitted a cross-origin
permission header, so acquisition uses a download link and file import. Python
normalization and calculations are stateless. Failed imports preserve saved
versions and results. Browser storage failure leaves the bundled example usable.
No external connection is required to reopen imported dates while the local or
installed application server is available.

Source zero and instantaneous forward rates are continuously compounded, par
rates nominal semiannual, and taus measured in years. Source yields/betas are
percent; normalized yields/betas and API rates are decimals. Curve valuation uses
Actual/365 Fixed as a Lab convention, while coupon accrual retains Actual/Actual
coupon-period accrual and after-payment settlement. The existing YTM pricer has
its own simple first-fractional-period convention. Match time and discount
conventions when comparing their prices.

Historical prices require every nonzero payment to fall in the row's supported
range, conservatively beginning at one year and ending at its published maximum.
Unsupported payments remain in the table with an unavailable PV and total price.
Zero-coupon principal can be priced within that range. Source dates whose fitted
parameters fail published-yield reproduction beyond rounding precision are also
blocked for pricing, with published observations still visible. The pinned full
file contains 16 such dates. See `notes/m4_validation.md` for the source audit,
short-end sensitivity table, and the open M5 gate.

| Interface | Behavior |
|---|---|
| `GET /api/curves/bundled` | Versioned exact-row excerpt, source evidence and date coverage |
| `POST /api/curves/normalize` | Raw official CSV body, `text/csv`; returns SHA-256 snapshot and normalized rows |
| `POST /api/curves/synthetic` | `calibration_price` in dollars and `horizon` in half-year steps from 0 to 2 |
| `POST /api/curves/compare` | Two selected rows and dates, snapshot identity, valuation date choice, 2/10-year maturity, decimal coupon rate and 0/1-month age |

Python calculations live in `filab.curves`; the Fed adapter is `filab.data.fed`.
Snapshots use version 1 and retain all 99 source numeric columns. Each normalized
row carries `date` and a `values` array in the returned `columns` order. Browser
rows are validated again for each comparison. Imported datasets belong to their
browser profile and are removed when that site's data is cleared.
