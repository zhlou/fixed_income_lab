## Price is also a date

**Goal:** Calculate what a buyer actually pays between coupon dates. Prerequisite: [yield to maturity](/lessons/yield-to-maturity). Keep the distinction between promised payments and their present values in mind.

The earlier lessons valued a bond just after a coupon payment. Now choose
an actual settlement date: the date on which the buyer pays for the bond.
A trade date and its settlement date can differ; this lesson takes settlement
as an input rather than calculating a market settlement lag.

In this regular-bond model, the buyer receives the full next coupon, although some of the coupon period
passed before the purchase. **Accrued interest** compensates the seller for
that elapsed portion. The **clean price** excludes accrued interest; the **dirty price** includes it and is the full settlement amount, before any fees. “Dirty” is just a market term, not a judgment about the security.

For example, halfway through a $2 coupon period, the buyer pays $1 of accrued interest to the seller and later receives the full $2 from the issuer. Receiving $2 does not mean the buyer earned $2 since purchase: $1 compensated the seller's portion of the period.

## Count the actual coupon days

Let $F$ be face value, $c$ the annual coupon rate, $m$ payments per year,
$A$ actual days since the previous coupon, and $E$ actual days in that period.
Each regular coupon is $K=Fc/m$. Our Actual/Actual coupon-period calculation is:

$$
AI=K\frac{A}{E}.
$$

$AI$ is accrued interest in dollars. The fraction $A/E$ is the share of the coupon period already elapsed; multiplying by the full coupon allocates that share to the seller. A **day-count convention** specifies how to count the numerator and denominator of such a fraction.

Actual/Actual here means the actual coupon-period denominator, not a fixed
365 days or the separate Actual/Actual ISDA convention. A leap day changes
$E$ when it falls in the relevant coupon period. Other instruments can use
Actual/360, Actual/365, or a 30/360 convention; their fractions need not match.
Do not switch day counts without changing the instrument assumptions.

In the default bond, the May 15–November 15, 2026 period has 184 days.
August 15 is 92 days after May 15. A $2 coupon therefore has $1.00 accrued.
Try May 15, August 15, November 14, and November 15 as settlement dates.
On a coupon date, this model settles **after payment**, starts a new accrual
period, and excludes that day's coupon from future payments.

## Clean price and the amount paid

$$
P_{\mathrm{dirty}}=P_{\mathrm{clean}}+AI,
\qquad P_{\mathrm{clean}}=P_{\mathrm{dirty}}-AI.
$$

All amounts in this experiment are dollars per $100 face. A quote per $100
must be scaled to the actual face amount before combining it with accrued
interest in dollars. On $1,000 face, multiply every displayed dollar amount
by ten. Dollar displays round to cents; calculations keep full precision.

Choose **YTM from price** to enter either a clean or a dirty price. The
solver converts it to the full settlement amount before discounting. Treating
a clean quote as the full amount paid would give the wrong implied yield.

## Discount the remaining payments

Let $w=(E-A)/E$ be the fraction of the current coupon period left, $y$ the annual nominal decimal YTM, and $q=y/m$ the nominal yield per coupon period. There are $N$ remaining payments; $CF_k$ includes principal in the final one. For regular future payments:

$$
P_{\mathrm{dirty}}=\frac{1}{1+wq}
\sum_{k=0}^{N-1}\frac{CF_k}{(1+q)^k}.
$$

The next payment uses $k=0$: it is zero **full** periods beyond the next coupon date, but still $w$ periods away from settlement. First discount later payments back to that next coupon date using full periods, then discount the entire sum back through the remaining fraction. We use simple discounting over the first
fractional period and compound discounting over subsequent full periods.
When $A=0$, $w=1$, and this reduces to the regular-period pricing formula
from Lesson 2. Using $(1+q)^{-w}$ instead would be a different convention.
The supported nominal yield domain is $y>-m$; extreme negative yields that
fall outside that domain are rejected.

## Worked example: from dates to the amount paid

Use the default $100 face, 4% coupon, 5% YTM, semiannual bond. Its issue/accrual start is November 15, 2025; settlement is August 15, 2026; maturity is November 15, 2028.

1. Each coupon is $100 × 0.04 / 2 = **$2.00**.
2. The current period runs May 15–November 15, 2026: $E=184$ and $A=92$ days. Thus $AI=2(92/184)=\$1.00$ and $w=0.5$.
3. Five payments remain: $2 on November 15, 2026; May 15 and November 15, 2027; and May 15, 2028; then $102 on November 15, 2028.
4. The half-year yield is $q=0.05/2=0.025$, and the first fractional-period factor is $1+wq=1.0125$. Discount each payment by that factor and its additional full periods:

$$
\begin{aligned}
P_{\mathrm{dirty}}&=\frac{2}{1.0125}+\frac{2}{1.0125(1.025)}\\
&\quad+\frac{2}{1.0125(1.025)^2}\\
&\quad+\frac{2}{1.0125(1.025)^3}\\
&\quad+\frac{102}{1.0125(1.025)^4}\\
&\approx\$98.88.
\end{aligned}
$$

The clean price is **$97.88**, accrued interest is **$1.00**, and the amount paid is **$98.88** per $100 face. Compare the experiment's payment table with the five terms above. The next coupon's present value is $2 / 1.0125 ≈ **$1.98**, not the full $2 today.

To practice a quote conversion without rounding ambiguity, select **YTM from price**, enter **$98.00 Clean**, and verify a **$99.00 dirty** amount. Then select **Dirty** and enter **$99.00**: the implied yield should be the same.

## Watch the bond approach par

This tendency toward face value as maturity approaches is called **pull-to-par**. Unlike the earlier yield shocks, time now passes and payments leave the bond.

The chart holds YTM fixed and moves settlement forward. Try a coupon below,
equal to, and above YTM. A discount bond's clean price generally rises toward
par; a premium bond's clean price generally falls toward par. The day before
maturity, clean price approaches $100 and dirty price approaches $100 plus
the last coupon. Principal and the last coupon are then paid out.

Between coupon dates accrued interest rises. At a coupon date it resets to
zero and dirty price drops as cash leaves the bond. **A price chart omits
coupons received and is not a total-return chart.** A flat YTM assumption
is a hypothetical scenario, not a prediction. Between-date clean prices need
not equal par exactly when coupon equals YTM under this fractional-period rule.

## What the dates do and do not represent

Schedules work backward from maturity, retaining an end-of-month rule when
maturity is at month end. Issue/accrual start must lie on that regular grid.
An irregular first or last coupon period is called a **stub**. **Ex-coupon trading** means the next coupon remains with the seller despite a purchase before the payment date. Stub coupons, business-day payment adjustments, holidays, ex-coupon trading, fees, and tax treatment are outside this regular-bond lab.
Actual Treasury transactions can require those additional rules.

The conventions and reference checks are documented in the
[Treasury's Appendix B, sections I.D and II.A/D](https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf).

```python
from datetime import date
from filab.pricing import settled_bond_valuation

value = settled_bond_valuation(
    face_value=100, coupon_rate=0.04, ytm=0.05,
    issue_date=date(2025, 11, 15),
    settlement_date=date(2026, 8, 15),
    maturity_date=date(2028, 11, 15),
)
print(f"Clean: ${value.clean_price:.2f}")
print(f"Accrued: ${value.accrued_interest:.2f}")
print(f"Paid: ${value.dirty_price:.2f}")
```

## Transfer exercise

A hypothetical semiannual bond has $1,000 face, a 6% annual coupon, and a clean quote of $99.00 per $100 face. Settlement is 61 days into a 183-day coupon period. What are the coupon, accrued interest, and full amount paid?

::: answer
The coupon is $1,000 × 0.06 / 2 = **$30.00**. Accrued interest is $30 × 61 / 183 = **$10.00**. Scale the clean quote first: $99 × 10 = **$990.00**. The dirty amount is **$1,000.00**. The $30 coupon still arrives in full on its payment date; accrued interest does not reduce the issuer's payment.
:::

## Check your understanding

1. Why does a buyer pay accrued interest when the issuer pays the next coupon in full?
2. What changes when settlement moves from the day before a coupon to the coupon date?
3. Why is a dirty-price drop on a coupon date not itself an investment loss?
4. Why must the YTM solver know whether the entered price is clean or dirty?
5. Why does a zero-coupon bond have no accrued coupon interest here?

**Next:** [Read Treasury bill yield quotations](/lessons/treasury-bill-yields).
