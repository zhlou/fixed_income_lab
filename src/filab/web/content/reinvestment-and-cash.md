## A coupon needs a cash policy

A fixed-coupon bond pays the promised coupon amount. It does not automatically
increase that amount because you reinvested an earlier payment. Interest on a
received coupon comes from a separate investment or cash account.

Prerequisite: [pull-to-par and maturity](/lessons/pull-to-par).

The previous lesson kept coupon receipts at zero interest through redemption.
Now keep the bond's payments the same and change only what its received cash earns.

**Goal:** Reconcile a two-period ledger by hand, then explain why an annual
purchase YTM and a compounded wealth return can differ even when all promised
bond payments arrive.

## State the rate and the clock

The experiment offers two policies: keep all receipts as cash at **0%**, or earn
an explicitly chosen **annual effective cash rate** $r$. This cash rate is
independent of the bond's annual nominal YTM. It applies to all available cash,
including coupons, early-sale proceeds, and principal after redemption.

The cash account uses **Actual/365 Fixed**. For a cash balance $B$ held over
$\Delta d$ actual calendar days, define elapsed cash-account years
$\tau=\Delta d/365$. Then

$$
B_{\text{before receipt}}=B(1+r)^\tau,
\qquad I=B\big[(1+r)^\tau-1\big].
$$

An annual effective rate describes a one-year growth factor of $1+r$. Taking
its fractional power extends that factor consistently to a fraction of a year.
The denominator remains 365 in a leap year. This is a stated account assumption;
the bond still uses Actual/Actual **coupon-period** accrual.

Grow the old balance first, then add today's coupon or sale proceeds. New money
earns from its receipt date onward. At $r=0$ the interest is exactly zero. A
negative cash rate reduces cash; it is not an extra coupon. There is no borrowing
or automatic purchase of additional bonds in this experiment.

## Worked example: two annual periods, no hidden reinvestment

Choose **Cash earns 5%** with the horizon **At maturity**. This case deliberately uses **annual coupons** so
both periods are 365 days and the cash clock matches the bond clock:

- $100 face, 4% coupon, 5% annual YTM, no fees.
- Buy at issue on November 15, 2025; maturity and horizon November 15, 2027.
- First coupon $4 on November 15, 2026; final coupon $4 and principal $100 on
  November 15, 2027.

The purchase amount is

$$
P_0=\frac{4}{1.05}+\frac{104}{1.05^2}=98.140589569.
$$

| Date | Face change | Cash event at 0% | Cash event at 5% |
|---|---:|---:|---:|
| Nov 15, 2025 | +$100 | −$98.140589569 purchase | Same purchase |
| Nov 15, 2026 | $0 | +$4 coupon | +$4 coupon |
| Nov 15, 2027, before new payments | $0 | $0 cash interest | +$0.20 cash interest |
| Nov 15, 2027, payments | −$100 | +$4 coupon, +$100 principal | Same payments |

Opening capital pays for the purchase. No bond remains after redemption.
At zero interest, ending wealth is $4+4+100=108.00$ dollars and the two-year
return is **10.046211%**. At 5% cash interest, the first coupon grows to $4.20:

$$
W_H=4(1.05)+104=108.20,
\qquad R_H=\frac{108.20}{98.140589569}-1=10.25\%.
$$

The $0.20 difference is cash interest, not a change in the bond's coupons or
principal. Dividing period return by two does not give a compounded annual rate.
For these exact two annual periods, the matching compounded annual rate is
$\sqrt{1.1025}-1=5\%$.

## Why matching YTM takes an assumption

For $N$ matching regular periods with periodic YTM $q$, pricing says
$P_0=\sum_k CF_k/(1+q)^k$. Multiply by $(1+q)^N$:

$$
P_0(1+q)^N=\sum_{k=1}^{N}CF_k(1+q)^{N-k}.
$$

The right side is terminal wealth **if each payment really grows at periodic
rate $q$ for its remaining periods**. Pricing alone does not establish that
reinvestment opportunity. The bond's promised-cash-flow internal rate of return
can still be its YTM while terminal wealth under a different cash policy gives
a different compounded return. The [CFA Institute overview](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/interest-rate-risk-and-return)
describes this dependence on reinvestment and investment horizon.

For semiannual nominal YTM $y$, the matching **annual effective** rate for equal
half-year periods is $(1+y/2)^2-1$, rather than $y$. Real calendar half-years
are not all 182.5 days. Our Actual/365 cash account and simple fractional bond
discounting therefore need not reproduce the textbook period identity exactly.
The two-period worked case avoids that mismatch intentionally.

## Experiment and boundary cases

1. Compare **Cash earns 0%** with **Cash earns 5%**. Reconcile the $0.20 difference
   in the table and ledger. The chart isolates the extra wealth from cash
   interest, so the small difference remains visible.
2. Change only the cash rate to 2%. Before calculating, predict a $0.08 increase
   over zero-interest cash. Verify it.
3. Choose the **First coupon** horizon. That coupon has no time to earn
   cash interest yet; the two cash-policy results should match.
4. Set the coupon rate to zero and hold exactly to maturity. There is no
   intervening receipt to reinvest, so cash policies match. Extend the horizon
   to **365 days after maturity**: redeemed principal can now earn cash interest.
5. Use **Full calculator** to carry this case to the complete tool. Export the
   inputs there, change the cash assumption, then import them. Reconcile the
   same ledger before interpreting the result.

The lesson fixes the purchase yield, annual payment frequency, bond dates, face
amount, and zero trading costs. Its three controls vary cash rate, coupon rate,
and the reporting horizon. Broader changes belong in the full calculator.

## Reflection checkpoint

- What additional assumption turns a price/YTM identity into a terminal-wealth result?
- Why is a 5% nominal semiannual yield different from a 5% annual effective cash rate?
- What would change if coupons were withdrawn rather than retained?

## Transfer exercise

A $100 face bond pays $6 after one year and $106 after two years. At a 5% annual
YTM, calculate the purchase price. Hold the first coupon at a 2% annual effective
cash rate for exactly 365 days. Find terminal wealth and the two-year return.

::: answer
Price is $6/1.05+106/1.05^2=101.859410431$ dollars. Terminal wealth is
$6(1.02)+106=112.12$ dollars. The two-year return is 10.073286%, using the unrounded
purchase price. Only $0.12 is interest on the first coupon; the final payment
has no reinvestment interval before this horizon.
:::

Optional reproduction, with the two-period case's exact dates:

```python
from datetime import date
from filab.analytics import BondHolding, YieldPoint, holding_period_ledger

start, end = date(2025, 11, 15), date(2027, 11, 15)
bond = BondHolding("A", 100, .04, start, end,
                   (YieldPoint(start, .05),), frequency=1)
result = holding_period_ledger(holdings=[bond], start_date=start,
                               end_date=end, cash_rate=.05)
print(f"${result.ending_wealth:.2f}")  # $108.20
```
