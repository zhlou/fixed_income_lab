## Read the curve, then its change

On November 5, 2026, the two-year Treasury par yield was **4.46%** and the ten-year was **4.84%**. Their spread was **38 basis points**. On November 6, both yields rose, but the spread narrowed to **35 bp**.

A **yield curve** plots yields against remaining maturity on one observation date. Treasury's **constant-maturity par yield** is the coupon rate that would price a hypothetical bond at face value under its estimated curve. The two-year point always represents two years remaining, so comparing that point across dates follows a maturity, rather than one aging security.

| Observation date | Two-year | Ten-year | Ten-year minus two-year |
|---|---:|---:|---:|
| November 5, 2026 | 4.46% | 4.84% | 38 bp |
| November 6, 2026 | 4.51% | 4.86% | 35 bp |

One basis point is 0.01 percentage point. With yields expressed in percent, subtract and multiply by 100. With decimal rates $y_{10}$ and $y_2$, the same calculation is

$$
s=10{,}000(y_{10}-y_2).
$$

The two-year yield rose **5 bp** and the ten-year rose **2 bp**, so the spread changed by $2-5=\mathbf{-3}$ bp. A positive spread places the ten-year above the two-year. A negative spread means this part of the curve is **inverted**. Widening means the difference increases, which can happen with either rising or falling yields.

These are published par observations. A particular bond has its own coupon, maturity, price, and YTM. To measure an investor's return, follow the purchase price, ending value, and payments received. To value individual future payments from a curve, we will need discount factors in M4.

The chart uses log maturity spacing to keep short maturities readable. Its table gives the actual rates. The [Treasury History Viewer](/tools/treasury-history) includes axis choices, missing-observation examples, a hypothetical revision, and saved datasets.

**Source note.** The observation date identifies the market day. Exact historical publication times are unknown in this dataset. Later downloads can contain revisions, so keep the dataset used for a saved comparison. The example is frozen to the November 7 acquisition. [Treasury observations](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202611&type=daily_treasury_yield_curve) and [curve methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology).

## Try another date

On November 4 the two-year was 4.58% and the ten-year 4.90%. Calculate the spread and its change to November 5, then compare those dates in the experiment.

::: answer
The spread was **32 bp**, widening **6 bp** to 38 bp. Both yields fell. The two-year fell 12 bp while the ten-year fell 6 bp.
:::
