## Follow the curve beyond its starting slope

For the ten-year 4% bond at 5% semiannual YTM, a **+100 bp** move produces a **−$7.43** duration estimate. Exact repricing gives **−$7.08**. Adding convexity gives **−$7.07**, much closer.

Duration follows a straight line tangent to the price curve. As yield rises, the curve's downward slope becomes less steep. Extending its starting slope therefore overstates the loss. In the opposite direction, the price gain exceeds the straight-line estimate.

## Add the change in slope

The first derivative $P'(y)$ measures the starting slope. The second derivative $P''(y)$ measures how that slope changes. For a small yield step $\Delta y$, approximate the slope at an intermediate step $u$ by $P'(y)+P''(y)u$. Accumulating those changes gives

$$
\Delta P\approx P'(y)\Delta y
+\frac12P''(y)(\Delta y)^2.
$$

The one-half comes from accumulating a slope change that grows from zero to its endpoint over the step. Define **convexity** as $\mathcal C=P''(y)/P$. Substitute the previous lesson's duration relation and divide by price.

$$
\frac{\Delta P}{P}\approx
-D_{\mathrm{mod}}\Delta y
+\frac12\mathcal C(\Delta y)^2.
$$

Differentiating the regular-period pricing sum a second time supplies the convexity used in the experiment. Here $q=1+y/m$ and $w_k$ is the present-value weight of payment $k$.

$$
\mathcal C=\frac{1}{P}\sum_k
\frac{k(k+1)}{m^2}CF_kq^{-k-2}
=\sum_k\frac{k(k+1)}{m^2q^2}w_k.
$$

For these fixed positive payments and positive discount bases, convexity is positive. Because the yield step is squared, the correction is positive in either direction. It reduces the estimated loss on a rate rise and increases the estimated gain on a fall.

## Judge the error in dollars

Our ten-year bond has price **$92.21**, modified duration **8.054231**, and convexity **77.111675 years²**.

| Yield shock | Exact change | Duration | Duration + convexity |
|---|---:|---:|---:|
| −200 bp | +$16.38 | +$14.85 | +$16.27 |
| +100 bp | −$7.08 | −$7.43 | −$7.07 |
| +200 bp | −$13.52 | −$14.85 | −$13.43 |

For +100 bp, the correction in dollars is approximately $\tfrac12(92.21)(77.111675)(0.01)^2=\mathbf{\$0.36}$. All displayed changes use unrounded values before rounding to cents. The table's signed error is estimate minus exact change.

Reverse the shock and then enlarge it. Squaring twice the yield step makes the convexity correction four times larger. Higher-order changes still remain, so exact repricing supplies the benchmark. These are hypothetical immediate price changes at fixed settlement.

The [Risk Explorer](/tools/bond-risk) includes other maturities, coupons, and numerical checks. A different payment pattern can produce different curvature, especially when contractual options change the cash flows.

## Try the correction yourself

A position has price $100, modified duration 5, and convexity 30. Estimate its changes for +100 and −100 bp. Which part changes sign?

::: answer
Duration gives **−$5.00** and **+$5.00**. Convexity adds **$0.15** in either direction, giving **−$4.85** and **+$5.15**. Exact changes require the full pricing model.
:::
