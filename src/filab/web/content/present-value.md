**Goal:** Derive a bond's price from its promised payments, then calculate one zero-coupon and one coupon-bond example by hand.

Prerequisite: [Lesson 1 glossary](/lessons/bond-basics).

## 1. Our assumptions

All examples are hypothetical. We value fixed, promised cash flows using a single supplied annual nominal yield y, compounded m times per year. We are not estimating market interest rates in this lesson.

An **annual nominal rate** is quoted as the rate per compounding period multiplied by the number of periods in a year. An **effective annual rate** includes a full year's compound growth. “Nominal” here describes a rate quotation; it has a different role from “nominal Treasury,” which means a security without inflation adjustment.

Assume valuation immediately after a coupon payment, equal periods until future payments, no accrued interest, and no fees or taxes. For the coupon examples, coupon and compounding frequencies match. Rates in formulas are decimals.

## 2. Derive present value by reversing compounding

Let r be the interest rate **per period**. One dollar today grows to 1 + r after one period. An amount P grows to:

$$
P(1+r) \quad\text{after one period},
$$

$$
P(1+r)^2 \quad\text{after two periods}.
$$

Here $k$ counts periods and $CF_k$ means the cash flow paid at the end of period $k$. After k periods, the future value is P(1+r)^k. To find the amount today equivalent to a future payment CF_k, solve:

$$
P(1+r)^k=CF_k
\quad\Longrightarrow\quad
\boxed{PV_k=\frac{CF_k}{(1+r)^k}}.
$$

This is discounting: reversing compound growth. For example, $100 in one year discounted at 5% annually is $100/1.05 = $95.24, rounded.

### Annual rate versus period rate

If y is an annual nominal yield compounded m times per year:

$$
r=\frac{y}{m},\qquad k=mt,
$$

where t is time in years. For y = 5% and m = 2, each half-year rate is 2.5%. A payment in two years is four periods away.

**Convention matters:** 5% nominal compounded semiannually has an effective annual rate of (1.025)^2 − 1 = 5.0625%. If instead 5% were an effective annual rate, its half-year rate would be sqrt(1.05) − 1, approximately 2.4695%. Always state which rate you mean.

## 3. Price a zero-coupon bond

A zero-coupon bond makes just one payment: face value F at maturity. Let $T$ be remaining years and $N=mT$ the number of compounding periods. Then:

$$
\boxed{P=\frac{F}{(1+y/m)^N}}.
$$

Example: F = $1,000, two years remaining, and y = 5% nominal compounded semiannually. Then m = 2 and N = 4:

$$
P=\frac{1{,}000}{1.025^4}
=905.9506448\ldots
\approx\boxed{\$905.95}.
$$

Check the logic: $905.9506448 growing at 2.5% for four periods becomes $1,000. The bond itself makes no interim payments; the compounding calculation establishes the equivalence between today's price and the maturity payment.

This is a generic zero-coupon pricing example. Actual Treasury bill discount-yield quotations use different conventions, which we will study separately.

## 4. Price a coupon bond by adding present values

Each coupon is a separate future payment. Because dollars received today can be added, add the present values of all the payments. The symbol $\sum_{k=1}^{N}$ means “add one term for every payment, from period 1 through period $N$”:

$$
\boxed{P=\sum_{k=1}^{N}\frac{CF_k}{(1+y/m)^k}}.
$$

Let c be the annual coupon rate and C = Fc/m the coupon dollars per payment. Then CF_k = C before maturity and CF_N = C + F. Equivalently:

$$
\boxed{P=\sum_{k=1}^{N}\frac{C}{(1+y/m)^k}
+\frac{F}{(1+y/m)^N}}.
$$

The coupon sum includes the final coupon; the last term adds principal once.

### Worked example: our note from Lesson 1

Use $1,000 face value, a 4% annual coupon, two years remaining, semiannual payments, and a supplied 5% nominal YTM compounded semiannually.

$$
C=\frac{1{,}000(0.04)}{2}=20,
\qquad r=\frac{0.05}{2}=0.025,
\qquad N=2(2)=4.
$$

| Period k | Years from valuation | Cash flow | Discount factor 1/(1.025)^k | Present value |
|---|---:|---:|---:|---:|
| 1 | 0.5 | $20 | 0.975610 | $19.51 |
| 2 | 1.0 | $20 | 0.951814 | $19.04 |
| 3 | 1.5 | $20 | 0.928599 | $18.57 |
| 4 | 2.0 | $1,020 | 0.905951 | $924.07 |

$$
P=\frac{20}{1.025}
+\frac{20}{1.025^2}
+\frac{20}{1.025^3}
+\frac{1{,}020}{1.025^4}
=981.19012896\ldots
\approx\boxed{\$981.19}.
$$

Retain full precision until the final result. Rounding each payment's present value to cents first can create a one-cent discrepancy.

The coupon rate is 4%, while the supplied yield is 5%. Buying below face value provides an additional gain at redemption that contributes to the yield.

## 5. A shortcut, derived from a geometric sum

Write v = 1/(1+r). The present value of the coupons is C(v + v^2 + ... + v^N). If S = v + ... + v^N, then subtracting vS from S gives:

$$
(1-v)S=v-v^{N+1}
\quad\Longrightarrow\quad
S=\frac{v(1-v^N)}{1-v}
=\frac{1-v^N}{r}.
$$

Therefore, for r ≠ 0:

$$
P=C\frac{1-(1+r)^{-N}}{r}+F(1+r)^{-N}.
$$

This is the same cash-flow sum in a shorter form. At r = 0, use P = NC + F directly.

### Why coupon rate equal to yield gives par

With matching conventions, c = y means C = Fr. Substituting:

$$
P=Fr\frac{1-(1+r)^{-N}}{r}+F(1+r)^{-N}=F.
$$

For our note, varying only the supplied yield gives:

| Annual nominal yield | Price |
|---|---:|
| 3% | $1,019.27 |
| 4% | $1,000.00 |
| 5% | $981.19 |

Higher yield makes each discount factor smaller, so the same positive payments have a lower price. The coupon dollars do not change.

## 6. Where the yield curve fits

A **yield curve** relates interest rates to maturities at one point in time. A **spot rate** applies to a single future payment at a particular maturity; a **discount curve** expresses the same valuation information as today's value of one dollar paid at each future date. These are previews of later lessons, not inputs you need to estimate here.

The more general expression is:

$$
P=\sum_k CF_kD(t_k),
$$

where D(t_k) is the discount factor for payment date t_k. In this lesson, our single-rate assumption sets D(t_k) = (1+y/m)^(-k).

A market discount curve can supply a different discount factor at each payment date. A bond's YTM is the single rate that reproduces its price; it does not imply the market's spot curve is flat. We will construct curves later. For now, every exercise supplies the yield and its compounding convention.

## 7. Effective annual rate: a comparison, not an automatic payment

A 4% nominal rate with two compounding periods has a 2% half-year rate.
To get the effective annual rate $R$, compound one dollar for all $m$ periods,
then subtract the starting dollar:

$$
R=\left(1+\frac{y}{m}\right)^m-1=1.02^2-1=4.04\%.
$$

A $1,000 bond bought at par pays two $20 coupons during the year.
Holding both as non-interest-bearing cash produces $40. Reinvesting the
first $20 at 2% for six months adds $0.40. The extra money comes from
reinvestment; the bond still pays only $40 in coupons.

To reverse the calculation, take the $m$th root of $1+R$ to recover the
per-period growth factor, subtract one, and multiply the period rate by $m$:

$$
y=m\left[(1+R)^{1/m}-1\right].
$$

For a zero-coupon payment, an effective annual rate uses years directly:

$$
P=\frac{F}{(1+R)^T},\qquad R=\left(\frac{F}{P}\right)^{1/T}-1.
$$

Here $T$ is in years, including fractional years. The annualized rate is
an equivalent rate: it does not guarantee an opportunity to repeat a
short investment at the same return for the rest of a year.

## 8. Predict and check in the experiment

Start with the worked example, then change only YTM from 5% to 4%. Predict which cash flows and present values will change. The payments stay at $20, $20, $20, and $1,020; their present values now sum to $1,000.00. At zero yield the discount factors are all one and price equals the $1,080 total receipts.

In the separate **What does “4% a year” mean?** experiment, select Annual nominal rate, 4%, and Semiannual. Compare $40.00 held as cash with $40.40 after reinvestment. Predict what Annual compounding will show: the nominal and effective annual rates coincide, and there is no within-year reinvestment income.

## 9. Common mistakes

- **Using 5% for every half-year:** divide a 5% annual nominal yield by two first.
- **Discounting the final coupon twice:** include it in the coupon sum or in the final combined payment, never both.
- **Assuming all discount factors are below one:** that holds for positive yields. At zero yield they equal one; a negative yield with $1+y/m>0$ makes future positive payments worth more than their undiscounted amounts in this model.
- **Treating compounding as an extra bond payment:** interest on coupons requires a separate reinvestment action.

## 10. Try it yourself

1. Price a $1,000 zero-coupon bond with one year remaining at 4% nominal yield compounded semiannually.
2. Price a $1,000 bond with a 6% coupon, one year remaining, semiannual payments, and 4% nominal yield compounded semiannually. List the cash flows before discounting them.
3. What would the bond in question 2 cost at a 6% nominal yield compounded semiannually?
4. Why is the final cash flow larger than the earlier coupons?

::: answer
**Answers — attempt the questions first**

1. $1,000/(1.02)^2 = **$961.17**.
2. Cash flows: $30 in six months and $1,030 in one year. Price = $30/1.02 + $1,030/(1.02)^2 = **$1,019.42**.
3. **$1,000.00**, since coupon rate and yield match under these conventions.
4. It includes both the last coupon and principal repayment.
:::

**Checkpoint:** You should be able to turn a bond description into cash flows, convert an annual nominal yield into a period rate, and discount each payment using the correct period count.

**Next:** Use the [Bond Pricing Lab](/lessons/bond-pricing-lab) to test how coupon, maturity, and yield change price, then [solve yield to maturity from a price](/lessons/yield-to-maturity). The optional “Under the hood” section below shows the implementation.
