"""Published lessons and milestone availability; no calendar promises."""
LESSONS = [
    dict(slug="bond-basics", title="Bond basics", headline="Meet the cash flows.",
         description="A bond is a promise about money and time. Change the terms and see exactly what gets paid.",
         tag="The building blocks", duration="15 min", file="basics.md"),
    dict(slug="present-value", title="Present value & bond pricing", headline="Bring the future back.",
         description="Discount future payments, understand annual rate conventions, and add them up to price a bond.",
         tag="The time value of money", duration="25 min", file="present-value.md"),
    dict(slug="bond-pricing-lab", title="Bond pricing lab", headline="Change one thing.",
         description="Hold the assumptions still. Move yield, maturity, or coupon—and learn from what changes.",
         tag="Experiment & explain", duration="30 min", file="lab.md"),
    dict(slug="yield-to-maturity", title="Yield to maturity", headline="What yield does this price imply?",
         description="Work backward from a bond price, then compare coupon rate, current yield, and yield to maturity.",
         tag="Price to yield", duration="20 min", file="yield-to-maturity.md"),
    dict(slug="settlement-and-accrued-interest", title="Settlement & accrued interest", headline="What do you actually pay?",
         description="Move between coupon dates, separate clean and dirty prices, and follow a bond toward maturity.",
         tag="Dates and dollars", duration="30 min", file="settlement.md"),
    dict(slug="treasury-bill-yields", title="Treasury bill yields", headline="One bill. Different quoted yields.",
         description="Translate a bank discount quote into price, holding-period return, and coupon-equivalent yield.",
         tag="Read the convention", duration="20 min", file="bills.md"),
]
LESSONS.extend([
    dict(slug="macaulay-duration", title="Cash-flow timing & duration", headline="When does value come back?",
         description="Weight each payment by its present value and discover why maturity alone cannot describe risk.",
         tag="M1 · Cash-flow timing", duration="25 min", file="macaulay-duration.md", milestone="M1",
         prerequisite="present-value", prediction="At the same maturity and yield, will a zero-coupon bond or a coupon bond have the longer weighted payment time?"),
    dict(slug="modified-duration-dv01", title="Modified duration & DV01", headline="Turn timing into sensitivity.",
         description="Translate a small yield move into a percentage change and a dollar exposure. Compare two bonds on equal face value.",
         tag="M1 · Interest-rate sensitivity", duration="30 min", file="modified-duration-dv01.md", milestone="M1",
         prerequisite="macaulay-duration", prediction="If you double face value, which doubles: modified duration, DV01, or both?"),
    dict(slug="convexity", title="Convexity & approximation error", headline="A curve is not a straight line.",
         description="Compare exact repricing with duration and convexity estimates, then inspect where the approximations break down.",
         tag="M1 · Test the approximation", duration="30 min", file="convexity.md", milestone="M1",
         prerequisite="modified-duration-dv01", prediction="For equal upward and downward yield shocks, will the price loss and gain have the same size?"),
])
for lesson in LESSONS:
    lesson.setdefault('milestone', 'M0')

MILESTONES = [
    ('M0', 'Bond foundations', 'Available'),
    ('M1', 'Duration & convexity', 'Available'),
    ('M2', 'Returns & cash accounting', 'Next'),
    ('M3', 'Historical observations', 'Planned'),
    ('M4', 'Discount curves', 'Planned'),
    ('M5', 'First strategy study', 'Planned'),
    ('M6', 'Robustness & curve risk', 'Planned'),
    ('M7', 'Daily research workbench', 'Planned'),
]
ROADMAP = [(key, title, 'Learn · experiment' if status == 'Available' else 'Future milestone', status)
           for key, title, status in MILESTONES]
