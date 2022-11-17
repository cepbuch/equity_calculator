from pydantic import BaseModel, NonNegativeInt, PositiveInt, root_validator

from app.schemas import FormattedDate


class OptionGrant(BaseModel):
    quantity: PositiveInt
    start_date: FormattedDate
    cliff_months: NonNegativeInt
    duration_months: PositiveInt

    @root_validator(pre=False)
    def check_cliff_months_is_within_durations_months(cls, values: dict) -> dict:
        cliff_months: int = values['cliff_months']
        duration_months: int = values['duration_months']

        if cliff_months > duration_months:
            raise ValueError('Cliff months value must be within the duration months')

        return values
