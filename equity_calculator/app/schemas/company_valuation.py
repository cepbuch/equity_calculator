from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas import FormattedDate


class CompanyValuation(BaseModel):
    price: Decimal = Field(..., gt=0)
    valuation_date: FormattedDate
