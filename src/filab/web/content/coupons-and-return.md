## A payment changes where the value sits

Just before a coupon, a bond's full price includes the payment about to arrive.
After payment, that coupon is no longer part of the remaining bond. It is cash
in the owner's account. The dirty-price drop alone is therefore a poor measure
of that owner's return.

Prerequisites: [holding-period return](/lessons/holding-period-returns) and
[settlement and accrued interest](/lessons/settlement-and-accrued-interest).

**Goal:** Cross a coupon date and account for both the accrued interest paid at
purchase and the coupon received. Explain who receives a payment under this
model's settlement convention.

## Accrued interest belongs in the purchase cost

Let $F$ be face value, $c$ the annual decimal coupon rate, and $m$ payments per
year. Each regular coupon is $C=Fc/m$. Let $a$ be actual days elapsed since the
previous coupon, and $d$ the actual number of days in that coupon period.
Accrued interest is $AI=C(a/d)$.

Write $P^c$ for clean price, $P^d$ for dirty price, and subscripts $0,H$ for
purchase and sale dates. The settlement identity is

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
return equation. It is not a causal attribution model. With cash interest add
that interest; with fees subtract those fees. Return divides total profit by
dirty purchase cost plus the entry fee.

## Worked example: buy one day before the coupon

Choose **Buy before the coupon**. All dates and prices here are hypothetical:

- $100 face, 4% coupon, semiannual payments, 5% nominal YTM held fixed.
- Issue November 15, 2025; maturity November 15, 2028.
- Buy November 14, 2026; sell November 16, 2026. No fees; cash earns zero.

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

Ending wealth after that hypothetical sale is **$100.13**, and the two-day return is
**+0.026797%**. The dirty sale price alone is **$98.13**, about $1.97 below the
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

1. Use the worked case. The experiment **keeps the bond at the horizon** and
   compares its dirty value with bond value plus cash. With no sale costs, that
   marked wealth equals the worked example's hypothetical sale wealth.
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
wider date window or examine an actual horizon sale.

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

- Reconcile the worked $2 coupon with only about three cents of profit.
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
