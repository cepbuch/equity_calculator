from decimal import Decimal

from pydantic import BaseModel, Field, validator

from app.schemas import FormattedDate, FormattedDateConfigMixin


class VestedEquityValuation(BaseModel):
    total_value: Decimal
    date_: FormattedDate = Field(..., alias='date')

    @validator('total_value', pre=False)
    def check_total_value_gte_zero(cls, value: Decimal):
        if value < Decimal(0):
            raise ValueError('Must be greater than or equal to zero')
        return value

    class Config(FormattedDateConfigMixin):
        allow_population_by_field_name = True
