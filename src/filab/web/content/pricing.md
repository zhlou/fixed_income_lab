These optional examples connect the formulas above to the Python functions
behind the calculator. You can understand and complete this lesson without
writing code or setting up a Python environment.

The cash-flow generator determines **what gets paid**; the pricing functions
determine **what those payments are worth today**. Changing yield changes
price, not the promised coupon schedule.

```python
from filab.pricing import (
    fixed_coupon_cashflows,
    price_zero_coupon,
    price_coupon_bond,
)

# $20 at 0.5, 1.0, and 1.5 years; $1,020 at 2.0 years.
payments = fixed_coupon_cashflows(
    face_value=1000, coupon_rate=0.04, maturity_years=2
)

zero_price = price_zero_coupon(
    face_value=1000, ytm=0.05, maturity_years=2
)
coupon_price = price_coupon_bond(
    face_value=1000, coupon_rate=0.04, ytm=0.05, maturity_years=2
)
print(f"Zero-coupon price: ${zero_price:.2f}")  # $905.95
print(f"Coupon-bond price: ${coupon_price:.2f}")  # $981.19
```

Rates are annual decimals; the default frequency is semiannual. A 5% YTM
means 2.5% per half-year. The coupon-bond pricer discounts each scheduled
payment and sums the present values without intermediate rounding.

Use `frequency=1` in the zero-coupon pricer when supplying an effective
annual rate. These functions use the regular-period assumptions explained
in the lesson; actual settlement dates and accrued interest come later.
