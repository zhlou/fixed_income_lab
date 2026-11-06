## Price is one part of the investment

A bond price tells you what the remaining payments are worth on one date.
A **holding-period return** asks what happened to the investor's whole wealth
between two dates. During that time, a coupon can leave the bond and arrive in
cash. Looking only at the bond price loses sight of that cash.

Prerequisites: [coupons and accrual](/lessons/coupons-and-return),
[pull-to-par and maturity](/lessons/pull-to-par), and
[reinvestment and cash](/lessons/reinvestment-and-cash).

You have followed a coupon into cash, reconciled redemption, and given receipts
an explicit cash policy. Now combine those pieces for an investor who may sell
before maturity. The earlier [risk lessons](/lessons/modified-duration-dv01)
change yield instantly; this investment also ages and makes payments.

**Goal:** Reconcile a return from beginning wealth, ending bond value, credited
cash, and trading costs. Explain why a purchase YTM is not a shorter-horizon
return forecast.

## Put the pieces into one wealth calculation

This calculator models a **closed portfolio**: all capital is present at the
opening, and there are no later contributions or withdrawals. Coupons stay
inside it. Buying a bond moves cash into a position; selling reverses the move.
Neither trade is a new contribution.

Use these symbols, all in matching dollar units:

| Symbol | Meaning |
|---|---|
| $P_0^d$ | Full dirty purchase price for the chosen face amount |
| $P_H^d$ | Full dirty sale price for the same face amount, if sold |
| $K_b$ | Purchase fee |
| $W_0$ | Beginning wealth, $P_0^d+K_b$ |
| $V_H$ | Dirty value of any bonds still held at horizon $H$ |
| $B_H$ | Cash balance at that horizon, including payments, cash interest, and sales, net of costs |
| $W_H$ | Ending wealth, $V_H+B_H$ |
| $R_H$ | Net return over the entire holding period |

Profit is the wealth left over after recovering the capital committed. Divide
that profit by the committed capital:

$$
R_H=\frac{W_H-W_0}{W_0}=\frac{V_H+B_H}{W_0}-1.
$$

This is an **accounting identity**, given the closed-portfolio boundary. For an
early sale of one bond, cash earning zero throughout, total coupons $C_H$, and
sale fee $K_s$, the same identity becomes

$$
R_H=\frac{P_H^d+C_H-K_s-(P_0^d+K_b)}{P_0^d+K_b}.
$$

Once $C_H$ has been credited into $B_H$, use the first formula without adding
it again. [FINRA's return explanation](https://syndication.finra.org/content/key-concepts-return-and-rate-return)
likewise distinguishes investment earnings, changes in value, and expenses.

## Worked example: a coupon cushions an early-sale loss

Use **Yield rises to 7%**. This is a hypothetical scenario, not a forecast:

- $100 face, 4% annual coupon, semiannual payments; issue November 15, 2025,
  maturity November 15, 2028.
- Purchase on November 15, 2026, after payment, at 5% annual nominal YTM.
- Sell on May 15, 2027, after receiving the $2 coupon. On that date YTM becomes
  7%; cash earns 0% and fees are zero.

At purchase four payments remain. With periodic yield $0.05/2=0.025$:

$$
P_0^d=\frac{2}{1.025}+\frac{2}{1.025^2}
+\frac{2}{1.025^3}+\frac{102}{1.025^4}
=98.119012896.
$$

At sale three payments remain, discounted at $0.07/2=0.035$:

$$
P_H^d=\frac{2}{1.035}+\frac{2}{1.035^2}
+\frac{102}{1.035^3}=95.797544529.
$$

| Item | Dollars |
|---|---:|
| Beginning wealth | $98.12 |
| Sale proceeds | $95.80 |
| Coupon already in cash | $2.00 |
| Ending wealth | $97.80 |
| Net profit | −$0.32 |

Using unrounded values gives a **−0.327631%** holding-period return. The dirty
price change alone is about **−2.37%**. The coupon reduces the loss, but does not
eliminate it. Neither percentage is the purchase YTM of 5%.

The [maturity lesson](/lessons/pull-to-par) kept the bond through redemption.
Here the investor sells before that final payment. The promise of $100 at
maturity does not set today's sale price. If held through redemption with all
promised payments arriving, interim yield marks would not change those payments;
cash reinvestment would still be a separate assumption.

## Experiment: explain each change

1. Run the worked case. Find the coupon before the sale in the event ledger.
2. Choose **Yield stays at 5%**, or set the horizon YTM to 5%. The dates and
   coupons stay fixed. Which terminal price changes?
3. Add a 10 bp trading cost. At $100 face this means $0.10 to purchase and $0.10
   to sell. Beginning wealth rises by the entry fee; ending cash falls by the
   exit fee. Each is charged once.
4. Choose **Keep & value**. At zero cost, marked wealth equals hypothetical
   sale wealth at the same price. With a sale cost, the marked result has not
   yet paid that exit cost. Its remaining value is still exposed to future risk.
5. Compare the two percentage curves. Price change uses dirty purchase price as
   its base; investment return uses opening capital including entry costs. With
   a positive entry fee, the initial marked return is already negative.

This lesson fixes the bond terms, dates, and zero-interest cash policy so you
can isolate the exit yield and costs. The **Full calculator** link carries your
current inputs to the dedicated tool. There you can also apply the earlier
cash-policy lesson to received payments.

Multiple-position comparisons are an optional extension in the full calculator.
First reconcile the single bond's purchase, coupon, sale or remaining value,
and fees before adding another position.

## Conventions and common mistakes

The displayed return covers the **whole period**, with no annualization. The
model assumes same-day trade and settlement, contractual unadjusted dates, no
default, and no tax. It preserves the existing dated pricing conventions:
Actual/Actual coupon-period accrual and simple first fractional discounting.
Stub coupons, holidays, ex-coupon rules, and settlement lags are excluded.

In this lesson YTM changes on the horizon date. The coupon is received first,
then the remaining bond is valued or sold at the exit YTM. Earlier marks use
the purchase YTM. These are hypothetical model prices; no observed market
history is used. A shorter horizon still depends on the sale price and
cash treatment; the [SEC's early-sale explanation](https://www.investor.gov/introduction-investing/investing-basics/glossary/bonds-selling-maturity)
describes the possibility of selling above or below face value.

Do not compare a six-month period return directly with an annual yield. Do not
mistake an unrealized mark for cash received. External deposits would require a
different return treatment; this closed-portfolio formula does not support them.

## Reflection checkpoint

- Explain the difference between dirty price change, dollar profit, and return.
- Why is the coupon in ending cash rather than added to wealth a second time?
- Why does a marked position still carry risk after this horizon?

## Transfer exercise

A hypothetical position costs $99 dirty plus a $0.10 purchase fee. You receive
$2 in coupons, then sell for $98 dirty and pay a $0.10 sale fee. Cash earns zero.
Calculate ending wealth and the period return before revealing the answer.

::: answer
Beginning wealth is $99.10. Ending wealth is $98+$2−$0.10=$99.90. Profit is $0.80
and return is $0.80/$99.10=0.807265%. The bond's $1 price decline does not by
itself describe the investment outcome.
:::

Reuse the [Bond Return Calculator](/tools/bond-return) and save the inputs. Record
your own reconciliation in the M2 learning journal; publishing the software does
not complete that reflection.
