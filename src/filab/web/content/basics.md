## The starting idea

A bond is a contract specifying payments from a borrower (the **issuer**) to an investor (the **holder**). To understand a plain fixed-rate bond, first list how much it pays and when. Pricing then asks: **What are those future payments worth today?**

**Goal:** Read a bond's terms and build its payment timeline. No prior bond knowledge is needed.

This lesson focuses on conventional nominal Treasury bills, notes, and bonds. Here **nominal** means amounts stated in dollars, without adjustment for inflation. Inflation is a rise in the general price level: a fixed dollar payment may buy less in the future. Inflation-linked securities adjust payments for inflation; floating-rate securities reset their interest rates. Both need additional rules and come later. All numerical examples here are hypothetical.

## 1. The Treasury family

| Term | Meaning | Payment pattern |
|---|---|---|
| **Treasury security** | Debt issued by the U.S. Treasury to borrow money. | Depends on the instrument. |
| **Treasury bill (T-bill)** | Short-term Treasury debt with an original term of up to one year. | No periodic coupons; pays face value at maturity. Usually purchased below face value, though issuance at par is possible. |
| **Treasury note (T-note)** | Fixed-rate Treasury debt currently issued with original terms of 2, 3, 5, 7, or 10 years. | Pays coupons every six months and principal at maturity. |
| **Treasury bond (T-bond)** | Fixed-rate Treasury debt currently issued with original terms of 20 or 30 years. | Pays coupons every six months and principal at maturity. |

These instrument descriptions follow TreasuryDirect: [bills](https://www.treasurydirect.gov/marketable-securities/treasury-bills/), [notes](https://www.treasurydirect.gov/marketable-securities/treasury-notes/), and [bonds](https://www.treasurydirect.gov/marketable-securities/treasury-bonds/). Note and bond issuance terms checked November 3, 2026.

**Naming detail:** “Bond” can mean debt securities generally. “Treasury bond” names a specific instrument. A 30-year Treasury bond with two years left remains a Treasury bond; its remaining maturity does not change its original classification.

## 2. What the contract promises

| Term | Plain-language definition | Example |
|---|---|---|
| **Face value / par value** | The amount used to calculate coupons and, for a conventional nominal Treasury, repaid at maturity. | A security has $1,000 face value even if you buy it for $970. |
| **Principal** | The underlying amount owed, distinct from interest. For our plain bond examples, it equals face value. | The final principal repayment is $1,000. |
| **Coupon rate** | Annual contractual interest as a percentage of face value. | A 4% coupon on $1,000 means $40 of coupons per year. |
| **Coupon payment** | The actual dollar interest payment on a coupon date. | With two payments per year, each coupon is $20. |
| **Coupon frequency** | Number of coupon payments per year, denoted by m. | Semiannual means m = 2. |
| **Maturity date** | The date the security's principal becomes payable. | A hypothetical note matures October 25, 2028. |
| **Time to maturity** | Time remaining from the valuation date to maturity. | Two years today; one year after another year passes. |
| **Redemption** | Repayment of the security's principal. | At maturity, the holder receives $1,000 principal plus any final coupon due. |
| **Cash flow** | An actual payment to or from the investor at a particular time. | Paying $1,000 to buy the bond is an outflow; receiving $20 is an inflow. |
| **Cash-flow schedule** | A dated list of payments. | Four coupon dates for a two-year semiannual bond. |
| **Zero-coupon bond** | A bond with no periodic coupon payments. | A bill is a familiar example: one payment at maturity. |

For face value F, annual coupon rate c, and regular coupon frequency m:

$$
\text{Coupon per payment} = \frac{Fc}{m}.
$$

The annual coupon dollars are $Fc$; dividing by $m$ splits them into equal payments. Use decimal rates in calculations: 4% = 0.04. Website controls display percentages, so enter **4** for 4%.

## 3. Worked example: follow the money

Suppose you purchase a hypothetical note with $1,000 face value, a 4% annual coupon, and exactly two years remaining. **Settlement** is when you pay for and take ownership of the bond. Assume it occurs immediately after a coupon payment, so that payment belongs to the previous holder and four equal half-year periods remain.

| Time from purchase | Coupon | Principal repayment | Total received |
|---|---:|---:|---:|
| 6 months | $20 | $0 | $20 |
| 12 months | $20 | $0 | $20 |
| 18 months | $20 | $0 | $20 |
| 24 months | $20 | $1,000 | $1,020 |

In the table, locate the three $20 payments. Why is the fourth payment $1,020? In the experiment, enter $1,000 face value, a 4% coupon, two years, and semiannual payments, then find the same four receipts on the timeline.

Total future receipts are $1,080. That does **not** make today's value $1,080: you must wait for those payments. Your purchase price is a separate cash outflow at time zero.

## 4. Why waiting changes value

| Term | Meaning |
|---|---|
| **Time value of money** | Money available today can earn a return before a future payment arrives. Comparing amounts at different dates therefore requires an interest-rate assumption. |
| **Present value (PV)** | Today's equivalent value of a future payment under a chosen discount rate. |
| **Future value (FV)** | What money grows to over a specified period under an interest assumption. |
| **Discounting** | Converting future money into present value; the reverse of accumulating interest. |
| **Discount rate** | The rate used to value a future payment today. Its compounding convention must match the formula. |
| **Discount factor** | The multiplier converting a future payment to present value. |
| **Simple interest** | Interest calculated only on the starting amount. Over t years, FV = PV × (1 + rt). |
| **Compound interest** | Growth that includes interest on previously accumulated interest. With annual compounding, FV = PV × (1 + r)^t. |

In the two interest formulas, $r$ is an annual decimal rate and $t$ is time in years. For example, $100 invested for two years at 5% grows to $110 with simple interest, or $110.25 with annual compounding. In the second case, the first year's $5 also earns $0.25 in the second year.

With a 5% annual compound discount rate, $100 payable in one year has present value:

$$
PV = \frac{100}{1.05} \approx 95.24.
$$

The discount factor is 1/1.05. The calculation answers what amount today would grow to $100 under that rate assumption.

## 5. Price, coupon, and yield

The contract tells you what will be paid. The **price** tells you what you must pay to acquire those payments. A **yield** expresses the relationship between payments and price as a rate. Read these as an introduction; Lessons 2 and 4 build the calculations step by step.

| Term | Meaning |
|---|---|
| **Market price** | What a security trades for today; it can differ from face value. |
| **At par** | Price equals face value. |
| **Premium bond** | Price is above face value. |
| **Discount bond** | Price is below face value. |
| **Yield to maturity (YTM)** | The single discount rate that makes the present value of promised remaining cash flows equal the full purchase price, under a specified compounding convention. |
| **Current yield** | Annual coupon dollars divided by the quoted bond price in matching dollar units; it omits the gain or loss from repayment at par. |

A fixed coupon stays fixed when market yields change. The market price adjusts: a higher required yield means a lower present value of the same payments. TreasuryDirect illustrates the [relationship between price, coupon rate, and YTM](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/).

For our $1,000-face-value, 4% note, the annual coupon remains $40 even if its price becomes $950. Current yield would then be $40/$950, approximately 4.21%. YTM also accounts for payment timing and the $50 difference between purchase price and principal repaid.

YTM is a pricing measure. It does not guarantee your return over a shorter holding period; selling early introduces an unknown sale price. Achieving a compound terminal return equal to YTM also requires coupons to be reinvested at that rate, with promised payments made as scheduled.

## 6. Misconceptions to catch early

- **Face value equals purchase price:** They can differ. Redemption of $1,000 does not reimburse a $1,050 purchase price.
- **A 4% coupon means a 4% investment return:** The coupon rate describes payments relative to face value. Your return also depends on price and what happens after purchase.
- **Zero coupon means zero interest income:** A security bought below its maturity payment can earn a positive return without periodic coupons.
- **The final cash flow is just principal:** Include the final coupon when one is due.
- **Fixed income means fixed market value:** Contractual payments can be fixed while resale prices change.

## 7. Predict, then build the schedule

Start with the worked example's $1,000 face, 4% coupon, two years, and semiannual payments. Find each of its four receipts in the experiment's timeline and table.

1. Predict what doubling face value will do. Set it to $2,000: each coupon and principal should double.
2. Reset. Switch from Semiannual to Annual. Each coupon becomes $40 and there are two payments; total coupons over two years remain $80. The timing changes.
3. Reset. Set the coupon to zero. Only the $1,000 principal is received at maturity.

Annual and quarterly choices are hypothetical comparisons. Actual Treasury notes and bonds pay semiannually.

## 8. Check your understanding

1. A $2,000-face-value note has a 3% annual coupon and semiannual payments. How large is each coupon?
2. You buy a conventional nominal Treasury for $980 with $1,000 face value. What principal amount is repaid at maturity?
3. If that Treasury pays a $20 coupon at maturity, what is the total final cash flow?
4. At a positive discount rate, is $100 due next year worth more or less than $100 today?
5. When market yields rise, does an existing fixed-rate note's coupon change, or does its price adjust?

::: answer
**Answers:** (1) $2,000 × 0.03 / 2 = $30. (2) $1,000; purchase price does not alter principal. (3) $1,020, including the final coupon. (4) Less, because money today can grow before next year. (5) Its price adjusts downward; the coupon stays fixed.
:::

**Next lesson:** Discount these payments to today. Actual settlement dates, accrued interest, and clean versus dirty prices come later.
