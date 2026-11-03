## Why the straight line misses

As yield rises, a fixed bond's price falls, but the slope itself changes.
Duration freezes that slope at the starting yield. Convexity describes the
curvature and supplies a second-order correction. It helps explain why, for
ordinary positive fixed cash flows, an equal yield fall produces a larger gain
than the loss from an equal yield rise.

Prerequisite: [modified duration and DV01](/lessons/modified-duration-dv01).
Predict the asymmetry before highlighting +200 bp and −200 bp in the explorer.

**Goal:** Improve a duration estimate and measure the error that remains. In the shared experiment, focus on **Bond A · exact versus approximate** and the shock grid. “Exact” here means fully repriced within our model, not a prediction of a market trade.

A **first-order** estimate uses only the starting slope, so it is proportional to the yield change. A **second-order** estimate also uses how that slope changes, adding a term proportional to the square of the yield change. This is why convexity matters more as a shock grows.

## Derive the second-order term

With fixed payments $CF_k$, annual nominal decimal yield $y$, frequency $m$,
price $P$, $N$ remaining payment periods, and growth factor $q=1+y/m$, differentiate the first derivative once more. The **second derivative** $d^2P/dy^2$ measures how the slope changes as yield changes:

$$
\frac{d^2P}{dy^2}=\sum_{k=1}^{N}\frac{k(k+1)}{m^2}CF_kq^{-k-2}.
$$

The previous derivative had the factor $-(k/m)q^{-k-1}$. Differentiating again brings down $-(k+1)/m$: the two minus signs cancel, leaving the positive $k(k+1)/m^2$ factor.

Define convexity $\mathcal C$ as the second derivative divided by initial price. This makes it independent of the position's dollar size. As before, $w_k=CF_kq^{-k}/P$ is payment $k$'s present-value weight:

$$
\mathcal C=\frac{1}{P}\frac{d^2P}{dy^2}
=\sum_{k=1}^{N}w_k\frac{k(k+1)}{m^2q^2}.
$$

It is quoted here in years squared under the annual-yield convention. The factor
one-half belongs in the Taylor approximation, **not** in this definition:

$$
\frac{\Delta P}{P}\approx-D_{\mathrm{mod}}\Delta y+
\frac12\mathcal C(\Delta y)^2.
$$

Here $\Delta y$ is the annual decimal yield change, $D_{\mathrm{mod}}$ is modified duration, and $\Delta P/P$ is the price change divided by initial price. The **Taylor approximation** is this local slope-plus-curvature expansion. The one-half arises because, to this order, the slope changes steadily across the yield step: its average change is half its endpoint change. Multiply the entire expression by $P$ to get dollars.

For these fixed positive cash flows and positive discount bases, convexity is
positive. The correction is positive for both yield directions: it reduces an
estimated loss and increases an estimated gain. Callable bonds can behave
differently: a **call** gives the issuer the right to repay early under specified terms, so expected payments can change as yields change. They are not modeled here.

## Reproduce the ten-year example

Set Bond A to ten years, 4% coupon, 5% nominal YTM, semiannual payments, and
$100 face. Its price is **$92.21**, modified duration **8.054231 years**, and
convexity **77.111675 years²**.

| Yield shock | Exact price change | Duration estimate | Duration + convexity |
|---|---:|---:|---:|
| −200 bp | +$16.38 | +$14.85 | +$16.27 |
| +100 bp | −$7.08 | −$7.43 | −$7.07 |
| +200 bp | −$13.52 | −$14.85 | −$13.43 |

At +200 bp, the exact percentage change is **−14.667277%**. Duration predicts
**−16.108462%**; adding convexity gives **−14.566229%**. Signed errors are
estimate minus exact: **−$1.33** for duration, **+$0.09** for duration plus
convexity. The latter is better here, but it still overestimates the ending price.

All values use full-precision initial price and derivatives; displayed cents are
rounded. This is a hypothetical instantaneous repricing, not a forecast or a
holding-period return.

For the +200 bp row, $\Delta y=0.02$. The curvature contribution is
$\tfrac12(77.111675)(0.02)^2=0.015422335$, or **+1.542234 percentage points**.
Adding it to the duration estimate of −16.108462% gives approximately
−14.566229%. The remaining error is about **+0.101048 percentage point**
of initial price, not 0.101048% of the exact loss. A positive signed error
means the estimate predicts a higher ending price than exact repricing does.

## Inspect the error, not just the estimate

1. Start with ±25 bp, then move through ±50, ±100, and ±200 bp. Inspect errors
   in dollars and in percentage points of initial price.
2. Repeat at two-year maturity. Explain why the approximation behaves differently.
3. Keep ten-year maturity but set coupon to zero. More value sits at the final
   payment; inspect how duration, convexity, and the errors change.
4. Double face value. Dollar errors double; normalized sensitivities and percentage
   errors do not. For the same face, A and B can still have different market values.

For a numerical check, let $h$ be a small decimal yield bump and compare prices at $y-h$, $y$, and $y+h$:

$$
\mathcal C_h=\frac{P(y-h)+P(y+h)-2P(y)}{h^2P(y)}.
$$

For a straight line, the average of the two outer prices would equal the middle price, making the numerator zero. On this convex curve, their average is higher. Dividing by $h^2$ measures curvature; dividing by price removes dollar size.

Second derivatives are especially vulnerable to cancellation at tiny bumps: subtracting nearly equal stored prices can erase significant digits. The
convergence table is a diagnostic; it is not proof that any chosen bump works
for all instruments. Dated mode uses the unchanged settlement pricer and dirty
price normalization, without inventing a textbook Macaulay value.

## Boundaries and misconceptions

- At zero shock, both estimates and exact price change are zero.
- For a regular zero-coupon bond with maturity $T=N/m$,
  $\mathcal C=T(T+1/m)/(1+y/m)^2$; it is not simply duration squared.
- Adding convexity does not make an estimate exact. Higher-order terms remain,
  especially for large shocks, long maturities, or yields near the pricing boundary $1+y/m=0$. Our formulas require a positive discount base.
- A Taylor estimate is not guaranteed to be an economically plausible price;
  exact repricing remains the reference.
- A high convexity figure is not a complete investment recommendation. Credit,
  liquidity, changing cash flows, nonparallel curve moves, and investment horizon
  are separate questions.

## Transfer exercise

A hypothetical position has price $100, modified duration 5, and convexity 30.
Predict its second-order change for +100 bp and −100 bp.

::: answer
**Answer:** the duration terms are −$5.00 and +$5.00. The convexity term is
+$0.15 in either direction, giving estimates of −$4.85 and +$5.15. You cannot
calculate the exact changes from just these two derivatives.
:::

## M1 reflection checkpoint

- Explain maturity, Macaulay duration, modified duration, DV01, and convexity
  in your own words, with their units.
- Reconcile one shock row with the original price and repriced cash flows.
- Why does the dated experiment normalize by dirty price?
- Export a comparison, change the inputs, and import it. What must be saved
  to reproduce the result?
- Describe one result that contradicted your initial prediction.

Record your prediction, observation, explanation, and remaining uncertainty.
Your answers establish learning completion; implementation does not. Next,
M2 will add time, payments, and a cash ledger to explain **holding-period returns**.

```python
from filab.risk import bond_risk
risk = bond_risk(face_value=100, coupon_rate=.04, ytm=.05,
                 maturity_years=10, frequency=2)
shock = .02  # 200 bp, not 2 bp
change = risk.price * (-risk.modified_duration * shock
                       + .5 * risk.convexity * shock**2)
print(f"Estimated price change: ${change:.2f}")  # -$13.43
```
