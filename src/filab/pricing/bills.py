"""Treasury bill discount quotations and coupon-equivalent investment yields."""
from math import isfinite, sqrt
from numbers import Integral
from ._validation import finite_real, positive_face_value


def treasury_bill(*, face_value=100, discount_rate, days_to_maturity, year_days=365):
    """Actual/360 discount price; investment yield on explicit 365/366 basis.

    At or below half a year use simple annualization on purchase price.
    Beyond half a year use Treasury's quadratic coupon-equivalent formula.
    No intermediate auction-price rounding is performed.
    """
    face_value = positive_face_value(face_value)
    discount_rate = finite_real('discount_rate', discount_rate)
    if isinstance(days_to_maturity, bool) or not isinstance(days_to_maturity, Integral) or not 1 <= days_to_maturity <= 366:
        raise ValueError('days_to_maturity must be an integer between 1 and 366.')
    if isinstance(year_days, bool) or year_days not in (365, 366):
        raise ValueError('year_days must be 365 or 366.')
    price = face_value * (1 - discount_rate * days_to_maturity / 360)
    if not isfinite(price) or price <= 0:
        raise ValueError('discount_rate must imply a positive finite price.')
    holding_return = (face_value - price) / price
    b = days_to_maturity / year_days
    simple = holding_return / b
    if b <= 0.5:
        investment_rate, method = simple, 'Simple annualization'
    else:
        a, c = b / 2 - 0.25, -holding_return
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            raise ValueError('discount_rate does not imply a real coupon-equivalent yield.')
        investment_rate = -2 * c / (b + sqrt(discriminant))
        method = 'Coupon-equivalent quadratic'
    return dict(price=price, discount_rate=discount_rate, investment_rate=investment_rate,
                simple_annual_rate=simple, holding_return=holding_return,
                interest=face_value - price, year_days=year_days, days_to_maturity=days_to_maturity,
                method=method)
