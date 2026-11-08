# Fixed-Income Lab

A local, interactive learning website for fixed-income mathematics, growing
toward a reproducible workbench for bond strategies and historical returns. Each
lesson combines a working experiment, an explanation, and optional Python
examples. The Python backend uses tested `filab.pricing`, `filab.risk`, and
`filab.analytics` calculations.

## Start the website

Use Python 3.12 locally to match the Docker runtime. On macOS with Homebrew,
install it with `brew install python@3.12`; see the
[Homebrew formula](https://formulae.brew.sh/formula/python@3.12).

From the project root (currently `/Users/zhlou/Work/fixed_income_lab`):

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
works offline afterward. Dependency versions follow `pyproject.toml` and are not
locked, so a fresh build can pick up newer compatible releases.

The Dockerfile uses pip 26.2 or newer and its
[`--only-deps` option](https://pip.pypa.io/en/stable/user_guide/#installing-only-dependencies)
to install the dependencies of `.[web,build]` before copying README and source. The
`build` extra in `pyproject.toml` declares the tools needed for the later
application build without isolation. An empty README satisfies the metadata-only
dependency step; the real README is copied before building the application wheel
so its package description is preserved. Source and README changes reuse the
dependency layer; only the application package is rebuilt. Changing
`pyproject.toml` invalidates that layer. To refresh allowed dependency versions
explicitly, rebuild with `docker build --no-cache`.

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
For the currently configured `deepl` context at `ssh://deepl.lan`, open an SSH
tunnel from the client in a separate terminal:

```bash
ssh -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:18000:127.0.0.1:8000 deepl.lan
```

Open [the container website](http://127.0.0.1:18000) or
[its API documentation](http://127.0.0.1:18000/docs) on the client. Replace
`deepl.lan` with the engine's SSH destination if the context changes. Port 18000
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

The current Docker client builds successfully with the legacy builder and emits
a deprecation warning because Buildx is not installed. This Dockerfile also works
with BuildKit; it does not require builder-specific features.

## Lessons

| Page | What to explore |
|---|---|
| `/lessons/bond-basics` | Coupon and principal cash-flow timelines |
| `/lessons/present-value` | Present value and bond pricing: discounting, rate conventions, and reinvestment |
| `/lessons/bond-pricing-lab` | Maturity, coupon, and payment-timing comparisons |
| `/lessons/yield-to-maturity` | Price-to-YTM solving and coupon/current-yield comparisons |
| `/lessons/settlement-and-accrued-interest` | Dated pricing, accrued interest, clean/dirty YTM, and pull-to-par |
| `/lessons/treasury-bill-yields` | Bank discount and coupon-equivalent yield conventions |
| `/lessons/macaulay-duration` | Present-value weights and average payment time |
| `/lessons/modified-duration-dv01` | Percentage sensitivity, dollar duration, and DV01 |
| `/lessons/convexity` | Exact repricing, curvature, and approximation error |
| `/tools/bond-risk` | Reusable two-bond risk comparison with JSON export/import |
| `/lessons/coupons-and-return` | Simple period return and dirty-price accounting across a coupon date |
| `/lessons/pull-to-par` | Fixed-YTM price convergence and final redemption |
| `/lessons/reinvestment-and-cash` | Explicit cash growth and the two-period ledger |
| `/lessons/holding-period-returns` | Integrated early-sale return, costs, and keeping versus selling |
| `/tools/bond-return` | One/two-position return calculator with input and ledger exports |
| `/lessons/par-yields-and-quotes` | Constant-maturity observations, spreads, and comparable samples |
| `/lessons/observation-and-publication` | Observation, publication, and retrieval timing |
| `/lessons/revisions-and-vintages` | Immutable evidence and hypothetical revisions |
| `/tools/treasury-history` | Cached historical curves, explicit refresh, and source evidence |

The six foundations lessons are **Bond Basics → Present Value and Bond Pricing
→ Bond Pricing Lab → Yield to Maturity → Settlement and Accrued Interest
→ Treasury Bill Yields**. Lesson 2 includes optional Python examples in a collapsed
“Under the hood” section. Implementation is supplementary, not a separate
required lesson. The former implementation page redirects to that section.
M1 adds three lessons: **Cash-flow timing & duration → Modified duration & DV01
→ Convexity & approximation error**. Each has prediction prompts, a derivation,
a worked example, reflection questions, and a transfer exercise with a collapsed
answer. The shared Risk Explorer is also available outside the lesson sequence.
M2 adds **Coupons, accrual & return → Pull-to-par & maturity → Reinvestment
& cash → Holding-period return & early sale**, bringing the M0–M2 total to thirteen lessons.
The first page introduces a simple return; the final page combines the pieces
with exit-yield changes and trading costs. Existing lesson URLs are preserved.
Their focused experiments share the same return ledger, which processes every
payment before measuring wealth. The complete calculator has its own tool page.

On desktop windows at least 1200 pixels wide, lessons place the experiment on the
left and the explanation on the right. Each side scrolls independently, so the
chart stays in place while you read. The experiment receives most of the width.
Hover over **Lesson 08 of 16 ▾** in the header to jump to any lesson, grouped under
Foundations, Risk, Returns, and History. Wide screens show those four groups
left to right; medium screens use two columns and phones use one.
Click to keep the picker open, or use Enter/Space
and Tab by keyboard. Escape closes it. On phones, tap the compact **08 / 16 ▾**
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
the calculations. `POST /api/yield` solves for annual nominal YTM given
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

The first four lessons assume regular periods immediately after a coupon payment.
Coupon and compounding frequencies match, accrued interest is zero, and
coupon maturities must contain a whole number of periods. The generic
zero-coupon pricer also supports fractional periods. Lesson 5 adds actual settlement dates and accrued interest; Lesson 6 adds
Treasury bill discount quotations. Market discount curves remain future work.
Dated bonds use Actual/Actual coupon-period accrual and Treasury-style simple
discounting over the first fractional period. Dates are unadjusted and issue
must be on the regular maturity-anchored grid; stub coupons, holidays,
ex-coupon rules, and market settlement lags are excluded. On a coupon date,
settlement is after payment. Bill yields use the selected 365/366 basis and
the coupon-equivalent quadratic beyond half a year. Input ranges are bounded
for the website; original pricing interfaces remain available.

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

M2 lessons use focused controls and related examples, with the remaining
assumptions stated explicitly:

| Lesson | Adjustable controls | Chart emphasis |
|---|---|---|
| 10. Coupons, accrual & return | Nearby purchase/valuation dates, coupon rate | Coupon-date transfer from bond value to cash |
| 11. Pull-to-par & maturity | Coupon, purchase YTM, maturity or day-before-maturity horizon | Clean/dirty price convergence at fixed YTM and final redemption |
| 12. Reinvestment & cash | Cash rate, coupon rate, reporting horizon | Extra wealth relative to cash at 0% |
| 13. Holding-period return & early sale | Exit YTM, trading cost, mark/sell | Dirty price change versus investment return |

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
object for the four M2 lesson slugs. The lesson controls are listed in the table
above; Python supplies the fixed assumptions and calls the shared ledger.
For example, lesson 13 at `/api/lesson-returns/holding-period-returns` accepts
`{"example":"yield-rise","controls":{"end_yield":0.07,"cost_bp":10}}`.
Lesson dates are constrained to its teaching window; unrelated controls and
examples are rejected. The response contains complete transferable `inputs`,
the shared `result`, and lesson-specific metrics, curves, and numerical rows.
Rates remain decimal fractions. Existing full-calculator APIs and their bounds
are preserved. For compatibility, the pull-to-par API still accepts its former
`early-sale` example, `early_sale` horizon, and `end_yield`; the lesson page
offers fixed-yield scenarios, with early exits taught in lesson 13.

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
implemented. M3 adds three lessons for sixteen total. Discount curves (M4) are
next, followed by the first two-strategy research release. Saved research studies
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
can still be opened with `python -m jupyterlab`. Its optional Node.js tools
are installed under this user's `~/.local/`; Bash PATH setup is in
`~/.bash_profile`. These are independent of the website runtime.

## Bundled software

KaTeX 0.16.22 is vendored under `src/filab/web/static/vendor/katex/`,
including its MIT license and fonts. JavaScript handles presentation;
financial calculations run on the local Python server.

## Treasury history (M3)

Open `/tools/treasury-history` to compare nominal constant-maturity **par yields**
on two exact dates. A fresh installation opens bundled October–November 2026
history: **21 October rows and five November rows (November 2–6)**, with
coverage October 1 through November 7. The default
November 5/6 comparison reproduces a 2s10s spread of **38 bp → 35 bp** (−3 bp).
This starter dataset works offline. November 7 has no row; later dates remain
outside coverage until acquired. Opening the page makes no Treasury request.

A second bundled sample covers February 1–28, 2025, with 19 published dates.
Lesson 14's **Series introduction** option uses February 14/18 to explain the
missing 1.5-month tenor. Its original snapshot ID and +5 bp benchmark remain
available. Lesson reset restores the frozen recent November example. The standalone
viewer opens the active cached history and offers both lesson samples through
its saved-dataset radio cards; reset restores the November dates on that history.
Lessons 14–16 explain rate types and comparable observations, information timing,
and vintages. Lesson 14 includes the missing-observations checkpoint. The source
observations are annual percentages; numerical API rates are decimals and
differences have explicit basis-point units.

Use **Load or refresh selected years** for an inclusive range from 1990 through
the current year. The default is the last completed calendar year. That
button fetches Treasury's annual XML feed and can check saved years for revisions. A current year is covered only through
the retrieval date. Coverage means the requested period, not a guarantee of a
row on every date. Missing dates and tenors remain absent, and the UI never
silently selects a nearby date. The chart's lines only connect published nodes.

Each date field has a calendar annotated from the **selected snapshot**:
**● Published row**, **— No published row** inside its coverage, and **? Outside
cached coverage**. Dates without data stay selectable. A published row may still
lack individual tenors. You can also type a real date as `YYYY-MM-DD`; the status
updates immediately, before you press Compare. Invalid dates such as February
30 are rejected. In the viewer and lessons 14–16, **opening or changing the
calendar month**, or typing a valid date, loads the selected month through a
same-origin Python endpoint. The browser never calls Treasury directly.
Requests are debounced and serialized; rapid navigation discards obsolete UI
responses. Complete historical months are reused. The current month is checked
at most hourly after successful acquisition; **Retry month** explicitly retries
failures. Future months and dates before 1990 make no Treasury request.

The calendar updates when data arrives. **Compare dates** explicitly calculates
against the resulting snapshot; the previous curves and their source ID remain
visible until then. Failed requests keep cached dates and show a retry option.
Cached coverage never extends to days that were not acquired. Successful empty
monthly feeds mean no published rows inside the acquired period; an invalid or
failed response does not establish that coverage.

Lessons 14–16 start from their pinned sample. Opening a lesson, opening its
pinned month, and **Reset example** work offline without checking Treasury.
Exploring other months enables the same automatic loader as the full viewer.
A visible notice distinguishes exploration from the worked example in the text;
Reset restores the original November dates, dataset, Log axis, and published
revision setting. Lesson 14 also retains its separate February worked example.
Lesson 16's hypothetical +10 bp description follows the selected second date and
its actual ten-year yield; missing rows or tenors cannot be revised. The API
supplies both original and hypothetical rates, keeping the arithmetic in Python.

The calendar supports arrow keys for days, Home/End for the week, Page Up/Down
for months, Shift + Page Up/Down for years, and Escape to close and return focus.
Month changes clamp the day to the target month (January 31 → February 28, or 29
in a leap year). On smaller screens the dialog scrolls vertically when needed.

The maturity axis defaults to **Log**, with a visible **Linear** option. Log
spacing gives the short tenors room: equal maturity ratios occupy equal
horizontal distances (for example, 1→2 years and 5→10 years). Linear spacing
shows equal additional years. The yield axis stays linear, and changing maturity
spacing preserves every rate, spread, table value, and missing-data gap. Tick
labels use familiar month/year maturities and adapt to screen width. Reset
restores the example dates and Log spacing.

The refresh runs in the background with progress and duplicate-submission
protection. All selected years must parse and validate before a single atomic
catalog transaction activates the candidate. A failed or interrupted refresh
leaves the previous snapshot active; raw responses already acquired are retained.
Previously cached years outside the selected range remain in the candidate.
Identical normalized values and coverage reuse a snapshot even when raw feed
metadata changes. Different values or coverage create a new immutable version.
Choose old versions with the saved-dataset radio cards. Completing a refresh
does not switch your open comparison; use **Open refreshed snapshot** explicitly.

The runtime store defaults to `~/.local/share/fixed-income-lab/`. Override it by
setting `FILAB_DATA_DIR` to an absolute writable directory before starting the
server. It contains `raw/<sha256>.xml` exact response files and
`catalog.sqlite3` with immutable normalized snapshot JSON, acquisition metadata,
the active pointer, and the latest successful normalized month checks. Raw files include generation timestamps exactly as
received; these are not treated as historical release times. Snapshot IDs use
SHA-256 over normalized numerical observations, coverage, and normalizer version.
Every snapshot retains the original source percentages and source references.
Successful duplicate retrievals are logged separately without rewriting snapshots.
Download a selected normalized snapshot from the viewer; for a complete backup,
stop the server and copy the entire runtime store, including its raw directory.
Both pinned examples remain packaged and readable even if that directory is
absent or read-only. Additional downloaded history belongs to the configured
runtime cache; the bundled examples are not the entire Treasury archive. No runtime database belongs in Git.

The local refresh-job status is transient and intended for the default single
Uvicorn process. If the server restarts, reopen saved datasets and retry the
refresh. Completed snapshots persist; unfinished candidates never activate.
A POSIX file lock also prevents concurrent cache writers on macOS and Linux.
There is no scheduled polling, account, or market-data credential.

For Docker persistence, use an engine-host named volume (also valid with the
remote `deepl` context). Docker initializes a new volume with the image's
unprivileged user's home permissions:

```bash
docker volume create fixed-income-lab-data
docker run --detach --name fixed-income-lab \
  --publish 127.0.0.1:8000:8000 \
  --env FILAB_DATA_DIR=/home/filab/.local/share/fixed-income-lab \
  --mount source=fixed-income-lab-data,target=/home/filab \
  fixed-income-lab:local
```

Use this command when creating the container, with the existing container stopped
and removed as described above. A host bind mount must be writable by the
container's `filab` user. The volume is optional for the bundled offline example;
without persistence, removing a container discards its downloaded history.

Read interfaces:

| Endpoint | Purpose |
|---|---|
| `GET /api/history/snapshots` | Active/viewer/recent/reference IDs, example date defaults, labeled saved coverage, latest observations, recent acquisitions |
| `GET /api/history/snapshots/{snapshot_id}` | Complete immutable normalized dataset and provenance |
| `GET /api/history/snapshots/{snapshot_id}/dates` | Snapshot ID, coverage intervals, and sorted published row dates for the calendars |
| `GET /api/history/compare?snapshot_id=…&first=YYYY-MM-DD&second=YYYY-MM-DD` | Exact-date curves, tenor changes, spreads, common sample, missing counts, source metadata |
| `POST /api/history/month-load` | Load an integer `year`/`month` onto `base_snapshot_id`; optional `force` bypasses the cache; returns a job ID |
| `GET /api/history/jobs/{job_id}` | Month job state, warning, cache-hit flag, and completed snapshot ID |
| `POST /api/history/refresh` | Start an explicit refresh with integer `start_year` and `end_year`; returns a job ID |
| `GET /api/history/refresh/{job_id}` | Running/complete/failed status, progress, completed snapshot ID |

Comparison requests require a snapshot ID. Missing observations return JSON null;
`date_states` distinguishes `published`, `no_published_row`, and
`outside_coverage`. The optional `hypothetical_revision=true` comparison flag
adds 10 bp to the second date's ten-year rate in memory for lesson 16 and labels
the response `hypothetical`; it never writes to the source snapshot. Each
comparison includes `revision_scenario` with its date, +10 bp assumption, original
and proposed decimal rates/percentage strings, and whether it was applied. Neither
these observations nor the spread comparison provide security prices or returns.
Exact historical publication times remain unknown. See
[M3 validation and the M4 feasibility assessment](notes/m3_validation.md).

Optional calendar helper checks, using Node.js when available:

```bash
node --test tests/history_dates.test.cjs tests/history_months.test.cjs
```

Node.js is not required to run the website. These tests check strict Gregorian
dates, leap years, month/year movement, availability states, request ordering,
deduplication, cancellation, errors, and retries.
