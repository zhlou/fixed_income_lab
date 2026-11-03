## One bond, one changing variable

**Goal:** Explain a price change by identifying which payments or discount rates changed. Prerequisite: [present value and bond pricing](/lessons/present-value).

We now use **$100 face**, one tenth of the first two lessons' $1,000 example. A price of $92.21 per $100 face means $922.10 for $1,000 face if scaling that rounded quote. The calculator keeps unrounded values internally.

Each comparison is valued just after a coupon date, with no accrued interest, taxes, or fees. Before moving a control, predict the result and name what stays fixed.

The dashed curve is always the same original bond: **10 years remaining,
4% annual coupon, $100 face value, semiannual payments**. The solid curve
is your selected bond. Every tab plots **price versus YTM**, using the same
0–10% yield range and $0–250 price range.

The **Compare at YTM** control moves the markers to a particular yield and
sets the starting yield for the table. It does not change either price curve.
These are hypothetical pricing scenarios, not a Treasury yield curve or
predictions of future rates.

## The calculation behind each curve

Let $P(y)$ mean “the price calculated at annual nominal decimal YTM $y$.” With $N$ half-year periods remaining and annual decimal coupon rate $c$, each coupon is $C=100c/2$. The previous lesson's formula becomes:

$$
P(y)=\sum_{k=1}^{N}\frac{C}{(1+y/2)^k}+\frac{100}{(1+y/2)^N}.
$$

Each point on a curve repeats this calculation at a different yield. The horizontal axis is a rate, not a date; moving along it does not age the bond.

## 1. Maturity: move the principal repayment date

Only the maturity control is enabled. The annual coupon stays at 4%, so
each half-year payment is $2 per $100 face value. Changing maturity changes
how many coupons remain and when the $100 principal is repaid.

Try 2, 10, and 30 years. All these curves pass through par at a 4% YTM.
At other yields, the curves separate. Longer maturity generally produces
a larger percentage response to a shared yield change for these bonds.
Use the table to check that relationship rather than judging dollar slopes
alone. Selecting 10 years reproduces the original bond, so the curves coincide.

## 2. Coupon: change the size of each payment

Only the coupon control is enabled; maturity stays at 10 years. Increase
the annual coupon from 4% to 6%: each half-year coupon rises from $2 to $3.
Principal is still $100, repaid on the same date.

At any fixed YTM, larger promised payments produce a higher price.
The selected bond is at par when YTM equals its coupon rate. A 4% coupon
matches the baseline and makes the curves coincide.

## 3. Payment timing: periodic coupons or one final payment

Switch between a 4% coupon bond and a zero-coupon bond. Both mature in
10 years. The coupon bond pays $2 every six months and repays $100 at
maturity; the zero-coupon bond pays only $100 at maturity.

The price axis remains in dollars. The zero-coupon bond has a lower price
because it promises less total cash. This comparison changes payment
amounts as well as timing, so a dollar-price difference alone does not
measure relative interest-rate sensitivity.

A **basis point (bp)** is 0.01 percentage point: 100 bp is a move from 5% to 6%, or 0.01 in decimal yield.

Use the **percentage change column** to compare sensitivity to the same
100-basis-point shock. Starting at a 5% YTM, the zero-coupon bond loses
about 9.27%, versus 7.68% for the coupon bond. Receiving some cash earlier
reduces the coupon bond’s percentage sensitivity in this comparison.

## Read the payment timeline

The small timeline shows your selected bond’s promised payments. Coupons
and principal use separate labeled dollar scales so the coupons stay
readable. Hover over a bar for its payment date and amount. When there
are no coupons, only the principal panel appears.

## A yield shock is not a year of investment return

The table reprices both bonds after the same **+100 basis points**, or
one-percentage-point, increase in YTM:

$$
\frac{\Delta P}{P}=\frac{P(y+0.01)}{P(y)}-1.
$$

Here $\Delta P$ means new price minus initial price, so a loss is negative. For the original ten-year 4% coupon bond, the unrounded prices at 5% and 6% YTM display as **$92.21** and **$85.12**. Their difference displays as **−$7.08**, and dividing the unrounded difference by the unrounded starting price gives **−7.68%**. Subtracting the two already-rounded prices would instead give −$7.09.

Each percentage uses that bond’s own initial price. No time passes,
maturity stays fixed, and no coupons arrive between the two valuations.
A holding-period return must also account for elapsed time, received
coupons, reinvestment, and sale value.

## Transfer exercise

Use the Maturity tab with two years remaining and Compare at YTM at 4%. Predict the selected bond's price and its change after the table's +100 bp shock.

::: answer
The starting price is **$100.00** because coupon and YTM match. At 5% YTM it is **$98.12**. The immediate change is **−$1.88**, or **−1.88%**, using unrounded values. Its remaining payments are still $2, $2, $2, and $102.
:::

## Try explaining the relationships

1. In Maturity, why do the curves meet at par when YTM is 4%?
2. In Coupon, why does increasing the coupon raise price at a fixed YTM?
3. Why is a zero-coupon bond’s lower price not evidence that it is a bargain?
4. Why should you use the table’s percentages to compare relative sensitivity?
5. What changes when you move Compare at YTM, and what stays unchanged?

**Next:** [Solve yield to maturity from a bond price](/lessons/yield-to-maturity), and compare coupon rate, current yield, and YTM.
