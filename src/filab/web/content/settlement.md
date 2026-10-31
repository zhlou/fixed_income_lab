## Price is also a date

The earlier lessons valued a bond just after a coupon payment. Now choose
an actual settlement date: the date on which the buyer pays for the bond.
A trade date and its settlement date can differ; this lesson takes settlement
as an input rather than calculating a market settlement lag.

The buyer receives the full next coupon, although some of the coupon period
passed before the purchase. **Accrued interest** compensates the seller for
that elapsed portion. It is separate from the clean price quoted for the bond.

## Count the actual coupon days

Let $F$ be face value, $c$ the annual coupon rate, $m$ payments per year,
$A$ actual days since the previous coupon, and $E$ actual days in that period.
Each regular coupon is $K=Fc/m$. Our Actual/Actual coupon-period calculation is:

$$
AI=K\frac{A}{E}.
$$

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

Let $w=(E-A)/E$ be the fraction of the current coupon period left and
$q=y/m$ the nominal yield per coupon period. For regular future payments:

$$
P_{\mathrm{dirty}}=\frac{1}{1+wq}
\sum_{k=0}^{N-1}\frac{CF_k}{(1+q)^k}.
$$

The next payment uses $k=0$. We use simple discounting over the first
fractional period and compound discounting over subsequent full periods.
When $A=0$, $w=1$, and this reduces to the regular-period pricing formula
from Lesson 2. Using $(1+q)^{-w}$ instead would be a different convention.
The supported nominal yield domain is $y>-m$; extreme negative yields that
fall outside that domain are rejected.

## Watch the bond approach par

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
Short or long first coupons, business-day payment adjustments, holidays,
ex-coupon trading, fees, and tax treatment are outside this regular-bond lab.
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

## Check your understanding

1. Why does a buyer pay accrued interest when the issuer pays the next coupon in full?
2. What changes when settlement moves from the day before a coupon to the coupon date?
3. Why is a dirty-price drop on a coupon date not itself an investment loss?
4. Why must the YTM solver know whether the entered price is clean or dirty?
5. Why does a zero-coupon bond have no accrued coupon interest here?

**Next:** [Read Treasury bill yield quotations](/lessons/treasury-bill-yields).
