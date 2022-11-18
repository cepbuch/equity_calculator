from collections import defaultdict
from datetime import date, datetime, time
from fractions import Fraction
from operator import attrgetter
from typing import DefaultDict, Optional

from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, rrule

from app.schemas import CompanyValuation, OptionGrant, VestedEquityValuation


def get_valuated_vesting_schedule(
    option_grants: list[OptionGrant],
    company_valuations: list[CompanyValuation],
) -> list[VestedEquityValuation]:
    if not option_grants or not company_valuations:
        raise ValueError(
            'At least one grant and one valuation '
            'must be provided for the computation.'
        )

    vesting_schedule = form_vesting_schedule(option_grants)

    vesting_start_date = min(option_grants, key=attrgetter('start_date')).start_date
    vesting_end_date = max(vesting_schedule)

    vesting_schedule = form_monthly_vesting_timeline(
        vesting_schedule, vesting_start_date, vesting_end_date,
    )

    vested_equity_valuations = form_valuated_vesting_schedule(
        vesting_schedule, company_valuations,
    )

    return vested_equity_valuations


def form_vesting_schedule(option_grants: list[OptionGrant]) -> dict[date, int]:
    """
        Return dates-to-quantity when stock options are vested for all provided grants.
        Quantity of stock options from different grants vested on the same date is summed up.
        Dates when no stock options are vested (before the cliff, for example) are not included.
    """
    date_to_vested_quantity: DefaultDict[date, int] = defaultdict(int)

    for grant in option_grants:
        monthly_vested_quantity_f = Fraction(grant.quantity, grant.duration_months)
        prev_month_decimal_remainder = Fraction(0)

        vesting_start_month_day = grant.start_date.day
        after_cliff_start_date: date = grant.start_date

        if grant.cliff_months:
            cliff_date = _get_next_vesting_date(
                grant.start_date, grant.cliff_months, vesting_start_month_day
            )

            cliff_vest_quantity, prev_month_decimal_remainder = _calculate_vested_quantity(
                monthly_vested_quantity_f, prev_month_decimal_remainder,
                months=grant.cliff_months
            )

            if cliff_vest_quantity:
                date_to_vested_quantity[cliff_date] += cliff_vest_quantity

            after_cliff_start_date = cliff_date

        vesting_end_date = _get_next_vesting_date(
            grant.start_date, grant.duration_months, vesting_start_month_day
        )

        timeline_date = _get_next_vesting_date(
            after_cliff_start_date, 1, vesting_start_month_day
        )

        while timeline_date <= vesting_end_date:
            vest_quantity, prev_month_decimal_remainder = _calculate_vested_quantity(
                monthly_vested_quantity_f, prev_month_decimal_remainder,
            )

            if vest_quantity:
                date_to_vested_quantity[timeline_date] += vest_quantity

            timeline_date = _get_next_vesting_date(timeline_date, 1, vesting_start_month_day)

    return dict(date_to_vested_quantity)


def _get_next_vesting_date(from_date: date, months: int, initial_day: int) -> date:
    """
        Get date in `months` from `from_date` with also trying
        to set the `initial_day` for months when it is possible or
        the last month day when there is not such day (e.g. not every month has 31 days)
    """
    return from_date + relativedelta(months=+months, day=initial_day)


def _calculate_vested_quantity(
    monthly_vested_quantity: Fraction,
    prev_month_remainder: Fraction,
    months: int = 1
) -> tuple[int, Fraction]:
    quantity_to_vest = monthly_vested_quantity * months + prev_month_remainder
    vested_quantity = int(quantity_to_vest)
    not_vested_remainder = quantity_to_vest - vested_quantity
    return vested_quantity, not_vested_remainder


def form_monthly_vesting_timeline(
    vesting_schedule: dict[date, int],
    start_date: date, end_date: date,
) -> dict[date, int]:
    """
        By vesting schedule (can be received with `form_vesting_schedule`) provide
        a monthly vesting timeline.

        Structure:
        yyyy.mm.dd (start_date) > yyyy.mm+1.01 > yyyy.mm+2.01 > ... > yyyy.mm.dd (end_date).

        On the first day of the month accumulates all vested stock options for the past month
        (except start and end dates).
    """
    monthly_vesting_schedule = defaultdict(int, vesting_schedule)

    # Add key for every month start in the overall vesting period
    start_date_month_start = start_date.replace(day=1)

    monthly_timeline_rrule = rrule(
        MONTHLY,
        dtstart=datetime.combine(start_date_month_start, time.min),
        until=datetime.combine(end_date, time.max),
    )

    for dt in monthly_timeline_rrule[1:]:
        monthly_vesting_schedule[dt.date()] += 0

    # Add keys for start and end dates
    monthly_vesting_schedule[start_date] += 0
    monthly_vesting_schedule[end_date] += 0

    # Rearrange vesting schedule date for the first day of the next month
    for timeline_date, date_vested_quantity in list(monthly_vesting_schedule.items()):
        if timeline_date.day == 1 or timeline_date == start_date or timeline_date == end_date:
            continue

        next_month_start_date = (timeline_date + relativedelta(months=+1)).replace(day=1)

        monthly_vesting_schedule[next_month_start_date] += date_vested_quantity
        del monthly_vesting_schedule[timeline_date]

    return dict(monthly_vesting_schedule)


def form_valuated_vesting_schedule(
    vesting_schedule: dict[date, int],
    company_valuations: list[CompanyValuation],
) -> list[VestedEquityValuation]:
    """
        By vesting schedule and company_valuations provide equity value timeline.

        For each date take the last company valuation price prior to the date and
        multiply it with the cumulative vested stock options quantity.
    """
    sorted_vesting_schedule = sorted(vesting_schedule.items())
    sorted_valuations = sorted(company_valuations, key=lambda cv: cv.valuation_date)

    timeline_current_valuation = None

    # Take the last actual valuation before the start of the timeline
    earliest_vesting_date = sorted_vesting_schedule[0][0]

    for valuation in sorted_valuations:
        if valuation.valuation_date > earliest_vesting_date:
            break

        timeline_current_valuation = valuation

    if not timeline_current_valuation:
        raise ValueError('Unknown stock price at the start of the timeline')

    try:
        timeline_next_valuation: Optional[CompanyValuation] = sorted_valuations[1]
        timeline_next_valuation_idx = 1
    except IndexError:
        # Only one valuation is provided
        timeline_next_valuation = None
        timeline_next_valuation_idx = -1

    # Calculate equity valuation by last valuation price at every schedule point
    valuated_vesting_schedule: list[VestedEquityValuation] = []
    overall_vested_quantity = 0

    for timeline_date, last_month_vested_quantity in sorted_vesting_schedule:
        if timeline_next_valuation and timeline_date >= timeline_next_valuation.valuation_date:
            timeline_current_valuation = timeline_next_valuation

            try:
                timeline_next_valuation_idx += 1
                timeline_next_valuation = sorted_valuations[timeline_next_valuation_idx]
            except IndexError:
                timeline_next_valuation = None
                timeline_next_valuation_idx = -1

        overall_vested_quantity += last_month_vested_quantity
        valuated_vesting_schedule.append(
            VestedEquityValuation(
                date_=timeline_date,
                total_value=timeline_current_valuation.price * overall_vested_quantity,
            )
        )

    return valuated_vesting_schedule
