## A blank changes the question you can answer

A missing rate is an absence of evidence for that tenor and date. Zero is an observed numerical value. Replacing a blank with zero invents a large rate movement and can distort every comparison that uses it.

**Goal:** Define which observations support a comparison. Prerequisite: [par yields and quotes](/lessons/par-yields-and-quotes).

Three cases appear in the experiment:

- **Missing tenor:** a published row exists, but one maturity is absent or explicitly null.
- **No published row:** the date is inside the cached period, but the source contains no row. Weekends, nonpublication days, and unexplained source gaps can produce this result. The feed alone does not prove the reason.
- **Outside cached coverage:** the dataset does not cover that date. This says nothing about what Treasury published elsewhere.

## Derive the common sample

Let $A$ and $B$ be the sets of tenors with rates on two dates. Only the intersection $A\cap B$ can support tenor changes. For a spread history, let $D_2$ and $D_{10}$ be the observation-date sets with two-year and ten-year values. Then the valid spread dates are

$$
D_s=D_2\cap D_{10}.
$$

The intersection includes a date only when **both** inputs are available. It is an identity about sample membership, not a rule to fill values. Adding an optional new tenor should not shrink a two-year/ten-year sample unless that tenor is actually required for the question.

## Reproduce a series introduction

Treasury's 1.5-month series began on February 18, 2025. In the pinned response, February 14 has no 1.5-month field. February 18 has **4.41%**, or **0.0441** as an annual decimal rate. The change between those dates is undefined. It is not +441 bp.

Both dates have two-year and ten-year rates, so their 21 bp and 26 bp spreads remain comparable. The missing short tenor does not invalidate that particular question. The fixture has 19 published rows, all with the two-year and ten-year rates.

## Predict, then experiment

Predict the 1.5-month change before opening its table row. Then use **Try February 17**: the first curve should disappear because there is no published row for that date. The second curve stays visible; every two-date change becomes unavailable. The viewer does not move the first date to February 14.

Next choose March 3 as the first date. That date is outside the pinned February coverage. Finally compare February 18 with itself: an observed zero change should appear, while an absent observation would still be excluded.

Connecting points across a missing tenor can suggest a smooth curve that was never supplied. The chart breaks those connections and lists exact values in the table. No forward fill or future backfill is performed.

## Misconceptions and boundaries

A weekday without a row is not automatically a data error, and an absent row is not automatically a confirmed holiday. A rate can legitimately be zero. Missing-value handling must inspect presence, not whether a numerical value is truthy. Earlier history also contains discontinued or newly introduced series; modern coverage cannot be assumed for every year.

## Reflect and transfer

Why would selecting a nearby date change a research question? Why could filling a missing observation from the next day create look-ahead bias?

**Transfer:** Suppose three dates have two-year rates, but the middle date lacks a ten-year rate. How many spreads can be computed? Would requiring the new 1.5-month series improve that sample?

::: answer
Two spreads can be computed. The middle date is excluded. Requiring an unrelated tenor would reduce or preserve the sample, not improve the evidence for the two-year/ten-year spread. The correct required-input set follows from the question.
:::

Source: [Treasury series notes and February table](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202502&type=daily_treasury_yield_curve). The published history documents changes in tenor availability.
