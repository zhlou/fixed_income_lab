## Time changes the remaining promise

A discount bond costs less than face value, but principal redemption is still
face value if the issuer pays as promised. As that payment gets closer, less
discounting separates it from today. A premium bond instead gives back part of
its premium as it approaches redemption. Coupon income and this price movement
both matter for return.

Prerequisites: [coupons and return](/lessons/coupons-and-return) and
[dated settlement](/lessons/settlement-and-accrued-interest).

**Goal:** Explain pull-to-par under a fixed-YTM assumption, reconcile a
hold-to-maturity return, and account for the final coupon and principal without
leaving a second bond value beside the cash.

The last lesson followed one coupon into cash. Now follow all the remaining
payments through maturity. Keep YTM fixed, retain receipts at 0%, and leave
changes in market yields and cash reinvestment for later lessons.

## Derive the regular-period price gap

First work immediately after coupon dates, where clean equals dirty. Define
face $F$, coupon dollars per period $C$, annual nominal YTM $y$, frequency $m$,
periodic yield $q=y/m$, and $N$ remaining periods. The price is

$$
P_N=C\sum_{k=1}^{N}(1+q)^{-k}+F(1+q)^{-N}.
$$

A bond paying exactly $Fq$ each period prices at par on those dates. Subtract
that par-bond expression:

$$
P_N-F=(C-Fq)\sum_{k=1}^{N}(1+q)^{-k}.
$$

For $q\ne0$, the sum is $[1-(1+q)^{-N}]/q$; for $q=0$ it is $N$. This separate
zero-yield form avoids division by zero. Every discount factor is positive for
$q>-1$. Thus coupon below required yield means a discount; coupon above it means
a premium. With fixed $q$, reducing the remaining number of periods reduces the
size of this price gap. These are **model identities under a fixed yield**, not
predictions of how market yields will move.

Between dates, the existing model uses simple first fractional discounting and
Actual/Actual coupon accrual. Just before maturity the dirty price approaches
$F+C$, while accrued interest approaches $C$. Clean price therefore approaches
$F$. On maturity itself, pay $C+F$ and remove the bond: its **remaining position
value is zero**, not an additional $F$ asset beside the redemption cash.

## Worked example: the continuing discount bond

Select **Discount bond**, with the horizon **At maturity**: $100 face, 4% coupon, semiannual payments; issue
November 15, 2025; buy November 15, 2026 after payment; mature November 15, 2028.
Hold nominal YTM at 5%, use zero-interest cash and no fees.

The opening dirty price is $98.119012896. Four $2 coupons and $100 principal
arrive during the holding period:

| Source of profit | Dollars |
|---|---:|
| Principal less purchase price | $1.880987104 |
| Four coupons | $8.000000000 |
| Cash interest and fees | $0 |
| Total profit | $9.880987104 |

Ending wealth is **$108.00**, entirely cash. The whole-period return is
$108/98.119012896-1=\mathbf{10.070410\%}$. It covers the entire two-year holding
period; the 5% purchase YTM is an annual nominal rate. Payments arrived at
different dates and were held at zero interest.
The model pays the final $2 coupon and $100 principal once each. A maturity
horizon redeems the bond; it creates no additional sale or fee.

The [TreasuryDirect pricing explanation](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/)
provides the coupon/yield premium-discount relationship and principal-redemption
context. This worked return is our own hypothetical calculation.

## Experiment: follow the remaining payments

Keep YTM fixed at 5% while following this price path. At maturity, identify the **$2 final coupon** and **$100 principal repayment** separately in the ledger. Explain how they produce the final $102 receipt.

1. Run the worked maturity case. Find the final coupon and redemption in the ledger.
   Verify zero face held and zero ending bond value.
2. Select **Premium bond**, or change coupon to 6%, keeping 5% YTM. Predict a premium purchase and a capital
   loss toward par, alongside higher coupon income. Reconcile both components.
3. Keep the 4% coupon and choose **Day before maturity**. The position still
   contains the final coupon and principal; redemption
   has not happened yet. Compare clean, accrued, dirty, and cash.
4. Set coupon equal to YTM at 5%. On coupon dates the price is par. Just before
   maturity, distinguish the clean price near $100 from the dirty value near
   $102.50, which still includes the final coupon.
5. Set the coupon to zero. There are no interim coupon receipts or accrued
   interest. At maturity the $100 principal moves to cash and no bond remains.

This lesson exposes coupon, purchase YTM, and a choice between the day before
maturity and maturity itself. Each scenario keeps YTM fixed through time;
changing purchase YTM starts a different fixed-yield scenario. Cash remains at
0% and costs remain zero. The price chart stops before redemption; the terminal
table separately records the final cash payment and zero remaining position,
so redemption does not look like a price collapse.

Use **Full calculator** to continue with your current inputs. The next lesson
changes the [cash policy](/lessons/reinvestment-and-cash); the final lesson
examines [early sale after a yield change](/lessons/holding-period-returns).

## Misconceptions and boundaries

Pull-to-par describes a specified fixed-YTM path. It does not guarantee a smooth
observed clean-price path. Dirty prices fall on payment dates, and between-date
clean prices reflect the fractional pricing convention. Even a bond with coupon
equal to YTM need not be exactly at clean par between dates under this model.

This calculation assumes every promised payment arrives. Redemption at face
does not establish what you could receive if you had to sell earlier. The
early-sale lesson will let the exit yield differ from the purchase yield.

**Roll-down** along a curved term structure asks how the yield assigned to an
aging bond changes as its remaining maturity shortens. That requires a discount
curve and a stated curve evolution assumption; it belongs in the planned discount-curves lessons. Keeping one
YTM fixed here does not measure curved-term-structure roll-down.

## Reflection checkpoint

- Why is redemption principal part of cash, with no remaining bond value?
- Explain how a premium bond can lose capital value and still earn a positive return.
- Why does changing purchase YTM change the purchase price without changing promised payments?
- Why does this lesson not yet establish historical roll-down profits?

## Transfer exercise

A zero-coupon bond promises $100 in two annual periods. Buy at 5% annual YTM.
What is its price and its two-period return if held to redemption? What is its
value after one year if YTM stays at 5%? Ignore costs and keep cash at 0%.

::: answer
Purchase price is $100/1.05^2=$90.702947846. Redemption gives a two-period
return of $100/$90.702947846−1=10.25%. After one year the remaining promise is
worth $100/1.05=$95.238095238, giving a one-year marked return of 5%. At
redemption the bond value becomes zero and cash becomes $100; those are not
two separate $100 assets.
:::
