## Start with what the number describes

A Treasury constant-maturity yield describes a point on Treasury's estimated **par curve**. A par coupon rate is the coupon rate that would make a hypothetical regular bond worth face value under the underlying curve. The two-year point on Tuesday and the two-year point on Friday both describe two years remaining. They do not follow one aging bond.

**Goal:** Read the data's rate type and units before calculating a difference. Prerequisite: [yield to maturity](/lessons/yield-to-maturity).

Treasury constructs this curve from indicative bid-side security quotations, rather than completed transactions. A **security quote** belongs to a particular instrument, with its own coupon, maturity, and settlement assumptions. A **YTM** is the single discount rate implied by that instrument's price under a stated convention. A **spot rate** discounts a single future payment. The par observations here supply neither a security price nor a complete set of spot discount factors.

## Derive a curve spread

Let $y_{2,t}$ and $y_{10,t}$ be the annual decimal par yields for the two-year and ten-year tenors on observation date $t$. One basis point is $0.0001$ in decimal yield, so a decimal difference becomes basis points by multiplying by $10{,}000$:

$$
s_t = 10{,}000(y_{10,t}-y_{2,t}),\qquad \Delta s=s_B-s_A.
$$

This is an arithmetic **identity**. A positive spread means the ten-year yield is higher. A widening spread can occur while both yields rise, both fall, or move in opposite directions. If either required rate is missing, this spread is undefined.

## Reproduce the published example

These are **historical observations**, annual percentage yields as published. There are no face-value or settlement inputs because we are comparing rates, not pricing cash flows.

| Date | Two-year | Ten-year | Ten-year minus two-year |
|---|---:|---:|---:|
| November 5, 2026 | 4.46% | 4.84% | 38 bp |
| November 6, 2026 | 4.51% | 4.86% | 35 bp |

In decimals, $10{,}000(0.0484-0.0446)=38$ bp. The two-year rate rose 5 bp and the ten-year rose 2 bp. Therefore the spread narrowed $2-5=-3$ bp. No coupon cash or purchase/sale price appears in this calculation, so it cannot determine a holding-period return.

## Read maturity spacing

The default **Log** maturity axis gives more room to the short tenors. Seven of
the fourteen reported maturities are one year or shorter; a linear 0–30-year
axis puts them in the first 3.3% of its width. Log spacing spreads those points
out so you can inspect the short end as well as the long end.

Equal distances on a log axis mean equal **ratios** of maturity: 1→2 years and
5→10 years have equal spacing. Under **Linear**, equal distances mean equal
additional years. Switch between them before describing the curve's slope.
The numerical rates and spreads do not change. The vertical yield axis stays
linear; a log maturity axis starts at the positive one-month tenor, not zero.

## Which observations can we compare?

Before calculating a change, check whether both inputs exist. **Missing does
not mean zero.** Open either date calendar to see **● published rows**, **— dates
with no published row**, and **? dates outside cached coverage**. These markers
refer to the selected dataset; a published row can still lack individual tenors.
Typing a date updates the status beneath its field before you compare.

Three situations have different meanings:

| Situation | Example in the pinned sample | What it tells you |
|---|---|---|
| Missing tenor on a published date | The February 2025 series-introduction example lacks the 1.5-month value on February 14 | That tenor cannot enter a two-date change |
| No published row within coverage | November 7 in the recent example | There are no rates to compare for that exact date |
| Outside cached coverage | October 30 in the recent example | The pinned November dataset cannot answer the question |

The recent example contains **five published rows, November 2–6**, in a frozen
response covering November 1–7, 2026. All fourteen tenors are present on those
five rows. Dates later in November are outside this acquisition's coverage; a
partial-month sample does not establish what will be published later.

Select **Series introduction** to inspect a real missing-tenor example. Treasury's
1.5-month series began on February 18, 2025 at **4.41%**. Its change from February
14 is undefined. The two-year and ten-year rates exist on both dates, so that
historical example's **21→26 bp spread comparison is valid**. An unrelated missing
tenor should not exclude a valid 2s10s spread. This February sample has 19 published
rows. Reset returns to the recent November example.

Use **Try November 7 · no published row** in the experiment. It selects the recent
sample and changes the first date to November 7. The first curve should disappear,
the November 6 curve should remain, and every two-date change should be excluded.
The viewer keeps your exact date. It does not substitute November 6. An absent
row can reflect nonpublication or a source gap; the feed alone does not establish
the reason. Connecting lines also break at missing tenors rather than inventing
rates between the remaining nodes.

## Predict, then experiment

Before comparing the default dates, predict which maturity rose more. Toggle Log and Linear to see the same observations with different horizontal spacing. Inspect the two curves and reconcile the two tenor changes with the spread change. Then reverse the dates: the changes should reverse sign. Finally choose the same date twice: every available change should be zero. Check that the table still excludes an unavailable tenor rather than displaying a zero change.

Explore another month in either date calendar, choose an exact published date, and press **Compare dates**. The exploration notice explains when the controls differ from the worked example. Cached months work offline; other months load when available online. **Reset example** restores the pinned November observations and dates.

The plotted lines only connect published tenor markers. They do not provide rates for unreported maturities. Treasury's internal curve construction is distinct from this visual guide.

## Misconceptions and limits

A constant-maturity series is not the return on a constant-maturity investment strategy. A strategy would need actual or synthetic securities, cash-flow accounting, and trading rules. Even a higher yield does not establish a better realized investment result. These observations also cannot be inserted as spot rates into a cash-flow valuation without a separately justified curve model.

## Reflect and transfer

Explain why the same ten-year tenor on two dates does not follow the same security. What extra information would you need to price a bond or measure a return? Why can the missing 1.5-month tenor coexist with a valid two-year/ten-year comparison?

**Transfer:** On November 4, 2026, the two-year rate was 4.58% and the ten-year 4.90%. Predict the spread and its change to November 5, then verify those dates in the recent example.

::: answer
The November 4 spread is 32 bp. It widened to 38 bp on November 5, a +6 bp change. Both yields fell: the two-year by 12 bp and the ten-year by 6 bp. A spread can widen while both yields decline.
:::

**Missing-data check:** Suppose three dates have two-year rates, but the middle
date lacks a ten-year rate. How many spreads can you calculate? Would requiring
the new 1.5-month series improve the evidence for that question?

::: answer
Two spreads can be calculated. The middle date is excluded; it is not filled
from a later observation. Requiring an unrelated tenor would only reduce or
preserve the sample. Deeper choices about stale marks and delayed trading belong
to a specified historical strategy, where their effect on results can be tested.
:::

Sources: [Treasury November 2026 observations](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202611&type=daily_treasury_yield_curve), [historical February 2025 observations and series notes](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202502&type=daily_treasury_yield_curve). See [Treasury's methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology) for the indicative quotations and par-curve construction.
