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
| Appendix B V.D.1 | 20-day bill at 7.93% discount | Price 99.559444; investment yield 8.076% |
| Appendix B V.D.2 | 364-day bill at 7.65% discount | Price 92.265000; investment yield 8.237% |
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
