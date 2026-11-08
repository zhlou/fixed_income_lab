## Follow the bond all the way to cash

Buy our two-year, 4% semiannual note at 5% YTM for **$98.12**. Hold every coupon as idle cash. At maturity you have four $2 coupons and $100 principal, or **$108.00**. Redemption leaves zero face value held.

This is a closed investment with no additional deposits or withdrawals. Its holding-period return is ending wealth $W_H$ divided by initial wealth $W_0$, less one.

$$
R_H=\frac{W_H-W_0}{W_0}=\frac{W_H}{W_0}-1.
$$

Using the unrounded purchase price, $108/98.119012896-1=\mathbf{10.070410\%}$. That return covers the whole two years. Purchase YTM is an annual nominal quote, so comparing the two requires attention to their periods and to what the coupons earn after receipt.

## Why price approaches face value

Keep YTM fixed in the first experiment. A discount bond has a coupon below the required yield. Each period that passes removes some of those below-market coupons and brings the $100 principal closer.

The pricing sum makes this precise. Let $q=y/m$ be the period yield, $C$ the coupon dollars, $F$ face value, and $N$ remaining periods. At coupon dates just after payment, subtract the price of a par bond, whose coupon would be $Fq$.

$$
P-F=(C-Fq)\sum_{k=1}^{N}(1+q)^{-k}.
$$

With fewer remaining periods, the positive sum shrinks, so the discount or premium shrinks. Immediately before the last payment, the bond is worth the approaching principal plus final coupon. After payment, that value is cash in the holder's account. The price chart stops before redemption so you can see the approach to par.

This is **pull-to-par** under a fixed-YTM assumption. Changing yields can dominate that price movement before maturity. Select Premium bond to see the same reasoning with a coupon above the required yield.

## Give the coupons somewhere to earn

Switch the experiment to **Coupon reinvestment**. To isolate the arithmetic, this example pays **annual coupons** over two exact 365-day periods. It costs

$$
P_0=\frac4{1.05}+\frac{104}{1.05^2}
=98.140589569\ldots.
$$

| Receipt | Held at 0% | Cash earns 5% for the remaining year |
|---|---:|---:|
| First year's $4 coupon at the horizon | $4.00 | $4.20 |
| Final coupon and principal | $104.00 | $104.00 |
| Ending wealth | **$108.00** | **$108.20** |

The $0.20 comes from investing the first coupon for one year. The final payment arrives at the horizon and has no time to grow. At 5% cash growth, the two-year return is **10.25%** and the equivalent compounded annual return is $\sqrt{1.1025}-1=5\%$.

Why does that match purchase YTM? Multiply the original pricing sum by the growth factor through the horizon.

$$
P_0(1+q)^N=\sum_{k=1}^{N}CF_k(1+q)^{N-k}.
$$

The right-hand side is terminal wealth when each payment earns the same period rate $q$ for its remaining periods. A different cash rate changes that wealth. For semiannual YTM $y$, the matching annual effective rate is $(1+y/2)^2-1$. Calendar half-years have varying lengths, so the calculator's separate Actual/365 Fixed cash account can differ from this equal-period identity.

The [Return Calculator](/tools/bond-return) supports other dates, cash horizons, and complete ledgers.

## Try a different cash rate

In the annual example, change cash growth from 5% to 3%. Predict ending wealth and explain which receipt earns interest.

::: answer
The first $4 grows to **$4.12**. Add the final $104 for **$108.12**. The bond's promised coupons and principal stay fixed while the cash account earns $0.12.
:::
