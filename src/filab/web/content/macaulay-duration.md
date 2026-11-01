## Follow value, not just the final date

A bond can repay some value early through coupons and the rest at maturity.
Maturity tells you when the last payment arrives. **Macaulay duration** asks when
value arrives on average, weighting each payment by its contribution to today's
price. It is a center of present value, not a literal date on which you recover
all your investment.

Prerequisite: [present value and bond pricing](/lessons/present-value).
Before changing a control, predict which has the longer weighted payment time:
a ten-year zero-coupon bond or a ten-year bond with coupons.

## Define the clock and weights

We begin just after a coupon payment. Face value is $F$, annual coupon rate is
$c$, annual nominal yield is $y$, and there are $m$ equal payments per year.
Time $t_k=k/m$ is in years, $N=mT$ is the number of payments, and $CF_k$ includes
principal in the final payment. Coupon and compounding frequencies match.
No accrued interest, default, embedded options, or changing cash flows are modeled.

$$
q=1+y/m,\qquad PV_k=CF_kq^{-k},\qquad P=\sum_{k=1}^{N}PV_k.
$$

Divide each present value by total price to get a weight:

$$
w_k=\frac{PV_k}{P},\qquad \sum_{k=1}^{N}w_k=1.
$$

The weighted average payment time is therefore

$$
D_{\mathrm{Mac}}=\sum_{k=1}^{N}t_kw_k.
$$

This is an identity under these conventions. The weights use **discounted value**,
not face value or undiscounted payment totals. Earlier cash has more present value
per dollar. Multiplying every payment by the same factor leaves the weights unchanged.

## Reproduce a two-year example

Use Bond A's defaults: $100 face, 4% coupon, two years, 5% nominal YTM,
semiannual payments. The four payments are $2, $2, $2, and $102.

| Time in years | Payment | Present value, displayed to cents |
|---|---:|---:|
| 0.5 | $2.00 | $1.95 |
| 1.0 | $2.00 | $1.90 |
| 1.5 | $2.00 | $1.86 |
| 2.0 | $102.00 | $92.41 |

The unrounded values give a price of **$98.12** and Macaulay duration of
**1.941305 years**. Calculate each contribution as time × present value / price;
the weight table in the experiment shows the contributions at higher precision.
Use unrounded values when summing: cent displays can differ from the rounded total.

For the default ten-year Bond B, price is **$92.21** and Macaulay duration is
**8.255587 years**. Both have the same coupon and yield. The later principal
repayment shifts the center of value outward.

## Predict, experiment, explain

1. Keep both maturities at ten years. Set A's coupon to zero and B's to 4%.
   Predict which duration is longer, then open the payment-weight chart.
2. Increase A's coupon to 8%. Where does the center of value move?
3. Double face value. Which table entries change, and which stay fixed?
4. Keep a zero coupon and change maturity from ten to two years. All its
   present value remains at the only payment date.

For a zero-coupon bond, $D_{\mathrm{Mac}}=T$. For multiple positive payments,
it lies between the first and last payment times. A positive-coupon bond with
only one payment remaining also has duration equal to maturity. As the last
payment approaches, its remaining weighted time approaches zero. Time passing
across a coupon also removes a payment; it is not the same experiment as changing
yield while holding time fixed.

## The boundary between timing and sensitivity

Macaulay duration is not yet the percentage response to a yield shock. The next
lesson derives that conversion. It also distinguishes a dimensionless percentage
change from dollar exposure. A long weighted payment time does not measure credit,
liquidity, inflation, or all possible yield-curve changes.

If you choose **Dated settlement**, the experiment preserves our simple first
fractional-period discounting convention. It shows actual payment dates and PV
weights, but deliberately does not report textbook Macaulay duration or apply
its regular-period conversion. Numerical price sensitivity remains available.

## Transfer exercise — attempt before reading the answer

A three-year zero-coupon bond has $100 face and an 8% nominal yield with quarterly
compounding. Predict its Macaulay duration and whether doubling face changes it.

::: answer
**Answer:** 3 years, unchanged by doubling face. There is one positive payment at
year three; its weight is one regardless of the discount rate. This does not say
its modified duration is three years.
:::

## Reflection checkpoint

- Explain why a ten-year bond can have duration less than ten years.
- Why do we weight by present value instead of promised payment size?
- What observation in the payment table changed your prediction?

Write your own explanation before opening [modified duration and DV01](/lessons/modified-duration-dv01).
Completing this page's software does not complete your learning checkpoint.

```python
from filab.risk import bond_risk
risk = bond_risk(face_value=100, coupon_rate=.04, ytm=.05,
                 maturity_years=2, frequency=2)
print(risk.macaulay_duration)  # 1.941305387...
```

Reference: [CFA Institute: yield-based duration measures](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/yield-based-bond-duration-measures-and-properties).
The numerical example above is independently reproducible from its four payments.
