## Work backward: price to yield

The **What yield does this price imply?** experiment reverses the pricing
calculation. Enter the price of a hypothetical fixed-coupon bond, keep its
payments fixed, and solve for the annual nominal YTM that discounts those
payments to that price. Rates compound at the selected payment frequency.

For $100 face value, a 4% annual coupon, two years remaining, and semiannual
payments, a price of **$98.12** implies approximately **4.9995% nominal YTM**. Annual
coupon dollars are $4, so current yield is about **4.0766%**.

These three rates answer different questions:

| Rate | Definition | What it includes |
|---|---|---|
| Coupon rate | Annual coupon dollars / face value | The promised coupon size |
| Current yield | Annual coupon dollars / purchase price | Coupon income relative to price |
| YTM | The discount rate that reproduces price | All scheduled coupons and principal |

The solver finds the root of:

$$
\sum_{k=1}^{N}\frac{CF_k}{(1+y/m)^k}-P_{\mathrm{entered}}=0.
$$

For these positive cash flows, price falls as yield rises, giving a unique
YTM for a positive price. The server uses SciPy's bracketed Brent method;
the payment table discounts the payments at the solved yield to check the
result. Calculations use full precision; displayed amounts are rounded,
so the rounded table entries may not sum exactly.

Try prices of $90, $100, $108, and $120 for the default bond. At par, all
three rates equal 4%. Below par, YTM exceeds current yield, which exceeds
coupon rate. Above par, the ordering reverses. At $108, YTM is zero because
the price equals the total promised payments; at $120, YTM is negative.
A zero coupon rate makes current yield zero even when YTM is positive.

YTM is an implied discount rate, not a guaranteed realized return. Earning
its compounded rate through maturity depends on receiving every payment
and reinvesting coupons at that rate. Selling sooner introduces an uncertain
sale price. Current yield omits the gain or loss between purchase price
and principal repayment, as well as reinvestment income.

This experiment still assumes valuation immediately after a coupon payment,
regular coupon periods, and zero accrued interest. Its price is both clean
and dirty under those assumptions. [Settlement between coupon dates](/lessons/settlement-and-accrued-interest)
comes next; [Treasury bill discount quotations](/lessons/treasury-bill-yields)
use a different convention.

```python
from filab.pricing import yield_to_maturity

ytm = yield_to_maturity(
    price=98.12, face_value=100,
    coupon_rate=0.04, maturity_years=2, frequency=2,
)
print(f"Annual nominal YTM: {ytm:.4%}")  # 4.9995%
```

## Try explaining the relationships

1. Why do current yield and YTM differ when price is away from par?
2. How can a positive-coupon bond have a negative YTM?
3. Why does rounding the input price to $98.12 make its implied yield slightly different from 5%?

**Next:** [Settle between coupon dates](/lessons/settlement-and-accrued-interest)
and distinguish clean quotes from the full purchase amount.
