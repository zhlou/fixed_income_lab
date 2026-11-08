## A $97.88 quote costs $98.88

The buyer pays **$98.88 per $100 face**, consisting of a **$97.88 clean quote** and **$1.00 accrued interest**. Settlement is August 15, 2026, halfway between the May 15 and November 15 coupons on our 4% semiannual note.

Settlement is the date money and ownership change hands. The buyer receives the full next $2 coupon. Paying the seller for the elapsed part of its period prevents that entire coupon from appearing to be income earned since purchase.

## Allocate the elapsed coupon

Let $K$ be coupon dollars per payment, $A$ the actual days since the previous coupon, and $E$ actual days in the coupon period. Accrued interest $AI$ allocates the coupon in proportion to elapsed days.

$$
AI=K\frac{A}{E}
=2\frac{92}{184}=\boxed{\$1.00}.
$$

This **Actual/Actual coupon-period** convention uses the actual length of that coupon period. A leap day matters when it lies inside the period.

The **clean price** excludes accrual. The **dirty price** includes it and is the full settlement amount before fees.

$$
P_{\mathrm{dirty}}=P_{\mathrm{clean}}+AI.
$$

Every dollar amount here is per $100 face. On $1,000 face, multiply the clean price, accrual, and dirty price by ten.

## Cross the payment date

Move settlement to November 14, then November 15. Just before payment, accrual includes almost the entire coupon. On the coupon date it resets to zero.

This model settles **after payment** on a coupon date. Someone buying on November 15 receives the next coupon in May. Someone holding from November 14 receives the November payment as cash, while the remaining bond value falls when that payment leaves it. To follow that holder's wealth, count both the remaining bond and the credited cash.

The experiment lists the payments belonging to the buyer. The next two lessons follow those receipts through redemption or sale.

::: calculation
**How the dated price is calculated**

The bond's issue/accrual start is November 15, 2025 and maturity is November 15, 2028. At August 15 settlement, five payments remain, ending with $102 at maturity. Let $w=(E-A)/E=0.5$ be the fraction until the next coupon and $q=y/2=0.025$ at 5% nominal YTM.

Discount through the first fractional period using simple interest, then through full semiannual periods using compound interest.

$$
\begin{aligned}
P_{\mathrm{dirty}}&=\frac{1}{1+wq}
\sum_{k=0}^{4}\frac{CF_k}{(1+q)^k}\\
&=\frac{1}{1.0125}\left[2+\frac2{1.025}+\frac2{1.025^2}
+\frac2{1.025^3}+\frac{102}{1.025^4}\right]\\
&\approx\$98.88.
\end{aligned}
$$

Subtract the $1.00 accrual to get $97.88 clean. At the start of a coupon period, $w=1$ and the expression reduces to regular-period pricing. The experiment's expanded payment table shows each discounted amount.

Dates use regular maturity-anchored coupons and after-payment settlement. Stub coupons, holiday adjustments, ex-coupon rules, and settlement lags are excluded. [Treasury Appendix B, sections I and II](https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf).
:::

## Try a quote conversion

At August 15, select **YTM from price** and enter **$98.00 Clean**. What is the full amount paid? Then enter that amount as Dirty and compare the implied yield.

::: answer
The full amount is **$99.00**. Entering $99.00 Dirty represents the same purchase and gives the same YTM. Reset restores the worked $97.88 clean / $98.88 dirty valuation at 5% YTM.
:::
