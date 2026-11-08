## Give every payment its own price

Our $100-face, 4% note pays $2 after six months, $2 after one year, $2 after eighteen months, and $102 after two years. Under the hypothetical discount curve below, those payments are worth **$97.60 today**.

A **discount factor**, $D(t)$, is today’s value of $1 paid in $t$ years. Multiplying each payment by its factor puts the payments in the same date’s dollars. Their sum is the bond’s price.

| Years until payment | Payment | Discount factor | Present value |
|---|---:|---:|---:|
| 0.5 | $2 | 0.99 | $1.98 |
| 1 | $2 | 0.97 | $1.94 |
| 1.5 | $2 | 0.94 | $1.88 |
| 2 | $102 | 0.90 | $91.80 |
| Total | $108 | | **$97.60** |

For payments $CF_i$ in dollars at times $t_i$ in years, the pricing identity is

$$P=\sum_i CF_i D(t_i).$$

Different horizons can have different discount rates. The continuously compounded **spot rate** $z(t)$ summarizes one payment’s factor through $D(t)=e^{-z(t)t}$. A bond’s YTM instead summarizes the price of its whole payment stream using the [quotation convention from lesson 1](/lessons/present-value).

## Recover a factor from a coupon bond

Suppose the first three factors are known. A second $100-face bond pays a 6% annual coupon semiannually and has a full price of **$101.40**. Its first three $3 payments are worth $3(0.99+0.97+0.94)=\$8.70$. Its final payment is $103. Therefore

$$D(2)=\frac{101.40-8.70}{103}=0.90.$$

Recovering factors in payment order is **bootstrapping**. Once earlier payments have been valued, the next instrument reveals the value of its final payment. Substituting the recovered factor into our 4% note gives $5.80+102(0.90)=\$97.60$.

The experiment holds the first three factors fixed. Change the calibration price to **$100.37**, inspect the new factor, and reconcile the 4% note’s new price. Reset restores $101.40. These are hypothetical full-period prices with zero accrued interest.

## Change one input

What factor and note price would a calibration price of $100.37 imply?

::: answer
The final factor becomes $(100.37-8.70)/103=0.89$. The 4% note is worth $5.80+102(0.89)=\$96.58$. Only its final payment’s present value changes in this experiment.
:::

The [Discount Curve Explorer](/tools/discount-curves) shows the factors and payment values together, with a separate historical data view.
