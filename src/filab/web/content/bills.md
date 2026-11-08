## One payment, several quoted rates

A **5% bank discount quote** for a 182-day Treasury bill implies **$97.47 paid per $100 face**, **2.59% earned over 182 days**, and a **5.20% investment yield** on a 365-day basis. All describe the same purchase and $100 redemption. These are hypothetical inputs.

Bank discount yield $d$ measures the discount relative to face $F$ using a 360-day year. With $n$ actual days remaining,

$$
F-P=Fd\frac n{360}
\quad\Longrightarrow\quad P=F\left(1-d\frac n{360}\right).
$$

Here $P=100(1-0.05\times182/360)=97.472222\ldots$. Return divides the $2.527778 gain by the money invested, giving $(F-P)/P=2.5933\%$.

For no more than half the selected year $Y$, investment yield $i$ scales this return to a year.

$$
i=\frac{F-P}{P}\frac Yn.
$$

This gives **5.2009%** for $Y=365$. The tool keeps full precision before displaying cents. Choose a 366-day investment basis when applicable. The discount price continues to use actual days over 360.

## At the chart's half-year boundary

Beyond half a year, the semiannual coupon-bond benchmark has a full half-year growth period followed by a remaining fractional period. Treasury's investment-yield convention then solves

$$
\frac FP=\left(1+\frac i2\right)
\left[1+i\left(\frac nY-\frac12\right)\right].
$$

At $n/Y=1/2$ both expressions give $F/P=1+i/2$. At a full year the longer expression gives $(1+i/2)^2$. That compounding adjustment produces the bend in the chart for a positive quote. At a zero quote, both yields are zero. The bill has a single maturity payment throughout.

The chart holds the bank discount quote fixed as days change. Its annualized rates provide quotation comparisons. Whether you can repeat the investment at the same rate depends on future opportunities. [Treasury Appendix B, section VI](https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf).
