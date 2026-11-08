## Four payments, one price

A fixed-rate bond promises interest payments called **coupons**, followed by repayment of its **face value** at maturity. Our hypothetical note has **$100 face**, a **4% annual coupon**, and **two years remaining**. It pays twice a year, so each coupon is $100\times0.04/2=\mathbf{\$2}$.

| Years from purchase | Coupon | Principal | Total payment |
|---|---:|---:|---:|
| 0.5 | $2 | $0 | $2 |
| 1.0 | $2 | $0 | $2 |
| 1.5 | $2 | $0 | $2 |
| 2.0 | $2 | $100 | $102 |

You receive $108 in total, spread over time. At a **5% annual nominal yield compounded semiannually**, those payments are worth **$98.12 today**. We begin immediately after a coupon payment, with no accrued interest, fees, or taxes.

## Reverse growth to find today's value

An annual nominal yield $y$ with $m$ compounding periods gives a period rate $r=y/m$. Here $r=0.05/2=0.025$, or 2.5% per half-year. One dollar today grows to $1+r$ after one period. After $k$ periods, an amount $PV$ grows to $PV(1+r)^k$. To match a payment $CF_k$ due then, solve

$$
PV(1+r)^k=CF_k
\quad\Longrightarrow\quad
PV_k=\frac{CF_k}{(1+r)^k}.
$$

The multiplier $1/(1+r)^k$ is the **discount factor**. The first $2 coupon has present value $2/1.025=\$1.95$. Add the present values of all four payments to get price $P$.

$$
\begin{aligned}
P&=\sum_{k=1}^{4}\frac{CF_k}{(1+y/2)^k}\\
&=\frac{2}{1.025}+\frac{2}{1.025^2}
+\frac{2}{1.025^3}+\frac{102}{1.025^4}\\
&=98.119012896\ldots\approx\boxed{\$98.12}.
\end{aligned}
$$

The experiment shows each payment and its discounted value. Raise the yield while keeping the payments fixed. Each discount factor falls, and so does price. At a 4% yield the price is $100, called **par**. Below $100 the bond trades at a **discount**. Above $100 it trades at a **premium**.

At zero yield, every discount factor is one and price equals the $108 receipts. Negative yields can make price exceed those receipts, provided the period growth factor stays positive. Prices are displayed to cents, with full precision retained in the calculation.

## Run the same equation backward

Switch to **Yield from price** and enter $98.12. **Yield to maturity (YTM)** is the single rate that makes the discounted payments equal that purchase price. The calculator varies $y$ in the same sum and obtains **4.9995%**. It differs slightly from 5% because the entered price was rounded to cents.

| Rate | Calculation or meaning | At $98.12 |
|---|---|---:|
| Coupon rate | $4 annual coupons / $100 face | 4.00% |
| Current yield | $4 annual coupons / purchase price | 4.08% |
| YTM | Rate accounting for every payment and its timing | 4.9995% |

Current yield leaves out the gain from buying below the $100 redemption amount. YTM captures that difference through the payment schedule. What you ultimately earn also depends on when you sell and how you use the coupons, which we calculate in lessons 6 and 7.

Treasury notes and bonds pay semiannually. The experiment fixes that convention so changing yield or price isolates this relationship. A Treasury bill pays only at maturity and uses a different quote convention. The [Treasury Bill Calculator](/tools/treasury-bills) translates its quote into price and return.

## Try a different price

Before entering $100 and then $108, predict the YTM for each price. Explain your answer using the four promised payments.

::: answer
At **$100**, YTM equals the **4%** coupon rate under these matching conventions. At **$108**, YTM is **0%**, since the price equals all four undiscounted receipts. In both cases the payments remain $2, $2, $2, and $102.
:::
