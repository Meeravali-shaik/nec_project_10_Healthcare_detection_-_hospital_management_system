from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(ORMBaseModel):
    created_at: datetime | None = None


class DateOnlyMixin(ORMBaseModel):
    date_of_birth: date | None = None


class TimeOnlyMixin(ORMBaseModel):
    appointment_time: time | None = None
