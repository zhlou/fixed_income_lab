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
| February 14, 2025 | 4.26% | 4.47% | 21 bp |
| February 18, 2025 | 4.29% | 4.55% | 26 bp |

In decimals, $10{,}000(0.0447-0.0426)=21$ bp. The two-year rate rose 3 bp and the ten-year rose 8 bp. Therefore the spread widened $8-3=5$ bp. No coupon cash or purchase/sale price appears in this calculation, so it cannot determine a holding-period return.

## Predict, then experiment

Before comparing the default dates, predict which maturity rose more. Inspect the two curves and reconcile the two tenor changes with the spread change. Then reverse the dates: the changes should reverse sign. Finally choose the same date twice: every available change should be zero. Check that the table still excludes an unavailable tenor rather than displaying a zero change.

The plotted lines only connect published tenor markers. They do not provide rates for unreported maturities. Treasury's internal curve construction is distinct from this visual guide.

## Misconceptions and limits

A constant-maturity series is not the return on a constant-maturity investment strategy. A strategy would need actual or synthetic securities, cash-flow accounting, and trading rules. Even a higher yield does not establish a better realized investment result. These observations also cannot be inserted as spot rates into a cash-flow valuation without a separately justified curve model.

## Reflect and transfer

Explain why the same ten-year tenor on two dates does not follow the same security. What extra information would you need to price a bond or measure a return?

**Transfer:** On February 13, the two-year rate was 4.31% and the ten-year 4.52%. Predict the spread and its change to February 14, then verify those dates in the experiment.

::: answer
The February 13 spread is 21 bp, so its change to February 14 is zero. Both rates fell 5 bp. An unchanged spread does not imply unchanged yields or unchanged bond prices.
:::

Source: [Treasury February 2025 observations and definitions](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202502&type=daily_treasury_yield_curve). See [Treasury's methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology) for the indicative quotations and par-curve construction.
