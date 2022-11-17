from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas import CompanyValuation, OptionGrant, VestedEquityValuation
from app.services.vesting_calculator import get_valuated_vesting_schedule

router = APIRouter()


class EquityValuationRequest(BaseModel):
    option_grants: list[OptionGrant] = Field(..., min_items=1)
    company_valuations: list[CompanyValuation] = Field(..., min_items=1)


@router.post(
    '/vested_value',
    response_model=list[VestedEquityValuation],
)
def calculate_vested_value_timeline(
    options_info: EquityValuationRequest,
) -> Any:
    return get_valuated_vesting_schedule(
        options_info.option_grants,
        options_info.company_valuations
    )
