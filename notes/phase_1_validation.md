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
