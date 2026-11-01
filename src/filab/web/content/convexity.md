## Why the straight line misses

As yield rises, a fixed bond's price falls, but the slope itself changes.
Duration freezes that slope at the starting yield. Convexity describes the
curvature and supplies a second-order correction. It helps explain why, for
ordinary positive fixed cash flows, an equal yield fall produces a larger gain
than the loss from an equal yield rise.

Prerequisite: [modified duration and DV01](/lessons/modified-duration-dv01).
Predict the asymmetry before highlighting +200 bp and −200 bp in the explorer.

## Derive the second-order term

With fixed payments $CF_k$, annual nominal decimal yield $y$, frequency $m$,
price $P$, and $q=1+y/m$, differentiate the first derivative once more:

$$
\frac{d^2P}{dy^2}=\sum_{k=1}^{N}\frac{k(k+1)}{m^2}CF_kq^{-k-2}.
$$

Define convexity $\mathcal C$ as normalized second derivative:

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

For these fixed positive cash flows and positive discount bases, convexity is
positive. The correction is positive for both yield directions: it reduces an
estimated loss and increases an estimated gain. Callable bonds can behave
differently because their expected payments can change; they are not modeled here.

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

## Inspect the error, not just the estimate

1. Start with ±25 bp, then move through ±50, ±100, and ±200 bp. Inspect errors
   in dollars and in percentage points of initial price.
2. Repeat at two-year maturity. Explain why the approximation behaves differently.
3. Keep ten-year maturity but set coupon to zero. More value sits at the final
   payment; inspect how duration, convexity, and the errors change.
4. Double face value. Dollar errors double; normalized sensitivities and percentage
   errors do not. For the same face, A and B can still have different market values.

A central numerical check is

$$
\mathcal C_h=\frac{P(y-h)+P(y+h)-2P(y)}{h^2P(y)}.
$$

Second derivatives are especially vulnerable to cancellation at tiny bumps. The
convergence table is a diagnostic; it is not proof that any chosen bump works
for all instruments. Dated mode uses the unchanged settlement pricer and dirty
price normalization, without inventing a textbook Macaulay value.

## Boundaries and misconceptions

- At zero shock, both estimates and exact price change are zero.
- For a regular zero-coupon bond with maturity $T=N/m$,
  $\mathcal C=T(T+1/m)/(1+y/m)^2$; it is not simply duration squared.
- Adding convexity does not make an estimate exact. Higher-order terms remain,
  especially for large shocks, long maturities, or yields near the pricing boundary.
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
