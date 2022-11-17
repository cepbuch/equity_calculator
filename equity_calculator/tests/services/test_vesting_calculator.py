from datetime import date
from decimal import Decimal

import pytest
from app.schemas import CompanyValuation, OptionGrant
from app.services.vesting_calculator import (form_monthly_vesting_timeline,
                                             form_valuated_vesting_schedule,
                                             form_vesting_schedule)


def test_form_vesting_schedule_without_cliff() -> None:
    option_grant = OptionGrant(
        quantity=4,
        start_date='01-01-2022',
        cliff_months=0,
        duration_months=4,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 2, 1): 1,
        date(2022, 3, 1): 1,
        date(2022, 4, 1): 1,
        date(2022, 5, 1): 1,
    }


def test_form_vesting_schedule_skip_cliff_dates() -> None:
    option_grant = OptionGrant(
        quantity=4,
        start_date='01-01-2022',
        cliff_months=2,
        duration_months=4,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 3, 1): 2,
        date(2022, 4, 1): 1,
        date(2022, 5, 1): 1,
    }


def test_form_vesting_schedule_cliff_same_as_duration() -> None:
    option_grant = OptionGrant(
        quantity=4,
        start_date='01-01-2022',
        cliff_months=4,
        duration_months=4,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 5, 1): 4,
    }


def test_form_vesting_schedule_one_month_duration() -> None:
    option_grant = OptionGrant(
        quantity=5,
        start_date='01-01-2022',
        cliff_months=0,
        duration_months=1,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 2, 1): 5,
    }


def test_form_vesting_schedule_start_at_the_end_of_month() -> None:
    option_grant = OptionGrant(
        quantity=6,
        start_date='31-10-2021',
        cliff_months=3,
        duration_months=6,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 1, 31): 3,
        date(2022, 2, 28): 1,
        date(2022, 3, 31): 1,
        date(2022, 4, 30): 1,
    }


def test_form_vesting_schedule_monthly_vest_is_not_integer() -> None:
    option_grant = OptionGrant(
        quantity=12,
        start_date='01-01-2022',
        cliff_months=3,
        duration_months=5,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 4, 1): 7,
        date(2022, 5, 1): 2,
        date(2022, 6, 1): 3,
    }


def test_form_vesting_schedule_monthly_vest_is_periodic() -> None:
    option_grant = OptionGrant(
        # 1,(6) monthly
        quantity=10,
        start_date='01-01-2022',
        cliff_months=0,
        duration_months=6,
    )
    vesting_schedule = form_vesting_schedule([option_grant])

    assert vesting_schedule == {
        date(2022, 2, 1): 1,
        date(2022, 3, 1): 2,
        date(2022, 4, 1): 2,
        date(2022, 5, 1): 1,
        date(2022, 6, 1): 2,
        date(2022, 7, 1): 2,
    }


def test_form_vesting_schedule_multiple_grants_different_day() -> None:
    option_grants = [
        OptionGrant(
            quantity=2,
            start_date='01-01-2022',
            cliff_months=0,
            duration_months=2,
        ),
        OptionGrant(
            quantity=4,
            start_date='02-01-2022',
            cliff_months=0,
            duration_months=2,
        ),
    ]

    vesting_schedule = form_vesting_schedule(option_grants)

    assert vesting_schedule == {
        date(2022, 2, 1): 1,
        date(2022, 2, 2): 2,
        date(2022, 3, 1): 1,
        date(2022, 3, 2): 2,
    }


def test_form_vesting_schedule_multiple_grants_same_day() -> None:
    option_grants = [
        OptionGrant(
            quantity=10,
            start_date='14-01-2022',
            cliff_months=0,
            duration_months=4,
        ),
        OptionGrant(
            quantity=6,
            start_date='14-02-2022',
            cliff_months=2,
            duration_months=6,
        ),
        OptionGrant(
            quantity=2,
            start_date='14-03-2022',
            cliff_months=0,
            duration_months=2,
        ),
    ]

    vesting_schedule = form_vesting_schedule(option_grants)

    assert vesting_schedule == {
        date(2022, 2, 14): 2,  # 2 + pre-cliff + NA
        date(2022, 3, 14): 3,  # 3 + pre-cliff + pre-month
        date(2022, 4, 14): 5,  # 2 + 2 + 1
        date(2022, 5, 14): 5,  # 3 + 1 + 1
        date(2022, 6, 14): 1,  # NA + 1 + NA
        date(2022, 7, 14): 1,   # NA + 1 + NA
        date(2022, 8, 14): 1,   # NA + 1 + NA
    }


def test_form_monthly_vesting_timeline():
    vesting_schedule = {
        date(2022, 1, 6): 1,
        date(2022, 1, 7): 2,
        date(2022, 2, 8): 5,
        date(2022, 2, 9): 5,
    }
    start_date = date(2022, 1, 5)
    end_date = date(2022, 3, 5)

    monthly_schedule = form_monthly_vesting_timeline(
        vesting_schedule, start_date, end_date
    )

    assert monthly_schedule == {
        date(2022, 1, 5): 0,
        date(2022, 2, 1): 3,
        date(2022, 3, 1): 10,
        date(2022, 3, 5): 0,
    }


def test_form_monthly_vesting_timeline_start_and_end_dates_are_already_in_schedule():
    vesting_schedule = {
        date(2022, 1, 5): 3,
        date(2022, 1, 7): 1,
        date(2022, 1, 8): 1,
        date(2022, 2, 5): 3,
    }
    start_date = date(2022, 1, 5)
    end_date = date(2022, 2, 5)

    monthly_schedule = form_monthly_vesting_timeline(
        vesting_schedule, start_date, end_date
    )

    assert monthly_schedule == {
        date(2022, 1, 5): 3,
        date(2022, 2, 1): 2,
        date(2022, 2, 5): 3,
    }


def test_form_monthly_vesting_timeline_month_start_dates_already_in_timeline():
    vesting_schedule = {
        date(2022, 1, 29): 1,
        date(2022, 1, 30): 1,
        date(2022, 2, 1): 1,
    }
    start_date = date(2022, 1, 1)
    end_date = date(2022, 2, 2)

    monthly_schedule = form_monthly_vesting_timeline(
        vesting_schedule, start_date, end_date
    )

    assert monthly_schedule == {
        date(2022, 1, 1): 0,
        date(2022, 2, 1): 3,
        date(2022, 2, 2): 0,
    }


def test_form_monthly_vesting_timeline_schedule_is_already_monthly():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 1): 1,
        date(2022, 3, 1): 1,
    }
    start_date = date(2022, 1, 1)
    end_date = date(2022, 3, 1)

    monthly_schedule = form_monthly_vesting_timeline(
        vesting_schedule, start_date, end_date
    )

    assert monthly_schedule == {
        date(2022, 1, 1): 1,
        date(2022, 2, 1): 1,
        date(2022, 3, 1): 1,
    }


def test_form_monthly_vesting_timeline_empty_months():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 2): 1,
        date(2022, 4, 4): 1,
        date(2022, 5, 5): 1,
    }
    start_date = date(2022, 1, 1)
    end_date = date(2022, 5, 5)

    monthly_schedule = form_monthly_vesting_timeline(
        vesting_schedule, start_date, end_date
    )

    assert monthly_schedule == {
        date(2022, 1, 1): 1,
        date(2022, 2, 1): 0,
        date(2022, 3, 1): 1,
        date(2022, 4, 1): 0,
        date(2022, 5, 1): 1,
        date(2022, 5, 5): 1,
    }


def test_form_valuated_vesting_schedule():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 1): 1,
        date(2022, 3, 1): 1,
    }
    company_valuations = [
        CompanyValuation(
            price=10.0,
            valuation_date=date(2021, 12, 1),
        )
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': 10.0, 'date_': date(2022, 1, 1)},
        {'total_value': 20.0, 'date_': date(2022, 2, 1)},
        {'total_value': 30.0, 'date_': date(2022, 3, 1)},
    ]


def test_form_valuated_vesting_schedule_two_valuations():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 2): 1,
        date(2022, 3, 3): 1,
    }

    company_valuations = [
        CompanyValuation(
            price=10.0,
            valuation_date=date(2021, 12, 1),
        ),
        CompanyValuation(
            price=15.0,
            valuation_date=date(2022, 3, 2),
        ),
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': 10.0, 'date_': date(2022, 1, 1)},
        {'total_value': 20.0, 'date_': date(2022, 2, 2)},
        {'total_value': 45.0, 'date_': date(2022, 3, 3)},
    ]


def test_form_valuated_vesting_schedule_unsorted_valuations():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 2): 1,
        date(2022, 3, 3): 1,
    }

    company_valuations = [
        CompanyValuation(
            price=15.0,
            valuation_date=date(2022, 3, 2),
        ),
        CompanyValuation(
            price=10.0,
            valuation_date=date(2021, 12, 1),
        ),
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': 10.0, 'date_': date(2022, 1, 1)},
        {'total_value': 20.0, 'date_': date(2022, 2, 2)},
        {'total_value': 45.0, 'date_': date(2022, 3, 3)},
    ]


def test_form_valuated_vesting_schedule_valuation_after_schedule_start():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 2): 1,
        date(2022, 3, 3): 1,
    }

    company_valuations = [
        CompanyValuation(
            price=15.0,
            valuation_date=date(2022, 1, 2),
        ),
    ]

    with pytest.raises(ValueError):
        form_valuated_vesting_schedule(
            vesting_schedule, company_valuations
        )


def test_form_valuated_vesting_schedule_valuation_on_timeline_date():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 2): 1,
        date(2022, 3, 3): 1,
    }

    company_valuations = [
        CompanyValuation(
            price=10.0,
            valuation_date=date(2022, 1, 1),
        ),
        CompanyValuation(
            price=7.0,
            valuation_date=date(2022, 2, 2),
        ),
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': 10.0, 'date_': date(2022, 1, 1)},
        {'total_value': 14.0, 'date_': date(2022, 2, 2)},
        {'total_value': 21.0, 'date_': date(2022, 3, 3)},
    ]


def test_form_valuated_vesting_schedule_valuation_outside_period():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 1): 1,
        date(2022, 3, 1): 1,
    }

    company_valuations = [
        CompanyValuation(
            price=100.0,
            valuation_date=date(2020, 1, 1),
        ),
        CompanyValuation(
            price=10.00,
            valuation_date=date(2021, 12, 31),
        ),
        CompanyValuation(
            price=1000.00,
            valuation_date=date(2023, 12, 31),
        ),
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': 10.0, 'date_': date(2022, 1, 1)},
        {'total_value': 20.0, 'date_': date(2022, 2, 1)},
        {'total_value': 30.0, 'date_': date(2022, 3, 1)},
    ]


def test_form_valuated_vesting_schedule_dates_without_vesting():
    vesting_schedule = {
        date(2022, 1, 1): 3,
        date(2022, 2, 1): 0,
        date(2022, 3, 1): 0,
        date(2022, 4, 1): 3,
    }

    company_valuations = [
        CompanyValuation(
            price=10.0,
            valuation_date=date(2021, 12, 30),
        ),
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': 30.0, 'date_': date(2022, 1, 1)},
        {'total_value': 30.0, 'date_': date(2022, 2, 1)},
        {'total_value': 30.0, 'date_': date(2022, 3, 1)},
        {'total_value': 60.0, 'date_': date(2022, 4, 1)},
    ]


def test_form_valuated_vesting_schedule_decimal_price():
    vesting_schedule = {
        date(2022, 1, 1): 1,
        date(2022, 2, 1): 2,
        date(2022, 3, 1): 1,
    }

    company_valuations = [
        CompanyValuation(
            price=0.357582,
            valuation_date=date(2021, 12, 30),
        ),
    ]

    valuated_schedule = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations
    )

    result_dict = [dict(v) for v in valuated_schedule]

    assert result_dict == [
        {'total_value': Decimal('0.357582'), 'date_': date(2022, 1, 1)},
        {'total_value': Decimal('0.357582') * 3, 'date_': date(2022, 2, 1)},
        {'total_value': Decimal('0.357582') * 4, 'date_': date(2022, 3, 1)},
    ]
