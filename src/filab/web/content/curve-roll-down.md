## The curve stays still while the payments move

The hypothetical curve from [the previous lesson](/lessons/discount-factors) assigns factors of 0.99, 0.97, 0.94, and 0.90 to half-year steps. Our $100-face, 4% note begins at **$97.60**.

Six months later the investor receives **$2.00**. Immediately after that payment, the remaining note is worth **$99.80** if the curve has the same shape by *remaining maturity*. The bond’s future payments now occupy shorter horizons.

| Remaining years after six months | Remaining payment | Factor | Present value |
|---|---:|---:|---:|
| 0.5 | $2 | 0.99 | $1.98 |
| 1 | $2 | 0.97 | $1.94 |
| 1.5 | $102 | 0.94 | $95.88 |
| Total | $106 | | **$99.80** |

This passage along a maturity curve is often called **roll-down**. Its effect depends on the curve’s shape and the remaining cash flows. An unchanged curve by remaining maturity is a hypothetical scenario. Future curves can move.

For an aging horizon $h$, retain payments with $t_i>h$ and move their discount horizons to $t_i-h$:

$$P_h=\sum_{t_i>h}CF_iD(t_i-h).$$

The price change is $99.80-97.60=\$2.20$. With the received coupon held at zero interest, ending wealth is $99.80+2=\$101.80$. To compute the holding-period return, use that wealth and the original purchase price as in [lesson 7](/lessons/holding-period-returns). The chart’s price change and coupon cash both enter that reconciliation.

Advance the experiment from six months to one year. Inspect which payments remain, and account for the coupon cash. Reset returns to six months. Settlement here uses exact half-year periods and occurs after payment. There are no fees.

## A forward rate implied by today’s factors

Today, $0.99 buys $1 at six months, while $0.97 buys $1 at one year. Their ratio implies the growth factor between those dates. An annual simple forward rate $f_{a,b}$ for years $a$ to $b$ satisfies

$$1+f_{a,b}(b-a)=\frac{D(a)}{D(b)}.$$

For a six-month interval, annualizing by multiplying by two also gives a nominal semiannual quote:

$$f_{0.5,1}=2\left(\frac{0.99}{0.97}-1\right)=4.1237\%.$$

This rate is implied by today’s relative prices of dated payments. The observed six-month rate at that future date can differ. Risk compensation and changing information affect those prices and future rates.

## Change one input

After one year, what are the remaining price and coupon cash under the unchanged curve?

::: answer
The remaining payments are $2 in six months and $102 in one year. Price is $2(0.99)+102(0.97)=\$100.92$. The two received coupons total $4.00. At zero cash interest, ending wealth is $104.92. At maturity, all $108 of original payments have arrived and the remaining bond value is zero.
:::
