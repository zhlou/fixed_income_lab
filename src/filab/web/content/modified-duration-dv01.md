## How much does a small yield move cost?

Faraway payments usually lose more present value when the discount rate rises.
Modified duration translates that intuition into a local percentage sensitivity.
DV01 translates it into dollars for a **one basis point** move in the bond's
yield to maturity (YTM). One basis point
is 0.01 percentage point, or 0.0001 in decimal yield. A move from 5% to 6% is
100 bp, not 1 bp.

Prerequisite: [cash-flow timing and Macaulay duration](/lessons/macaulay-duration).
Predict first: doubling face value should double dollar exposure, but should it
change percentage sensitivity?

**Goal:** Estimate a small price change from a yield change, first as a percentage and then in dollars. “Local” sensitivity means sensitivity near the starting yield; it can change when the yield changes.

## Which rate moves?

Here, **“yield move” means a change in YTM**, with the coupon rate and all
promised payments held fixed. Recall the distinction:

| Rate | What it means for this fixed-coupon bond | During a yield shock |
|---|---|---|
| Coupon rate | Annual coupon dollars divided by face value; set in the bond's terms | Stays fixed |
| Yield to maturity (YTM) | The single discount rate that makes the present value of remaining promised payments equal the bond's full price | Changes; we recalculate price |

For example, a **4% coupon** on **$100 face** pays **$4 a year**, split into
two **$2 payments** if semiannual. If YTM rises from **5.00% to 5.01%**,
that is a **+1 bp yield move**. The coupons remain $2 each and principal at
maturity remains $100. Discounting those same payments at the higher YTM
gives a lower price; DV01 estimates the dollar decrease.

The experiment asks: “What price would these same payments have if the market
required a different YTM right now?” When observing a market price instead,
we can work backward to its implied YTM, as in the
[YTM lesson](/lessons/yield-to-maturity). Here YTM is an annual nominal rate
compounded at the selected payment frequency. No time passes during the shock;
settlement, payment dates, and compounding convention stay fixed.

## Derive the sensitivity

Think of zooming in on the price-versus-yield curve until a small piece looks straight. Its **slope** is price change divided by yield change. A **derivative**, written $dP/dy$, is the limiting slope as the yield step becomes very small. You can use the resulting duration and DV01 rules without doing calculus yourself.

Keep the previous lesson's notation: price $P$, annual nominal decimal yield $y$,
frequency $m$, $N$ remaining payment periods, payment $CF_k$ at $k/m$ years, and the growth factor $q=1+y/m$.
Differentiate price with respect to **annual decimal yield**, keeping payments
and settlement fixed:

$$
\frac{dP}{dy}=-\sum_{k=1}^{N}\frac{k}{m}CF_kq^{-k-1}.
$$

To see where the factors come from, each price term is $CF_kq^{-k}$. Differentiating the power brings down $-k$, reduces the power by one, and multiplies by $1/m$ because $q=1+y/m$. Thus a more distant payment has a larger timing factor $k/m$ in its sensitivity.

Divide by price and reverse the sign to get a positive sensitivity for these
positive-cash-flow bonds:

$$
D_{\mathrm{mod}}=-\frac{1}{P}\frac{dP}{dy}
=\frac{D_{\mathrm{Mac}}}{1+y/m}.
$$

The division by price expresses the slope relative to the size of the investment. Compared with the Macaulay weighted-time sum, every term has one extra factor $1/q$; that is why the conversion divides by $1+y/m$. Although modified duration is conventionally quoted in years, it describes sensitivity, not a waiting time. A modified duration of 5 means roughly a 5% price fall for a one-percentage-point yield rise.

The symbol $\Delta$ means “change”: $\Delta y$ is new yield minus initial yield, and $\Delta P$ is new price minus initial price. For a small yield change, the **tangent line** is the straight line with the curve's starting slope. Its estimate is

$$
\Delta P\approx-PD_{\mathrm{mod}}\Delta y,
\qquad \frac{\Delta P}{P}\approx-D_{\mathrm{mod}}\Delta y.
$$

Here we define **dollar duration** as $-dP/dy=PD_{\mathrm{mod}}$, in dollars per
unit decimal yield. Terminology varies, so always inspect the units. We define
DV01 as the positive local dollar magnitude:

$$
\mathrm{DV01}=PD_{\mathrm{mod}}\times 0.0001.
$$

A +1 bp move therefore has an approximate price change of **minus DV01**.
A −1 bp move has an approximate gain of DV01. These are approximations;
exact upward and downward moves differ because price is curved.

Use decimal changes in these formulas: +50 bp is +0.005, not 0.5 or 50. **DV01** means “dollar value of one basis point.” It uses the selected face amount: it is not automatically per $100 face or per bond.

## Worked example: turn the two-year bond into dollar risk

For $100 face, 4% coupon, 5% YTM, two years and semiannual payments:

| Measure | Value |
|---|---:|
| Initial price | $98.12 |
| Macaulay duration | 1.941305 years |
| Modified duration | 1.893956 years |
| Dollar duration | $185.83 per unit decimal yield |
| DV01, displayed to cents | $0.02 per bp |

At $100,000 face, price is **$98,119.01**, modified duration remains
**1.893956**, and DV01 is **$18.58**. Scaling face is a useful way to inspect
small dollar sensitivities without confusing display rounding with zero risk.

For a +100 bp shock at $100 face, duration predicts **−$1.86**, or **−1.893956%**.
Exact repricing gives **−$1.84**, or **−1.871310%**. The small difference is real;
full precision is used before displaying cents. No time has passed, so these
numbers are price changes, not a year's return.

For example, the percentage calculation is $-1.893956(0.01)=-0.01893956$, which is **−1.893956%** after multiplying by 100. Multiplying this decimal price change by the initial price gives the dollar estimate.

## Test the prediction

A **basis point** is **0.01 percentage point**, or 0.0001 in decimal yield. Double face value and compare DV01 with modified duration and the percentage price change. Which dollar amounts doubled, and why did percentage sensitivity stay the same?

1. Double face value. Modified duration should stay fixed; dollar duration and
   DV01 should double.
2. Compare the default two-year A and ten-year B at +25 bp, then +200 bp.
   Does the tangent stay equally accurate?
3. Give A a zero coupon at ten years; compare with B's ten-year 4% coupon.
4. Change yield to zero, then negative. For a regular zero-coupon bond,
   modified duration is $T/(1+y/m)$, so it can exceed maturity when yield is
   negative. Macaulay duration still equals maturity.

Equal face values do not mean equal market values or equal DV01. This tool
compares individual-bond YTM shocks. **Key-rate risk** measures sensitivity to changes near particular maturities on a yield curve; it comes later. A curve can steepen or flatten when rates at different maturities move by different amounts, even if one overall duration figure is unchanged.

## Check with numerical repricing

You can estimate the derivative without an analytical formula. Let $h$ be a
small annual decimal-yield bump:

$$
D_h=\frac{P(y-h)-P(y+h)}{2hP(y)}.
$$

Here $P(y-h)$ and $P(y+h)$ are prices at yields just below and above the starting yield. They are $2h$ apart. Dividing their price difference by that gap estimates the slope's positive magnitude; dividing by $P(y)$ gives percentage sensitivity. For a one-basis-point bump, $h=0.0001$.

The numerical-check table tries ±1, ±0.5, and ±0.25 bp. For regular periods,
compare them to the analytical answer. Smaller bumps reduce truncation error
until subtracting nearly equal computer-stored prices loses useful digits; “smaller” is not always “better.” This loss of precision is called **cancellation**. “Analytical” means calculated directly from the derivative formula; “numerical” means estimated from repriced values.

For **Dated settlement**, this calculation uses dirty prices from our existing
pricer: Actual/Actual coupon-period accrual, simple first fractional period,
compound later periods, unadjusted regular dates, and after-payment coupon-date
settlement. Accrued interest is fixed during a yield shock, so clean and dirty
*dollar* changes agree, but dividing by clean versus dirty price would give
different percentage sensitivities. We normalize by dirty price. The dated
result uses ±0.5 bp and does not assert the regular Macaulay conversion.

## Transfer exercise

A bond position has price $10,000 and modified duration 4.0. Predict DV01 and the
first-order price change for a +50 bp move before checking the arithmetic.

::: answer
**Answer:** DV01 is $4.00; the estimate is −$200.00, or −2%. It is not an exact
repricing and not a holding-period return. Explain what extra information you
would need to calculate either of those.
:::

## Reflection checkpoint

- Why is DV01 positive here even though price falls when yield rises?
- If a 4% coupon bond's YTM rises from 5% to 6%, which payments change, and why does its price change?
- What exactly stays fixed when taking the price derivative?
- Why could equal-duration portfolios still respond differently to a changing curve?

Next: [convexity and approximation error](/lessons/convexity).

```python
from filab.risk import bond_risk
risk = bond_risk(face_value=100000, coupon_rate=.04, ytm=.05,
                 maturity_years=2, frequency=2)
print(f"DV01: ${risk.dv01:.2f}")  # $18.58
```

Reference: [CME's DV01 calculation note](https://www.cmegroup.com/trading/interest-rates/files/Calculating_the_Dollar_Value_of_a_Basis_Point.pdf)
relates small price bumps and modified-duration dollar sensitivity. Its printed
price/duration example is checked separately from our bond pricer; see the
validation record for the rounding tolerance and convention limits.
