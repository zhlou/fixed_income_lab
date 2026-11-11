## Price the four payments

In [lesson 1](/lessons/present-value), our two-year note was worth **\$98.12** at a 5% yield. Here it is worth **\$97.60** on a hypothetical discount curve. In both examples you buy just after a coupon payment and receive the same four amounts. What changes is how much you pay today for a dollar due on each date.

**CF** stands for *cash flow*. The subscript $i$ counts the payment dates in order. For our \$100-face, 4% note, $\mathrm{CF}_1$ is the \$2 coupon you receive in six months. The next two coupons are also \$2 each. The fourth cash flow, $\mathrm{CF}_4$, is **\$102** because the last coupon and the \$100 principal arrive together.

## What is a spot rate?

Imagine buying just one payment. On this curve you could pay **\$99 today** to receive **\$100 in six months**, with nothing paid along the way. The **six-month spot rate** is the annualized yield on that single payment, also called the six-month *zero-coupon yield*. Here “six-month” means the rate covers the time **from today to six months from now**.

You earn \$1 on \$99 over the half-year, about 1.01%. Using an annual nominal rate compounded semiannually, double that half-year rate to quote the six-month spot rate as **2.02% per year**. The same transaction also tells us today’s price of \$1 due in six months, $99/100=0.99$. This is the six-month **discount factor**. The note’s first coupon arrives on that date, so its \$2 is worth **\$1.98 today**.

## Read the curve as rates or prices

A **yield curve** plots annualized yields against maturity. A **spot yield curve** collects the spot rates from today to different payment dates. A **discount-factor curve** shows today's price of \$1 due at each of those dates. With a fixed compounding convention, the two curves express the same pricing information.

Write $s(t)$ for the annual nominal spot rate in decimals, compounded semiannually, for a payment in $t$ years. Its discount factor must grow to \$1 over $2t$ half-year periods, so

$$D(t)\left(1+\frac{s(t)}{2}\right)^{2t}=1
\quad\Longrightarrow\quad
D(t)=\frac{1}{\left(1+s(t)/2\right)^{2t}}.$$

For example, the two-year spot rate is about **5.3380%**. Discounting for four half-years gives $D(2)\approx1/(1+0.053380/2)^4\approx0.90$. The table shows each spot rate, its factor, and the present value (PV) of the note's payment. Rates are displayed rounded; calculations retain full precision.

| Due in | Annual spot rate, semiannual compounding | Discount factor | Payment × factor = PV |
|---|---:|---:|---:|
| 6 months | 2.0202% | 0.99 | $2\times0.99=\$1.98$ |
| 1 year | 3.0692% | 0.97 | $2\times0.97=\$1.94$ |
| 18 months | 4.1679% | 0.94 | $2\times0.94=\$1.88$ |
| 2 years | 5.3380% | 0.90 | $102\times0.90=\$91.80$ |
| **Price today** | | | **\$97.60** |

At a fixed maturity, a higher spot rate gives a smaller discount factor and a lower payment value. A zero spot rate gives a factor of one. A negative spot rate gives a factor above one, provided the half-year growth factor stays positive.

Write $t_i$ for the years until payment $i$. Multiply each cash flow by its factor and add the results to find the price $P$.

$$P=\sum_{i=1}^{4}\mathrm{CF}_i\,D(t_i).$$

The bond's YTM at **\$97.60** is about **5.28%**, quoted with semiannual compounding. That single rate reproduces the total price. The spot curve also gives the value of each payment separately. When every spot rate is the same under a matching compounding convention, YTM pricing and spot-curve pricing agree payment by payment.

::: calculation
The lab also quotes spot rates using continuous compounding. If $z(t)$ is the annual continuously compounded spot rate for a payment in $t$ years, then $D(t)e^{z(t)t}=1$. For the six-month payment, $z(0.5)=-\ln(0.99)/0.5\approx2.01\%$. This and the semiannual quote of 2.02% describe the same \$99 growing to \$100 in six months.
:::

## Why do par and spot yields differ?

The Treasury curve introduced earlier shows **par yields**, the coupon rates that price hypothetical coupon bonds at face value. Our example curve gives a two-year par yield of **5.2632%**, alongside the two-year spot yield of **5.3380%**. Both are annual nominal rates with semiannual compounding.

The spot yield describes buying a single \$100 payment due in two years for **\$90 today**, since $100D(2)=\$90$.

To find the par yield, choose the coupon that makes a two-year \$100-face note worth **\$100 today**. The principal already contributes \$90 of that price, so the four coupons must contribute the remaining \$10. Write $C$ for each half-year coupon in dollars. Discount every coupon, including the one paid with principal at maturity.

$$100=C(0.99+0.97+0.94+0.90)+100(0.90).$$

The factors sum to 3.80, so $C=10/3.80$. The annual coupon rate is twice that coupon divided by \$100 face, giving the **par yield** $2C/100\approx5.2632\%$. Using the unrounded coupon, all payments together are worth exactly \$100.

| Two-year yield | Payments it describes | Annual rate |
|---|---|---:|
| Spot | One \$100 payment, bought for \$90 | 5.3380% |
| Par | Semiannual coupons plus \$100 principal, bought for \$100 | 5.2632% |

Here the earlier coupons are discounted at lower spot rates than the final payment. That makes them more valuable than discounting every payment at the two-year spot rate, so a smaller coupon rate can support a \$100 price. The par yield uses factors from every coupon date, while the two-year spot yield depends only on $D(2)$. On a flat spot curve, par and spot yields coincide under matching conventions.

## How can a second bond tell us the two-year factor?

Suppose we know the first three factors and need the fourth. A second \$100-face note with a 6% annual coupon paid semiannually has a price of **\$101.40**. Its first three \$3 coupons are worth $3(0.99+0.97+0.94)=\$8.70$ today. Subtracting them leaves **\$92.70** of the price for the final **\$103** payment. Divide to find today’s price per dollar due in two years.

$$D(2)=\frac{92.70}{103}=0.90.$$

This process of using earlier factors to recover the next one from a bond price is called **bootstrapping**. Both notes pay on the same two-year date, so the experiment uses that 0.90 factor for the 4% note’s \$102 payment too.

## Change one input

Change the 6% bond’s price from **\$101.40** to **\$100.37** and calculate. The first three factors stay fixed. Which row in the 4% note’s payment table changes, and how much does its price move? Use the new factor to calculate the two-year par and spot yields.

::: answer
The two-year factor falls to $(100.37-8.70)/103=0.89$. Only the final row changes. Each of its 102 dollars is worth one cent less today, so the 4% note’s price falls by **\$1.02**, from **\$97.60** to **\$96.58**.

The new par yield is $2(1-0.89)/(0.99+0.97+0.94+0.89)\approx5.8047\%$. The two-year spot yield is $2(0.89^{-1/4}-1)\approx5.9124\%$. Both rates rise, and the par yield remains lower because the curve still values earlier coupons at lower spot rates.
:::
