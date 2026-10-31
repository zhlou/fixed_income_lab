"""Worked examples and economic identities, independent of code structure."""

import pytest

from filab.pricing import (
    CashFlow,
    fixed_coupon_cashflows,
    price_coupon_bond,
    price_zero_coupon,
    yield_to_maturity,
)


def test_schedule_includes_final_coupon_and_principal():
    assert fixed_coupon_cashflows(
        face_value=1000, coupon_rate=0.04, maturity_years=2
    ) == [
        CashFlow(0.5, 20),
        CashFlow(1.0, 20),
        CashFlow(1.5, 20),
        CashFlow(2.0, 1020),
    ]


def test_zero_coupon_lesson_example():
    assert price_zero_coupon(
        face_value=1000, ytm=0.05, maturity_years=2
    ) == pytest.approx(905.9506447997552)


def test_coupon_bond_lesson_example():
    assert price_coupon_bond(
        face_value=1000, coupon_rate=0.04, ytm=0.05, maturity_years=2
    ) == pytest.approx(981.1901289599514)


@pytest.mark.parametrize("frequency", [1, 2, 4])
def test_matching_coupon_and_yield_prices_at_par(frequency):
    assert price_coupon_bond(
        face_value=1000,
        coupon_rate=0.04,
        ytm=0.04,
        maturity_years=10,
        frequency=frequency,
    ) == pytest.approx(1000)


def test_positive_cashflows_price_falls_as_yield_rises():
    prices = [
        price_coupon_bond(
            face_value=1000, coupon_rate=0.04, ytm=y, maturity_years=2
        )
        for y in [-0.01, 0, 0.03, 0.04, 0.05]
    ]
    assert all(left > right for left, right in zip(prices, prices[1:]))
    assert prices[-3] > 1000  # Premium when yield is below coupon.
    assert prices[-1] < 1000  # Discount when yield is above coupon.


def test_zero_yield_returns_undiscounted_total():
    assert price_coupon_bond(
        face_value=1000, coupon_rate=0.04, ytm=0, maturity_years=2
    ) == pytest.approx(1080)
    assert price_zero_coupon(
        face_value=1000, ytm=0, maturity_years=2
    ) == pytest.approx(1000)


def test_zero_coupon_rate_agrees_with_zero_coupon_pricer():
    assert price_coupon_bond(
        face_value=1000, coupon_rate=0, ytm=0.05, maturity_years=2
    ) == pytest.approx(
        price_zero_coupon(face_value=1000, ytm=0.05, maturity_years=2)
    )


def test_annual_compounding_reproduces_effective_annual_example():
    assert price_zero_coupon(
        face_value=1000, ytm=0.04, maturity_years=0.5, frequency=1
    ) == pytest.approx(980.5806756909201)


def test_equivalent_rate_conventions_give_same_price():
    nominal = 0.04
    effective = (1 + nominal / 2) ** 2 - 1
    semiannual = price_zero_coupon(face_value=1000, ytm=nominal, maturity_years=0.25)
    annual = price_zero_coupon(
        face_value=1000, ytm=effective, maturity_years=0.25, frequency=1
    )
    assert semiannual == pytest.approx(annual)


def test_zero_coupon_at_maturity_returns_face_value():
    assert price_zero_coupon(
        face_value=1000, ytm=0.05, maturity_years=0
    ) == 1000


def test_price_scales_with_face_value():
    small = price_coupon_bond(
        face_value=100, coupon_rate=0.04, ytm=0.05, maturity_years=2
    )
    large = price_coupon_bond(
        face_value=1000, coupon_rate=0.04, ytm=0.05, maturity_years=2
    )
    assert large == pytest.approx(10 * small)


@pytest.mark.parametrize("maturity", [0, -1, 0.75])
def test_coupon_schedule_rejects_nonregular_maturity(maturity):
    with pytest.raises(ValueError, match="maturity_years"):
        fixed_coupon_cashflows(
            face_value=1000, coupon_rate=0.04, maturity_years=maturity
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"face_value": 0},
        {"face_value": -100},
        {"face_value": float("inf")},
        {"ytm": float("nan")},
        {"ytm": -2},
        {"ytm": -3},
        {"maturity_years": -1},
        {"maturity_years": float("inf")},
        {"frequency": 0},
        {"frequency": 2.5},
        {"frequency": True},
    ],
)
def test_zero_pricer_rejects_invalid_inputs(overrides):
    inputs = dict(face_value=1000, ytm=0.05, maturity_years=2)
    inputs.update(overrides)
    with pytest.raises(ValueError):
        price_zero_coupon(**inputs)


@pytest.mark.parametrize("coupon_rate", [-0.01, float("nan"), float("inf")])
def test_invalid_coupon_rates_are_rejected(coupon_rate):
    with pytest.raises(ValueError, match="coupon_rate"):
        price_coupon_bond(
            face_value=1000, coupon_rate=coupon_rate, ytm=0.05, maturity_years=2
        )


@pytest.mark.parametrize("frequency", [1, 2, 4, 12])
@pytest.mark.parametrize("coupon_rate", [0, 0.04, 0.12])
@pytest.mark.parametrize("ytm", [-0.02, 0, 0.04, 0.15])
def test_yield_solver_round_trip(frequency, coupon_rate, ytm):
    args = dict(face_value=1000, coupon_rate=coupon_rate,
                maturity_years=10, frequency=frequency)
    price = price_coupon_bond(ytm=ytm, **args)
    solved = yield_to_maturity(price=price, **args)
    assert solved == pytest.approx(ytm, abs=1e-12)
    assert price_coupon_bond(ytm=solved, **args) == pytest.approx(price, rel=1e-11)


def test_yield_solver_matches_independent_one_period_solution():
    # One semiannual payment of $102: y = 2 * (102 / P - 1).
    for price in [90, 100, 102, 110, 1000]:
        assert yield_to_maturity(price=price, face_value=100, coupon_rate=0.04,
                                 maturity_years=0.5) == pytest.approx(2 * (102 / price - 1))


def test_yield_solver_matches_zero_coupon_closed_form():
    price, face, years, frequency = 61.5, 100, 30, 2
    expected = frequency * ((face / price) ** (1 / (frequency * years)) - 1)
    assert yield_to_maturity(price=price, face_value=face, coupon_rate=0,
                             maturity_years=years, frequency=frequency) == pytest.approx(expected)


def test_yield_solver_scales_with_price_and_face():
    small = yield_to_maturity(price=98, face_value=100, coupon_rate=0.04, maturity_years=2)
    large = yield_to_maturity(price=980, face_value=1000, coupon_rate=0.04, maturity_years=2)
    assert small == pytest.approx(large)


@pytest.mark.parametrize('price', [1e-100, 1e100])
def test_yield_solver_handles_wide_price_brackets(price):
    solved = yield_to_maturity(price=price, face_value=100, coupon_rate=0.04, maturity_years=30)
    # Negative powers avoid overflowing the denominator at extreme yields.
    flows = fixed_coupon_cashflows(face_value=100, coupon_rate=0.04, maturity_years=30)
    repriced = sum(flow.amount * (1 + solved / 2) ** (-period)
                   for period, flow in enumerate(flows, 1))
    assert repriced == pytest.approx(price, rel=1e-9, abs=0)


@pytest.mark.parametrize('overrides', [
    {'price': 0}, {'price': -1}, {'price': float('nan')}, {'price': float('inf')},
    {'price': True}, {'maturity_years': 0}, {'maturity_years': 0.75},
    {'frequency': 0}, {'frequency': True}, {'coupon_rate': -0.01}, {'face_value': 0},
])
def test_yield_solver_rejects_invalid_inputs(overrides):
    args = dict(price=98, face_value=100, coupon_rate=0.04, maturity_years=2)
    args.update(overrides)
    with pytest.raises(ValueError):
        yield_to_maturity(**args)
