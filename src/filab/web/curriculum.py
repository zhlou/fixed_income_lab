"""Reading order and explicit experiment assignments for the published course."""
LESSONS = [
    dict(slug="present-value", title="Payments, price & yield",
         headline="What does this bond pay, and what is it worth?",
         description="Follow four payments from their promised amounts to a price and an implied yield.",
         tag="Price from payments", file="present-value.md", milestone="M0", experiment="pricing", prerequisite=None),
    dict(slug="par-yields-and-quotes", title="Read a Treasury curve",
         headline="How do you read a Treasury yield curve?",
         description="Compare two published curves and reconcile the change in the ten-year minus two-year spread.",
         tag="Treasury observations", file="par-yields-and-quotes.md", milestone="M3", experiment="history", prerequisite="present-value"),
    dict(slug="modified-duration-dv01", title="Duration & dollar risk",
         headline="Which bond loses more when yields rise?",
         description="Connect payment timing to percentage sensitivity and dollars per basis point.",
         tag="Interest-rate sensitivity", file="modified-duration-dv01.md", milestone="M1", experiment="duration", prerequisite="present-value"),
    dict(slug="convexity", title="Convexity & error",
         headline="When does duration give a poor estimate?",
         description="Add curvature, then judge the estimate against exact repricing.",
         tag="Approximation error", file="convexity.md", milestone="M1", experiment="convexity", prerequisite="modified-duration-dv01"),
    dict(slug="settlement-and-accrued-interest", title="Settlement & coupon ownership",
         headline="What do you actually pay between coupon dates?",
         description="Reconcile a quote with the amount paid, then cross the coupon date.",
         tag="Dates and dollars", file="settlement.md", milestone="M0", experiment="settlement", prerequisite="present-value"),
    dict(slug="reinvestment-and-cash", title="Hold to maturity",
         headline="What do you earn by holding to maturity?",
         description="Follow a discount bond into cash and measure what reinvesting its coupons adds.",
         tag="Time and cash", file="reinvestment-and-cash.md", milestone="M2", experiment="maturity", prerequisite="settlement-and-accrued-interest"),
    dict(slug="holding-period-returns", title="Sell before maturity",
         headline="What do you earn if you sell early?",
         description="Combine sale proceeds, coupons, and costs to reconcile an investment return.",
         tag="Investment return", file="holding-period-returns.md", milestone="M2", experiment="sale", prerequisite="reinvestment-and-cash"),
]

MILESTONES = [
    ('M0', 'Bond foundations', 'Available'),
    ('M1', 'Duration & convexity', 'Available'),
    ('M2', 'Returns & cash accounting', 'Available'),
    ('M3', 'Historical observations', 'Available'),
    ('M4', 'Discount curves', 'Next'),
    ('M5', 'First strategy study', 'Planned'),
    ('M6', 'Robustness & curve risk', 'Planned'),
    ('M7', 'Daily research workbench', 'Planned'),
]
ROADMAP = [(key, title, 'Learn · experiment' if status == 'Available' else 'Future milestone', status)
           for key, title, status in MILESTONES]
