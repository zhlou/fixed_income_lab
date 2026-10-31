## A yield needs a denominator and a clock

A Treasury bill pays no periodic coupons. You pay $P$ and receive face value
$F$ at maturity. The dollar gain is $F-P$, and holding-period return is:

$$
H=\frac{F-P}{P}.
$$

This is the return over the bill's remaining days, not an annual rate.
Different annualization rules can describe exactly the same purchase and
redemption. A higher quoted number alone does not mean a better investment.

## The bank discount quotation

For annual bank discount rate $d$ and $r$ actual days to maturity:

$$
P=F\left(1-d\frac{r}{360}\right),
\qquad d=\frac{F-P}{F}\frac{360}{r}.
$$

The discount rate uses **face value**, not money invested, and a **360-day
year**. It is not the coupon rate, compound nominal YTM, or holding-period
return. In the calculator, keep the discount quote fixed and change the days:
more time means a larger discount and a lower purchase price.

## Coupon-equivalent, bond-equivalent, and investment yield

Coupon-equivalent yield expresses the bill's gain using a **semiannual
coupon-bond benchmark**. Treasury notes and bonds pay coupons every six
months, so six months is one interest period in that comparison.

This quotation uses **purchase price** and a **365- or 366-day year**.
Bond-equivalent and investment yield are common names for this bill
quotation. Choose 366 when the year following issue includes February 29;
this calculator makes the basis an explicit input.

### Within one six-month period

Treasury's convention uses simple interest within a partial interest period.
Let $t=r/Y$ be the holding time in years and $i$ the annual quoted yield.
For $t\leq 1/2$, the growth factor is:

$$
\frac{F}{P}=1+it.
$$

Rearranging gives the investment yield used for shorter bills:

$$
i=\frac{F-P}{P}\frac{Y}{r},\qquad Y\in\{365,366\}.
$$

This is simple annualization, not an effective annual compound return.

### Beyond one six-month period

The comparison now spans a complete interest period and a remaining partial
period. The quotation allows compounding between those periods:

$$
\frac{F}{P}=\underbrace{\left(1+\frac{i}{2}\right)}_{\text{one full half-year}}
\underbrace{\left[1+i\left(t-\frac12\right)\right]}_{\text{remaining partial period}}.
$$

Substituting $t=r/Y$ gives the Treasury relationship solved by the calculator:

$$
P\left[1+\left(\frac{r}{Y}-\frac12\right)i\right]
\left(1+\frac{i}{2}\right)=F.
$$

At exactly half a year, both formulas give $F/P=1+i/2$. At one full year,
the longer-bill formula becomes $F/P=(1+i/2)^2$: two compounded half-year
periods. For example, a 5% annual quoted benchmark corresponds to a 2.5%
gain over half a year and a 5.0625% gain over a full year under this convention.
This example holds the benchmark yield fixed, rather than the chart's bank
discount quote.

### Why the chart bends at half a year

**The yield stays continuous, but the formula's slope changes.** Before the
boundary, the quote uses simple annualization. After it, the quote includes
the semiannual compounding adjustment. For a positive gain, compounding lets
a lower annual quoted rate represent the same total gain than simple
annualization would. This slows the curve's rise just beyond the boundary.

The dotted line marks half the selected year: 182.5 days on a 365-day basis,
or 183 days on a 366-day basis. The six-month boundary belongs to the
comparison convention. **The bill still pays only at maturity**; it does not
start paying coupons at six months. This quotation does not require you to
receive or reinvest an intermediate payment.

The results retain simple annualization as a separate row so you can see the
difference. Try 182 versus 364 days. Switching to 366 changes the investment
yield calculation, while bank discount price remains on actual/360.
A bill's coupon-equivalent quotation and a coupon bond's nominal YTM still
have instrument-specific rules; matching rate labels is not sufficient.

Try a 5% bank discount quote with a 365-day basis:

| Days | Simple annualized yield | Coupon-equivalent yield |
|---|---:|---:|
| 182 | 5.2009% | 5.2009% |
| 364 | 5.3394% | 5.2701% |

These values use unrounded prices. Compare the two yield rows as you move
past half a year: their growing difference is the compounding adjustment.

## One worked comparison

At a 5% bank discount quote and 182 days, $100 face costs **$97.47** when
displayed to cents. The calculation uses the unrounded price, approximately
$97.472222, giving a 182-day return of about **2.5933%** and a 365-day
investment yield of about **5.2009%**. All three describe the same cash flows.
If an actual purchase price is rounded, recomputing yield from that rounded
price can give a slightly different result.

This lesson implements the formulas in
[Treasury Appendix B, section V](https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf).
Treasury also provides a short
[pricing example](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/).
Prices and yields are illustrative; they are not current market data.

```python
from filab.pricing import treasury_bill

bill = treasury_bill(
    face_value=100, discount_rate=0.05,
    days_to_maturity=182, year_days=365,
)
print(f"Price: ${bill['price']:.2f}")
print(f"Investment yield: {bill['investment_rate']:.4%}")
```

## Phase 1 checkpoint

Before moving to duration and convexity, explain these in your own words:

1. How do you construct and discount a bond's promised payments?
2. How do coupon rate, current yield, YTM, and bill discount yield differ?
3. Why does a clean quote differ from the full settlement amount?
4. How do day counts and compounding change a calculation?
5. Why can bonds with the same maturity and YTM have different sensitivity?

For the last question, revisit the coupon and payment-timing experiments:
earlier cash receipts change the weights of distant payments. Phase 2 will
turn that intuition into duration and convexity. Completing the software
makes these experiments available; completing the learning checkpoint means
you can explain their results.

**Next module:** Duration, convexity, DV01, and exact versus approximate repricing.
