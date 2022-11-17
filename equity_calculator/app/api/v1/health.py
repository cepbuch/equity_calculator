from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get('/ping')
def ping() -> Any:
    return
