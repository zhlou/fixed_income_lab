# Repository Guidelines

## Purpose and Working Approach

This is both a fixed-income learning environment and a local interactive website. Financial understanding is the goal; Python implementation is supplementary. Read `fixed_income_lab_plan.md`, `PROJECT_STATUS.md`, and relevant code before extending a module. Confirm actual implementation rather than treating roadmap directories as existing features.

For learning questions, explain the intuition and conventions before introducing equations. For development requests, deliver the calculation, lesson, experiment, and appropriate validation together. Distinguish software completion from the learner completing reflection questions.

## Project Structure

- `src/filab/pricing/`: reusable financial calculations; keep these independent of HTTP and templates.
- `src/filab/web/app.py`: FastAPI routes, request validation, and numerical APIs.
- `src/filab/web/content/`: canonical website lesson Markdown.
- `src/filab/web/templates/` and `static/`: Jinja layouts, JavaScript, CSS, SVG, and bundled KaTeX.
- `tests/`: pytest financial and API tests.
- `notes/`, `notebooks/`: reference material and validation records; preserve original learning artifacts.

## Lesson and Curriculum Design

Give distinct financial concepts their own lesson pages, with overview cards, sidebar entries, and previous/next navigation. Include intuition, defined symbols, a derivation, a reproducible numerical example, an interactive experiment, misconceptions, and reflection questions. Keep Python examples optional and collapsed.

Explain why a convention or formula changes, including its boundary behavior. Connect charts to cash flows and numerical tables. Label hypothetical scenarios, empirical observations, identities, and forecasts separately. Never present immediate price changes as holding-period returns.

## Financial Conventions and Research

Keep financial calculations in Python. API rates are decimals; controls display percentages. State face-value units, compounding frequency, settlement assumptions, and day counts. Display prices to cents and commit purchase-price inputs in one-cent increments; retain intermediate calculation precision.

Preserve existing interfaces and model conventions unless explicitly extending them. Dated pricing currently uses regular maturity-anchored coupons, Actual/Actual coupon-period accrual, and simple first-fractional-period discounting. Coupon-date settlement is after payment. Stub coupons, holidays, ex-coupon rules, and settlement lags are excluded; do not imply otherwise.

Use authoritative financial references and record sources and tolerances for benchmark calculations. Implement core mathematics before using reference libraries. Future market-data work must preserve raw observations, acquisition metadata, missing values, and rate types; par yields are not spot rates. Avoid look-ahead bias and label synthetic prices.

## Web Implementation and Accessibility

Use FastAPI/Jinja, plain JavaScript/SVG, Markdown, and local KaTeX. Resolve resources relative to the package. Keep the website usable offline after installation; avoid unnecessary frameworks, CDNs, accounts, or hosting work.

Use visible radio option cards instead of dropdowns. Order frequencies Annual → Semiannual → Quarterly → Monthly where available; preserve the semiannual default. Support keyboard navigation, readable mobile layouts, clear selected/disabled states, input errors, resets, and stale-response protection. Keep implementation details out of financial learning controls.

## Development Commands and Runtime

Use Python 3.12 for the local environment to match the Docker runtime. Package
metadata continues to permit Python 3.9+.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python --version  # Expect Python 3.12.x.
python -m pip install -e '.[web,dev]'
python -m uvicorn filab.web.app:app --host 127.0.0.1 --port 8000
python -m pytest -q
```

The site runs on port 8000; API documentation is at `/docs`. Reuse an existing server and stop temporary servers after verification. Normal startup omits reload. For development, add `--reload --reload-dir src/filab --reload-delay 1`; bare `--reload` previously caused high CPU by polling `.venv`. Restart after Python changes when reload is disabled.

## Style and Validation

Use four-space Python indentation, `snake_case` functions/modules, and `PascalCase` classes. Document assumptions in public functions. Preserve surrounding JavaScript/CSS/template formatting. No formatter, linter, or coverage threshold is configured.

Name tests `tests/test_*.py` and functions `test_*`. Test financial identities, independent examples, meaningful boundaries, invalid inputs, and API parity. Use `pytest.approx` with justified tolerances. Install both extras so web tests run. For UI changes, verify desktop/mobile behavior, keyboard controls, formulas, and console errors. Documentation-only changes need targeted checks rather than new tests.

## Documentation, Commits, and Handoffs

Update the README for interface/setup changes, the plan for curriculum changes, and `PROJECT_STATUS.md` for milestone progress. Record financial reference validation in `notes/phase_1_validation.md`; report checks actually performed and remaining limitations.

There is no established commit-message convention beyond the initial commit; use concise imperative subjects. PRs should explain resulting behavior, validation, related issues, and material assumptions, with screenshots for visual changes. Exclude environments, caches, build outputs, credentials, and generated package metadata from commits.
