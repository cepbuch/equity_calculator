from datetime import date, datetime

from pydantic import errors
from pydantic.datetime_parse import StrBytesIntFloat, parse_date

from app.core.config import settings


class FormattedDate(date):
    """Date field formatted in settings.DATE_FORMAT for pydantic models."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    def validate(value: date | StrBytesIntFloat) -> date:
        """
        Parse date in settings.DATE_FORMAT only for str.
        Use standard pydantic parse_date function as a fallback.
        """
        if isinstance(value, str):
            try:
                return datetime.strptime(value, settings.DATE_FORMAT).date()
            except ValueError:
                raise errors.DateError()

        return parse_date(value)


class FormattedDateConfigMixin:
    """
    Serialize FormattedDate field with it's format

    Usage:
    class YourModel(BaseModel):
        date_field: FormattedDate

        class Config(FormattedDateConfigMixin):
            ...

    Watching https://github.com/pydantic/pydantic/discussions/4243
    for a better solution to be proposed.
    """
    json_encoders = {
        date: lambda date_: date_.strftime('%d-%m-%Y'),
    }
