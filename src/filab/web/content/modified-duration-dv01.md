## The later principal moves more

Give the two-year note a **+100 bp** yield shock, from 5% to 6%. Its price falls from **$98.12 to $96.28**, a **1.87%** loss. A ten-year bond with the same $100 face, 4% coupon, and 5% initial YTM falls from **$92.21 to $85.12**, a **7.68%** loss.

This is an immediate repricing. Settlement and promised payments stay fixed while the discount rate changes. Most of the ten-year bond's value comes from more distant payments, whose discount factors respond more strongly.

## Measure when today's value is paid

Let $CF_k$ be the payment in period $k$, $m$ the number of periods per year, and $y$ annual nominal decimal YTM. Payment time is $t_k=k/m$ years. Write the period growth factor as $q=1+y/m$.

The share of price attributable to payment $k$ is its **present-value weight**, $w_k=CF_kq^{-k}/P$. The weights add to one. Their weighted average payment time is **Macaulay duration**.

$$
D_{\mathrm{Mac}}=\sum_k t_kw_k.
$$

For the two-year note, about **94.18%** of price comes from the final $102. The other coupons arrive earlier, bringing the average time down to **1.941305 years**. For a zero-coupon bond, the sole payment carries all the weight and Macaulay duration equals maturity.

## Turn timing into price sensitivity

Differentiate the pricing sum with respect to annual decimal yield, holding its payments and dates fixed. A derivative is the price curve's local slope.

$$
\begin{aligned}
\frac{dP}{dy}
&=-\sum_k\frac{k}{m}CF_kq^{-k-1}\\
&=-\frac{P}{q}\sum_k t_kw_k.
\end{aligned}
$$

The timing term $k/m$ makes distant payments more sensitive. Divide the negative slope by price to obtain **modified duration**.

$$
D_{\mathrm{mod}}=-\frac{1}{P}\frac{dP}{dy}
=\frac{D_{\mathrm{Mac}}}{1+y/m},
\qquad
\frac{\Delta P}{P}\approx-D_{\mathrm{mod}}\Delta y.
$$

For the two-year note, $D_{\mathrm{mod}}=1.893956$. A +100 bp move is $\Delta y=0.01$, giving an estimated change of **−1.893956%**, or **−$1.86**. Exact repricing gives **−$1.84**. The next lesson examines that approximation error.

**DV01** expresses the local dollar sensitivity for one basis point, $0.0001$ in decimal yield. We report its positive magnitude.

$$
\mathrm{DV01}=P D_{\mathrm{mod}}\times0.0001.
$$

At $100 face the note's DV01 rounds to $0.02. At **$100,000 face**, price is **$98,119.01** and DV01 is **$18.58 per bp**. A small upward yield move produces approximately that many dollars of loss per basis point. Face value scales dollar exposure, while payment weights and percentage sensitivity stay fixed.

The experiment compares equal face amounts and regular semiannual periods immediately after payment. The [Risk Explorer](/tools/bond-risk) lets you change coupons, maturities, frequency, and settlement dates, and inspect numerical sensitivities. The Macaulay conversion above belongs to the regular-period convention used here.

## Try a larger position

Double face value from $100 to $200. Predict what happens to modified duration, DV01, and the percentage loss for the same yield shock, then check the comparison.

::: answer
Modified duration and the percentage loss stay fixed. Price and DV01 double because every payment doubles. Equal face amounts across different bonds can still carry different dollar exposure.
:::
