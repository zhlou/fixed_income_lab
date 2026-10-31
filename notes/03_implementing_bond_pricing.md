# Step 4: Implement Cash Flows and Pricing

## Connect the math to the code

The implementation separates what the bond pays from how we value those payments.

- `src/filab/pricing/cashflows.py`: generates regular payments without knowing the yield.
- `src/filab/pricing/yield_math.py`: discounts payments using a supplied yield.
- `tests/test_pricing.py`: checks worked examples, economic identities, and input constraints.

## 1. Generate cash flows

```python
from filab.pricing import fixed_coupon_cashflows

payments = fixed_coupon_cashflows(
    face_value=1000, coupon_rate=0.04, maturity_years=2
)
for payment in payments:
    print(payment.time_years, payment.amount)
```

Expected output:

```text
0.5 20.0
1.0 20.0
1.5 20.0
2.0 1020.0
```

Each `CashFlow` stores a time in years and a dollar amount. The coupon is
`face_value * coupon_rate / frequency`. The generator adds principal only to
the last payment. Yield does not affect this schedule.

## 2. Discount a zero-coupon payment

```python
from filab.pricing import price_zero_coupon

price = price_zero_coupon(face_value=1000, ytm=0.05, maturity_years=2)
print(f"{price:.2f}")  # 905.95
```

The core calculation directly implements Lesson 2:

```python
period_rate = ytm / frequency
periods = frequency * maturity_years
price = face_value / (1 + period_rate) ** periods
```

`ytm=0.05, frequency=2` means 5% annual nominal yield, or 2.5% per half-year.
It does not mean a 5% effective annual rate.

To supply an effective annual rate, use annual compounding (`frequency=1`):

```python
price = price_zero_coupon(
    face_value=1000, ytm=0.04, maturity_years=0.5, frequency=1
)
print(f"{price:.2f}")  # 980.58
```

Fractional periods are allowed for this generic compound-rate calculation.
Treasury bill discount-yield conventions are not implemented yet.

## 3. Sum the discounted coupon payments

```python
from filab.pricing import price_coupon_bond

price = price_coupon_bond(
    face_value=1000, coupon_rate=0.04, ytm=0.05, maturity_years=2
)
print(f"{price:.2f}")  # 981.19
```

The pricer gets the schedule from `fixed_coupon_cashflows`, then discounts
each payment by its period number: 1, 2, 3, 4. It uses `math.fsum` to sum the
present values accurately. Formatting rounds the displayed result; the
function does not round intermediate values.

## Assumptions and boundaries

- Coupon valuation is immediately after a coupon payment. The next payment is
  one full period away; accrued interest is zero.
- Coupon maturities must be whole numbers of periods. With semiannual
  coupons, 0.5, 1, and 1.5 years are supported; 0.75 years requires settlement
  timing logic that comes later.
- Face value is positive, coupon rate is nonnegative, and frequency is a
  positive integer. Rates and times must be finite real numbers.
- Negative yields are supported as long as `1 + ytm/frequency > 0`.
- A zero-coupon payment at time zero is worth face value. The coupon
  generator requires at least one future period.
- Face value sets the price units: use 100 for prices per 100 of face value.
- This is a single-yield model. Market discount curves, date conventions,
  and clean/dirty price calculations will be added in later lessons.

## Validate and experiment

Run `python -m pytest` from the activated environment. Validation covers the
lesson examples, par pricing, price decreasing with yield, zero-yield totals,
equivalent compounding conventions, and invalid inputs.

Try changing just `ytm` from 0.05 to 0.04, then 0.03. Predict whether the
price is below, equal to, or above $1,000 before running the calculation.
Then change `coupon_rate` while keeping yield fixed. Explain which changes
alter the promised payments and which only alter their present value.
