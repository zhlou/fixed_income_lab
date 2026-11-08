## A coupon cushions an early-sale loss

Buy the same two-year note for **$98.12** at 5% nominal YTM. Six months later, receive its **$2.00 coupon** and sell the remaining bond for **$95.80** after YTM rises to 7%. The investment loses about **0.33%** over those six months.

We buy November 15, 2026 after payment and sell May 15, 2027 after receiving that day's coupon. The bond matures November 15, 2028. Cash earns zero and the initial example has no trading costs. Prices are hypothetical, with the yield change applied on the sale date.

## Reconcile the money

At sale, three payments remain. Use the pricing relationship from lesson 1 with the new half-year rate $0.07/2=0.035$.

$$
P_H=\frac2{1.035}+\frac2{1.035^2}+\frac{102}{1.035^3}
=95.797544529\ldots.
$$

| Component | Amount per $100 face |
|---|---:|
| Purchase | $98.12 |
| Sale proceeds | $95.80 |
| Coupon received | $2.00 |
| Ending wealth | $97.80 |
| Net loss | −$0.32 |

Use the unrounded amounts in the holding-period return from the preceding lesson.

$$
R_H=\frac{P_H+2}{P_0}-1
=\frac{95.797544529+2}{98.119012896}-1
\approx\boxed{-0.327631\%}.
$$

The bond price alone fell **2.3660%**. Adding coupon cash brings the investment loss to **0.3276%**. The chart follows both measures so you can see the payment's contribution.

## Include trading costs where they are paid

The cost control charges basis points of face value on each trade. At **10 bp**, each trade costs $100\times0.001=\$0.10$. Initial wealth includes the purchase fee $K_b$. Sale cash is reduced by the sale fee $K_s$.

$$
R_H=\frac{P_H+\text{coupon cash}-K_s}{P_0+K_b}-1.
$$

Thus both the numerator and denominator change. At 10 bp each way, net profit rounds to **−$0.52**, and the six-month return is about **−0.5309%**. The fees are charged once each.

Change exit YTM first, then costs. The note's coupons and principal stay fixed, while a lower sale yield raises its sale price. With a 5% exit YTM and zero costs, the six-month return is **2.50%**. The purchase YTM alone could not tell you which of these sale outcomes would occur.

All examples use the lesson 5 settlement convention. Coupons are credited before sale on a payment date, so the sold bond contains only its remaining payments. The [Return Calculator](/tools/bond-return) includes keeping and marking a position, cash growth, and the full ledger. Use the link beside the experiment to carry its current scenario into that tool.

## Try an unchanged yield

Set exit YTM to 5% with zero costs. Predict why the six-month return differs from both the coupon rate and the annual YTM. Then add 10 bp of cost per trade and locate each fee.

::: answer
Price plus the received coupon produces **2.50% over six months** under these matching regular-period assumptions. The 4% coupon describes annual payments relative to face. The 5% YTM is annual nominal with two periods. Entry and exit fees reduce wealth and increase the initial capital required.
:::
