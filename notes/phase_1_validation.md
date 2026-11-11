# Phase 1 validation

The regular-bond implementation is complete; learner reflection remains a
personal checkpoint. Run all checks with `python -m pytest -q`.

## Independent references

Published examples are checked in `tests/test_settlement.py` against
[Treasury Appendix B](https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf)
and the [TreasuryDirect pricing page](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/).

| Reference | Case | Published result |
|---|---|---|
| Appendix B II.A | 8.75% coupon, 8.84% YTM; May 15, 1990–May 15, 2020 | Clean price 99.057893 / $100 |
| Appendix B II.D | 9.5% coupon, 9.54% YTM; settlement November 29, 1985; maturity November 15, 1995 | Clean 99.730918; dirty 100.098321; accrued 0.367403 / $100 |
| Appendix B I.D | 6.75% note; May 15–August 15, 2000 accrual | 16.87500 / $1,000; 2,531.25 / $150,000 |
| Appendix B VI.D.1 | 20-day bill at 7.93% discount | Price 99.559444; investment yield 8.076% |
| Appendix B VI.D.2 | 364-day bill at 7.65% discount | Price 92.265000; investment yield 8.237% |
| TreasuryDirect | $1,000, 182-day bill, 0.145% discount | Price $999.27 |

Six-decimal published prices allow half of the last printed decimal.
The short-bill example rounds intermediate ratios, so its investment yield
is compared at the final published percentage precision. Our calculations
keep full precision and round only for display.

## Additional numerical checks

- Regular-period and coupon-date dated prices agree.
- Clean + accrued equals dirty; discounted payments sum to dirty price.
- Clean- and dirty-price yield solvers round-trip positive, zero, and negative yields.
- Coupon dates reset accrual and remove the paid coupon from future payments.
- End-of-month schedules retain February 29; actual coupon days change in leap years.
- Before redemption, clean price approaches principal; dirty includes the final coupon.
- Short- and long-bill yields reconstruct redemption under their own conventions.
- Invalid dates, irregular first coupons, invalid price/rate domains, and unsupported conventions fail explicitly.

## Model boundaries

Dated bonds use regular maturity-anchored coupons, Actual/Actual coupon-period
accrual, and simple discounting for the first fractional period followed by
compound full periods. Settlement on a coupon date is after that payment.
Dates are unadjusted calendar dates. Stub coupons, holidays, ex-coupon rules,
trade-to-settlement lags, and auction-specific intermediate rounding are not
implemented. These limits are stated in Lesson 5; this is not a complete
security-level Treasury settlement engine.

The bill calculator uses actual/360 bank discount pricing and an explicit
365/366 investment-year basis. It applies the coupon-equivalent quadratic
beyond half a year. No online data or QuantLib installation is required to
repeat the published-reference checks.

## November 3, 2026 teaching review

Reopened the TreasuryDirect pricing page and linked Appendix B PDF. Bill formulas
and the published short/long examples are in **VI.D**, not V.D, in that PDF;
the lesson, reference table, and test comments now identify the correct section.
The underlying formulas and benchmark values are unchanged.

Independently recomputed the revised lesson examples before comparing with the
Python functions. The default dated bond ($100 face, 4% coupon, 5% nominal YTM,
semiannual, issue November 15, 2025, settlement August 15, 2026, maturity
November 15, 2028) gives 92/184 elapsed days, $1 accrued, dirty price
98.88297569974827 and clean price 97.88297569974827. Direct discounting of its
five payments agrees within $1e-10; displayed prices are $98.88 and $97.88.
The new bill exercise ($100 face, 4% discount, 90 days) gives $99.00 price,
1.0101% holding-period return, and 4.0965% / 4.1077% investment yield for
365 / 366 days. Price is exact to cents here; yields are checked at four decimal
places in percent. Additional arithmetic and browser checks are recorded in
[the lesson review](lesson_content_review.md).

## M1 follow-on

The pricing interfaces and conventions above remain unchanged. Duration,
convexity, numerical dated sensitivities, and yield-shock approximation checks
are documented separately in [M1 validation](m1_validation.md).

## M2 follow-on

The dated pricing conventions and original reference checks above are preserved.
The return ledger adds dirty-price cash accounting, explicit coupon eligibility,
cash growth, costs, and mark/liquidation treatment. Its independent two-period
example, nine published OTS/OCC horizon-return checks, tolerances, and model limits
are recorded in [M2 validation](m2_validation.md). This does not extend the pricing
model to stubs, holidays, ex-coupon rules, or market settlement lags.

### November 5, 2026 curriculum revision

M2 now teaches coupon accounting, fixed-YTM pull-to-par, cash reinvestment, and
integrated early-sale return in that order. The pricing model and published
reference benchmarks above are unchanged. Independently recomputed simple-return
and fixed-yield zero-coupon teaching examples, regression tolerances, and
desktop/mobile checks are recorded in [M2 validation](m2_validation.md).


## M3 observation benchmarks — November 7, 2026

The official Treasury February 2025 source response, its hash and retrieval time,
published 2y/10y benchmark values, basis-point tolerances, and missing-value
checks are recorded in [M3 validation](m3_validation.md). Existing Phase 1 pricing
benchmarks and dated-model conventions remain unchanged.


The current M3 default additionally validates the November 5/6, 2026 Treasury
par observations (38→35 bp 2s10s spread). Its raw response hash, UTC retrieval
time, partial-month coverage, and tolerances are in the recent-example section
of [M3 validation](m3_validation.md); the original February benchmark is preserved.


The October–November starter additionally checks October 30, 2026 par yields
against Treasury's published table (2y 4.56%, 10y 4.94%, spread 38 bp). Changes to
November 6 are −5/−8 bp and a −3 bp spread change. Exact source hashes, acquisition
times, monthly cache recovery, and the same decimal-rate tolerance are recorded
in the automatic-month section of [M3 validation](m3_validation.md).


Lesson month exploration now reuses those source benchmarks for a hypothetical
+10 bp revision on arbitrary second dates. October 30's 4.94% becomes 5.04%;
the original observation remains intact. Python/API checks distinguish missing
observations from genuine zero. The lesson/deployment section of
[M3 validation](m3_validation.md) records exact spread cases and UI checks.


## Visitor wording review — November 8, 2026

The landing page and sixteen lessons now use visitor-facing questions and explicit
experiment prompts. Existing pricing examples, conventions, sources, and tolerances
are retained. The full Python suite passed 525 tests. Browser checks covered
rendered formulas and desktop/mobile lesson openings. The browser-owned Treasury
workflow and its limits are recorded in notes/m3_validation.md.


## November 8, 2026 curriculum consolidation

The seven-lesson rewrite reuses the conventions and published reference benchmarks recorded above. A separate finite cash-flow calculation checked the new $100-face presentation, the reversed price/YTM example, settlement at $97.88297569974827 clean plus $1 accrued, and the 182-day bill at $97.47222222222223. Prices, decimal rates, and normalized risk measures agreed with the Python APIs to absolute 1e-10, well below displayed cents. Sources remain Treasury Appendix B and the earlier benchmark records. See [the curriculum review](lesson_content_review.md#curriculum-tightening--november-8-2026) for the complete teaching and browser verification record.


## M4 curve extension — November 8, 2026

The existing regular and dated YTM conventions are retained. Curve PVs have their
own explicit time and discount conventions. [M4 validation](m4_validation.md)
records the independent synthetic arithmetic, full Fed source reproduction audit,
and short-maturity support decision. Historical coupon-note valuation retains
an open coverage gate; supported zero-coupon principal and synthetic scenarios
can be valued.

## Lesson 8 par and spot yields — November 8, 2026

The hypothetical comparison uses D(0.5)=0.99, D(1)=0.97, D(1.5)=0.94 and D(2)=0.90.
The nominal semiannual spot conversion and par-yield identity follow equations
(3) and (7) in sections 2.1–2.2 of the
[Fed methodology](https://www.federalreserve.gov/pubs/feds/2006/200628/index.html).
The two-year spot yield is 5.3380192161%. Exact rational arithmetic gives a
half-year par coupon of $10/3.80 and annual par yield of 5.2631578947%.
Independent cash-flow valuation reprices that coupon bond to $100 within absolute
1e-12 dollars. Its YTM at $100 matches its coupon rate within absolute 1e-14
in decimal rates.

Changing the calibration price to $100.37 gives D(2)=0.89, par yield 5.8047493404%
and spot yield 5.9123969077%. The zero-coupon YTM solver independently reproduced
both spot yields. Synthetic API factors matched within absolute 1e-14.
Lesson-route, table and collapsed-answer checks passed, and all 32 formulas
rendered with bundled KaTeX. No fresh browser layout review was performed.
