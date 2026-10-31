# Fixed-Income Lab

A local, interactive learning website for fixed-income mathematics. Each
lesson combines a working experiment, an explanation, and optional Python
examples. The Python backend uses the existing tested `filab.pricing` package.

## Start the website

From the project root (currently `/Users/zhlou/Work/fixed_income_lab`):

```bash
python3 -m venv .venv  # Only when creating a new environment.
source .venv/bin/activate
python -m pip install -e '.[web,dev]'
python -m uvicorn filab.web.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. Python 3.9 or newer is required. If port
8000 is in use, choose another with `--port`. Stop the server with Ctrl+C.
JupyterLab and Node.js are not required to run the website. The `web` extra
alone is sufficient for website use; `dev` adds tests and the original
notebook tools.

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

## Lessons

| Page | What to explore |
|---|---|
| `/lessons/bond-basics` | Coupon and principal cash-flow timelines |
| `/lessons/present-value` | Present value and bond pricing: discounting, rate conventions, and reinvestment |
| `/lessons/bond-pricing-lab` | Maturity, coupon, and payment-timing comparisons |
| `/lessons/yield-to-maturity` | Price-to-YTM solving and coupon/current-yield comparisons |
| `/lessons/settlement-and-accrued-interest` | Dated pricing, accrued interest, clean/dirty YTM, and pull-to-par |
| `/lessons/treasury-bill-yields` | Bank discount and coupon-equivalent yield conventions |

The six-lesson sequence is **Bond Basics → Present Value and Bond Pricing
→ Bond Pricing Lab → Yield to Maturity → Settlement and Accrued Interest
→ Treasury Bill Yields**. Lesson 2 includes optional Python examples in a collapsed
“Under the hood” section. Implementation is supplementary, not a separate
required lesson. The former implementation page redirects to that section.

Use the course sidebar and previous/next links to move between lessons.
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

## Project layout

```text
src/filab/pricing/          Reusable pricing calculations
src/filab/web/app.py        Lesson routes and numerical API
src/filab/web/content/      Website lesson Markdown
src/filab/web/templates/    Shared page templates
src/filab/web/static/       CSS, JavaScript, SVG and vendored KaTeX
tests/                     Pricing and website tests
notes/                     Preserved original definitions and derivations
notebooks/                 Preserved original learning experiments
```

The website Markdown is the source for website lessons. Original notes and
Notebook 01 remain available as reference artifacts. The [12-week project
plan](fixed_income_lab_plan.md) defines future lesson modules and labs.
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
sources, tolerances, and model limits. Phase 1 software is complete; the
next implementation milestone is duration and convexity.

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
