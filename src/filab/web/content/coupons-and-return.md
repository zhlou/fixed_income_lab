## A payment changes where the value sits

Just before a coupon, a bond's full price includes the payment about to arrive.
After payment, that coupon is no longer part of the remaining bond. It is cash
in the owner's account. The dirty-price drop alone is therefore a poor measure
of that owner's return.

Prerequisite: [settlement and accrued interest](/lessons/settlement-and-accrued-interest).

**Goal:** Calculate a simple holding-period return, then cross a coupon date
without mistaking a payment for new profit or a price drop for a wealth loss.

## Start with the money invested and the money left

A **holding-period return** compares what an investment is worth at the end
with the money put in at the beginning. For this first experiment, buy one
bond, keep every receipt as cash at 0%, and pay no fees. There are no later
deposits or withdrawals.

In a hypothetical example, pay $100 dirty, then later hold a bond worth $99
dirty and $2 of coupon cash. Ending wealth is $101, profit is $1, and the
period return is 1%. The $1 bond-price decline describes only part of the
outcome. Selling for the same $99 with no fees leaves $101, now entirely cash.

Write $P_0^d$ for the full dirty purchase price, $V_H^d$ for the dirty value of
the bond still held at ending date $H$, and $B_H$ for the coupon cash received.
All three amounts refer to the same face value and are in dollars. Ending
wealth is $V_H^d+B_H$. Subtract the purchase cost to find profit:

$$
\text{profit}=V_H^d+B_H-P_0^d.
$$

Return is profit per dollar invested:

$$
R_H=\frac{V_H^d+B_H-P_0^d}{P_0^d}.
$$

This is an **accounting identity** under the stated assumptions. It covers the
whole holding period, with no annualization. Count coupon cash once in ending
wealth. We will add reinvestment and trading costs in later lessons.

## Accrued interest belongs in the purchase cost

Let $F$ be face value, $c$ the annual decimal coupon rate, and $m$ payments per
year. Each regular coupon is $C=Fc/m$. Let $a$ be actual days elapsed since the
previous coupon, and $d$ the actual number of days in that coupon period.
Accrued interest is $AI=C(a/d)$.

Write $P^c$ for clean price, $P^d$ for dirty price, and subscripts $0,H$ for
purchase and ending valuation dates. The settlement identity is

$$
P^d=P^c+AI.
$$

The buyer pays the dirty amount, compensating the seller for elapsed coupon
time. Receiving the next full coupon does not make all of it new profit.
[TreasuryDirect's purchase explanation](https://www.treasurydirect.gov/marketable-securities/buying-a-marketable-security/)
explains why accrued interest can be part of a Treasury purchase amount.

Subtract the two dirty prices and add the coupons actually received. With
zero cash interest and no fees:

$$
\text{profit}=(P_H^c-P_0^c)+(AI_H-AI_0)+\sum_i C_i.
$$

This is an **identity**, obtained by substituting clean plus accrued into the
profit equation above. It is not a causal attribution model. Here return
divides this profit by the dirty purchase cost. Later lessons add cash interest
and trading costs explicitly.

## Worked example: buy one day before the coupon

Choose **Buy before the coupon**. All dates and prices here are hypothetical:

- $100 face, 4% coupon, semiannual payments, 5% nominal YTM held fixed.
- Issue November 15, 2025; maturity November 15, 2028.
- Buy November 14, 2026; value the bond still held on November 16, 2026.
  No fees; cash earns zero.

The current coupon period is May 15–November 15, 2026: **184 days**.
At purchase **183 days** have elapsed. Each coupon is $2, so

$$
AI_0=2\frac{183}{184}=1.989130435.
$$

The dated pricer gives a clean purchase value of $98.116281182. You pay
$100.105411617 dirty. On November 15 the $2 coupon is credited to cash; accrued
interest resets to zero. On November 16 one of the new period's 181 days has
elapsed, so $AI_H=2/181=0.011049724$.

| Component | Full-precision dollars, shortened for reading |
|---|---:|
| Change in clean price | +0.004905576 |
| Change in accrued interest | −1.978080711 |
| Coupon received | +2.000000000 |
| Profit | +0.026824865 |

Ending wealth is **$100.13**, and the two-day return is
**+0.026797%**. The remaining dirty bond value is **$98.13**, about $1.97 below the
dirty purchase price. That comparison omits the $2 already in cash. The calculator
keeps full precision; cent-rounded displays can differ by one cent when summed.

## Who gets a coupon on a trade date?

This educational model places settlement **after payment** on a coupon date:

| Event | Treatment |
|---|---|
| Buy on a coupon date | The new buyer does not receive that date's coupon |
| Own before the date, then sell on it | Credit the coupon to the seller, then sell the remaining bond |
| Reach maturity while holding | Credit the final coupon, redeem principal once, leave zero face held |
| Value after a payment | Include the credited cash and only the remaining bond payments |

Cash earns through the elapsed interval before new receipts are credited. A
coupon received at the horizon earns no cash-account interest before that same
horizon. A valuation is a measurement: it changes neither cash nor face held.

Actual securities can involve settlement lags, holiday changes, record dates,
and ex-coupon rules. Those are excluded here. The table states this model's
ordering, rather than a universal rule for all bond markets.

## Experiment: follow one coupon through the ledger

1. Use the worked case. The experiment **keeps the bond at the horizon**.
   Compare its dirty value with bond value plus cash, then divide the total
   profit by the dirty purchase cost to reproduce the period return.
2. Set the valuation date to November 15. Accrued interest resets to zero;
   the coupon has already been credited before the closing valuation.
3. Choose **Buy on the coupon date**. The opening-date coupon disappears from
   this investor's ledger. Explain why.
4. Inspect the dated numerical table. On a payment date, dirty bond value falls
   while cash rises. Total wealth includes both. The vertical chart marker is
   the November 15 coupon date when it lies within your selected window.
5. Turn the coupon rate to zero. There is no coupon-date cash jump and no
   accrued interest. Principal still redeems at maturity.

The date controls stay near this coupon, while YTM, face amount, cash policy,
and costs are fixed. Use **Full calculator** to carry the current case into a
wider date window. Next, [follow the bond through maturity](/lessons/pull-to-par).

## Misconceptions and boundaries

A clean quote is not the full capital required. Accrued interest paid is not a
fee, and a coupon receipt is not all incremental earnings. Never add accrued
interest separately after already using dirty prices. Likewise, never add
coupons separately after already using the full cash balance.

The gap across two calendar dates also includes elapsed time and any assumed
yield change; it need not equal the coupon exactly. The accounting identity
still holds. Contractual payment dates are processed even when the chart has
only a few valuation dates.

## Reflection checkpoint

Find the $2 coupon in the ledger. Reconcile its transfer from accrued interest in the purchase price to cash after payment, then explain the **$0.026824865** two-day profit using the table’s four components.

- Reconcile the worked $2 coupon with only about three cents of profit.
- Why does a fall in bond value alone not determine the investment return?
- Why does accrued interest fall sharply without creating an equal wealth loss?
- Explain the difference between a coupon date purchase and a coupon date sale.

## Transfer exercise

You pay $99 clean plus $1.50 accrued. Later you receive a $2 coupon and sell for
$99.10 clean plus $0.20 accrued. There are no fees or cash interest. Calculate
profit and return using both dirty prices and the clean/accrual decomposition.

::: answer
Purchase dirty is $100.50; sale dirty is $99.30. Ending wealth is $101.30,
including the $2 coupon. Profit is $0.80 and return is 0.796020%. The decomposition
is $0.10 clean gain − $1.30 accrued change + $2 coupon = $0.80.
:::
