## Work backward: price to yield

**Goal:** Find the yield implied by a price and explain why it differs from the coupon rate. Prerequisite: [present value and bond pricing](/lessons/present-value).

Previously we supplied a yield and calculated price. Now the price is known.
**Yield to maturity (YTM)** is the one discount rate that makes the present
value of the remaining promised payments equal that price. It summarizes
price and payment timing in a rate; it does not change the promised payments.

Use a hypothetical bond with $100 face, a 4% annual coupon, two years
remaining, and semiannual payments. Its receipts are $2, $2, $2, and $102.
Valuation is just after a coupon date: no accrued interest, fees, or taxes.
YTM is an annual nominal rate compounded at the selected payment frequency.

## Three rates, three questions

- **Coupon rate:** What coupon does the contract promise? Divide annual coupon dollars by face value.
- **Current yield:** How much annual coupon income is there relative to the price? Divide annual coupon dollars by purchase price.
- **YTM:** What single rate accounts for price and payment timing? Find the rate that discounts every remaining coupon and principal payment to the purchase price.

For a price of **$98.12**, the coupon rate is $4 / $100 = **4%**,
current yield is $4 / $98.12 ≈ **4.0766%**, and YTM is approximately
**4.9995%**. Buying below $100 adds a gain at redemption that current yield
does not include. Current yield also ignores when the coupons arrive.

## Solve by checking trial yields

For this bond, a trial yield $y$ produces:

$$
\begin{aligned}
P(y)&=\frac{2}{1+y/2}+\frac{2}{(1+y/2)^2}\\
&\quad+\frac{2}{(1+y/2)^3}+\frac{102}{(1+y/2)^4}.
\end{aligned}
$$

Try these annual nominal yields and compare their prices with the $98.12 target:

| Trial YTM | Price | What to do next |
|---|---:|---|
| 4% | $100.00 | Price is too high; increase the trial yield |
| 6% | $96.28 | Price is too low; decrease the trial yield |
| 5% | $98.12 | Matches to cents; refine using unrounded values |

At exactly 5%, the calculated price is $98.1190129 before rounding.
The entered $98.12 is slightly higher, so its implied yield is slightly lower
than 5%. A displayed price match is not necessarily an exact match.

For the general case, let $m$ be payments per year, $N$ the number of remaining
periods, $CF_k$ the payment in period $k$, and $P_{\mathrm{entered}}$ the
purchase price. We seek the yield that makes this difference zero:

$$
\sum_{k=1}^{N}\frac{CF_k}{(1+y/m)^k}-P_{\mathrm{entered}}=0.
$$

Finding a **root** means finding an input that makes an expression zero.
The calculator repeatedly narrows a range of trial yields, then checks the
answer by discounting every payment at the solved rate. There is generally
no convenient formula that isolates $y$ for a multi-payment coupon bond.

For positive future payments, price falls continuously as yield rises within
$1+y/m>0$. It ranges from arbitrarily large to arbitrarily small positive
prices, so a positive price has one mathematical YTM under this convention.
Extremely large or small inputs can exceed the calculator's numerical limits.

## Predict, then change the price

Keep the default payments fixed. Before entering $90, $100, $108, and $120,
predict whether each implied yield is above 4%, equal to 4%, between 0% and
4%, zero, or negative. Verify each result in the discounted-payment table.

::: answer
- At **$90**, YTM is about **9.6150%**: paying less buys the same receipts.
- At **$100**, coupon rate, current yield, and YTM all equal **4%**.
- At **$108**, YTM is **0%**: price equals all promised receipts, $2 + $2 + $2 + $102.
- At **$120**, YTM is about **−5.3414%**: you pay more than all future receipts combined.
:::

For these regular positive-coupon bonds, below par YTM exceeds current yield,
which exceeds coupon rate. Above par the ordering reverses. A zero-coupon
bond is a useful exception to strict ordering: coupon rate and current yield
are both zero even when YTM is positive.

## What YTM does and does not tell you

YTM is an implied discount rate, not a guaranteed realized return. Calculating
it does not require you to reinvest anything. Turning it into a compound
return through maturity requires all payments to arrive and coupons to earn
that same periodic rate when reinvested. Selling sooner also introduces an
uncertain sale price. A positive coupon can coexist with a negative YTM if
the purchase price is high enough.

The price here is the full purchase amount. Between coupon dates, the quoted
price may exclude accrued interest. The [settlement lesson](/lessons/settlement-and-accrued-interest)
will call these **clean** and **dirty** prices and explain the conversion.

## Transfer exercise: one payment needs no search

A zero-coupon bond costs $96.00 per $100 face and matures in one year.
Use semiannual compounding. Start from $96=100/(1+y/2)^2$ and solve for $y$.
Would current yield describe this investment's gain?

::: answer
Divide by 96, take the square root, subtract one, then multiply by two:

$$
y=2\left[\left(\frac{100}{96}\right)^{1/2}-1\right]
\approx 4.1241\%.
$$

Current yield is zero because there are no coupons. The one-year return is
$100 / $96 − 1 ≈ **4.1667%**. It is the effective annual return; 4.1241% is
the equivalent annual nominal quote with two compounding periods.
:::

## Reflection checkpoint

1. Why do current yield and YTM differ when price is away from par?
2. How can a positive-coupon bond have a negative YTM?
3. Why does rounding the input price to $98.12 make its implied yield slightly different from 5%?
4. What information beyond YTM would you need to determine a return from selling early?

```python
from filab.pricing import yield_to_maturity

ytm = yield_to_maturity(
    price=98.12, face_value=100,
    coupon_rate=0.04, maturity_years=2, frequency=2,
)
print(f"Annual nominal YTM: {ytm:.4%}")  # 4.9995%
```

**Next:** [Settle between coupon dates](/lessons/settlement-and-accrued-interest)
and distinguish clean quotes from the full purchase amount.
