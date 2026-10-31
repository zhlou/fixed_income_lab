"""Dated identities, boundaries, and independent published Treasury examples.

Reference: 31 CFR 356 Appendix B, I.D, II.A/D and V.D.
https://www.treasurydirect.gov/files/laws-and-regulations/auction-regulations-uoc/31-cfr-part-356.pdf
Published prices use six decimals; comparisons allow half of the final unit.
"""
from datetime import date, timedelta
import pytest
from filab.pricing import (coupon_schedule, accrued_interest, clean_to_dirty, dirty_to_clean,
    settled_bond_valuation, settled_yield_to_maturity, price_coupon_bond, treasury_bill)

BASE = dict(face_value=100, coupon_rate=0.04, issue_date=date(2025, 11, 15),
            settlement_date=date(2026, 8, 15), maturity_date=date(2028, 11, 15))


def test_treasury_published_regular_thirty_year_price():
    # Appendix B II.A, May 15, 1990 issue: 8.75% coupon, 8.84% yield.
    value = settled_bond_valuation(face_value=100, coupon_rate=.0875, ytm=.0884,
        issue_date=date(1990, 5, 15), settlement_date=date(1990, 5, 15), maturity_date=date(2020, 5, 15))
    assert value.clean_price == pytest.approx(99.057893, abs=0.5e-6, rel=0)
    assert value.accrued_interest == 0


def test_treasury_published_reopening_clean_dirty_and_accrued():
    # Appendix B II.D, 9.5% note accruing Nov 15, 1985, settled Nov 29.
    args = dict(face_value=100, coupon_rate=.095, issue_date=date(1985, 11, 15),
                settlement_date=date(1985, 11, 29), maturity_date=date(1995, 11, 15))
    value = settled_bond_valuation(ytm=.0954, **args)
    assert value.clean_price == pytest.approx(99.730918, abs=0.5e-6, rel=0)
    assert value.dirty_price == pytest.approx(100.098321, abs=0.5e-6, rel=0)
    assert value.accrued_interest == pytest.approx(.367403, abs=0.5e-6, rel=0)
    assert settled_yield_to_maturity(price=99.730918, **args) == pytest.approx(.0954, abs=2e-9)


@pytest.mark.parametrize('face, expected', [(1000, 16.875), (150000, 2531.25)])
def test_treasury_published_actual_actual_accrued(face, expected):
    # Appendix B I.D: 6.75% May 15, 2000 note, reopened August 15.
    accrued = accrued_interest(face_value=face, coupon_rate=.0675,
        issue_date=date(2000, 5, 15), settlement_date=date(2000, 8, 15), maturity_date=date(2005, 5, 15))
    assert accrued == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize('ytm', [-.02, 0, .04, .05, .20])
@pytest.mark.parametrize('coupon', [0, .04])
def test_dated_prices_and_both_yield_price_types_round_trip(ytm, coupon):
    args = dict(BASE, coupon_rate=coupon)
    value = settled_bond_valuation(ytm=ytm, **args)
    assert value.dirty_price == pytest.approx(sum(f.present_value for f in value.cashflows))
    assert value.clean_price == pytest.approx(dirty_to_clean(value.dirty_price, value.accrued_interest))
    assert value.dirty_price == pytest.approx(clean_to_dirty(value.clean_price, value.accrued_interest))
    for kind, price in [('clean', value.clean_price), ('dirty', value.dirty_price)]:
        assert settled_yield_to_maturity(price=price, price_type=kind, **args) == pytest.approx(ytm, abs=1e-11)


def test_coupon_date_matches_regular_period_price():
    args = dict(BASE, settlement_date=date(2026, 11, 15))
    value = settled_bond_valuation(ytm=.05, **args)
    regular = price_coupon_bond(face_value=100, coupon_rate=.04, ytm=.05, maturity_years=2)
    assert value.dirty_price == pytest.approx(regular)
    assert value.accrued_interest == 0
    assert value.cashflows[0].payment_date == date(2027, 5, 15)


def test_coupon_date_resets_accrual_and_payment_leaves_future_schedule():
    before = settled_bond_valuation(ytm=.05, **dict(BASE, settlement_date=date(2026, 11, 14)))
    after = settled_bond_valuation(ytm=.05, **dict(BASE, settlement_date=date(2026, 11, 15)))
    assert before.accrued_interest == pytest.approx(2 * 183 / 184)
    assert after.accrued_interest == 0
    assert len(before.cashflows) == len(after.cashflows) + 1
    assert before.dirty_price - after.dirty_price == pytest.approx(2, abs=.02)
    assert abs(before.clean_price - after.clean_price) < .02


def test_last_day_before_redemption_and_one_period_solver():
    args = dict(BASE, settlement_date=date(2028, 11, 14))
    value = settled_bond_valuation(ytm=.05, **args)
    assert len(value.cashflows) == 1
    assert value.dirty_price == pytest.approx(102 / (1 + .025 / 184))
    assert value.clean_price == pytest.approx(100, abs=.01)
    assert settled_yield_to_maturity(price=value.dirty_price, price_type='dirty', **args) == pytest.approx(.05)


def test_end_of_month_schedule_and_leap_day():
    schedule = coupon_schedule(issue_date=date(2023, 8, 31), maturity_date=date(2025, 8, 31))
    assert schedule == [date(2023, 8, 31), date(2024, 2, 29), date(2024, 8, 31), date(2025, 2, 28), date(2025, 8, 31)]
    value = settled_bond_valuation(face_value=100, coupon_rate=.04, ytm=.05,
        issue_date=schedule[0], maturity_date=schedule[-1], settlement_date=date(2024, 2, 28))
    assert value.period_days == 182 and value.elapsed_days == 181
    assert value.accrued_interest == pytest.approx(2 * 181 / 182)


@pytest.mark.parametrize('frequency', [1, 2, 4, 12])
def test_regular_frequencies_and_scaling(frequency):
    args = dict(BASE, frequency=frequency, settlement_date=date(2026, 11, 15))
    value = settled_bond_valuation(ytm=.05, **args)
    assert value.dirty_price == pytest.approx(price_coupon_bond(face_value=100, coupon_rate=.04, ytm=.05, maturity_years=2, frequency=frequency))
    large = settled_bond_valuation(ytm=.05, **dict(args, face_value=1000))
    assert large.clean_price == pytest.approx(10 * value.clean_price)


@pytest.mark.parametrize('changes', [
    {'issue_date': date(2025, 11, 14)}, {'settlement_date': date(2025, 11, 14)},
    {'settlement_date': date(2028, 11, 15)}, {'settlement_date': date(2029, 1, 1)},
    {'maturity_date': date(2024, 11, 15)}, {'frequency': 3}, {'coupon_rate': -.01},
    {'ytm': -2}, {'ytm': float('nan')}, {'face_value': 0},
])
def test_invalid_dated_inputs(changes):
    args = dict(BASE, ytm=.05, **{})
    args.update(changes)
    with pytest.raises(ValueError):
        settled_bond_valuation(**args)


def test_unattainable_extreme_one_payment_yield_fails_promptly():
    with pytest.raises(ValueError, match='boundary'):
        settled_yield_to_maturity(price=1e6, **dict(BASE, settlement_date=date(2028, 11, 14)))


def test_treasurydirect_published_bill_price():
    # TreasuryDirect pricing page, 26-week $1,000 bill at 0.145% discount.
    value = treasury_bill(face_value=1000, discount_rate=.00145, days_to_maturity=182)
    assert round(value['price'], 2) == 999.27


def test_treasury_published_short_and_long_bill_examples():
    # Appendix B V.D: June 1–21, 1990; June 7, 1990–June 6, 1991.
    short = treasury_bill(discount_rate=.0793, days_to_maturity=20)
    assert short['price'] == pytest.approx(99.559444, abs=0.5e-6, rel=0)
    # The printed calculation rounds intermediate ratios. Match the final
    # published percentage, rather than reproducing that rounding internally.
    assert round(short['investment_rate'] * 100, 3) == 8.076
    long = treasury_bill(discount_rate=.0765, days_to_maturity=364)
    assert long['price'] == pytest.approx(92.265)
    assert long['investment_rate'] == pytest.approx(.082373244, abs=1e-9)


@pytest.mark.parametrize('year_days', [365, 366])
@pytest.mark.parametrize('days', [1, 182, 183, 364, 366])
def test_bill_yield_reconstructs_redemption(days, year_days):
    value = treasury_bill(discount_rate=.05, days_to_maturity=days, year_days=year_days)
    price, y = value['price'], value['investment_rate']
    if days <= year_days / 2:
        redemption = price * (1 + y * days / year_days)
    else:
        redemption = price * (1 + (days / year_days - .5) * y) * (1 + y / 2)
    assert redemption == pytest.approx(100)
    assert value['holding_return'] == pytest.approx((100 - price) / price)


@pytest.mark.parametrize('changes', [{'days_to_maturity': 0}, {'days_to_maturity': 367}, {'days_to_maturity': 1.5},
                                    {'days_to_maturity': True}, {'year_days': 360}, {'discount_rate': 10}, {'discount_rate': float('nan')}])
def test_bill_invalid_inputs(changes):
    args = dict(discount_rate=.05, days_to_maturity=182)
    args.update(changes)
    with pytest.raises(ValueError):
        treasury_bill(**args)
