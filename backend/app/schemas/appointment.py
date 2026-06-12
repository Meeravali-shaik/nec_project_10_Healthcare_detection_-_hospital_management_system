from datetime import date, time

from app.models.appointment import AppointmentStatus
from app.schemas.common import ORMBaseModel


class AppointmentBase(ORMBaseModel):
    patient_id: int | None = None
    doctor_id: int
    appointment_date: date
    appointment_time: time
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(ORMBaseModel):
    appointment_date: date | None = None
    appointment_time: time | None = None
    notes: str | None = None


class AppointmentStatusUpdate(ORMBaseModel):
    appointment_status: AppointmentStatus


class AppointmentRead(AppointmentBase):
    appointment_id: int
    appointment_status: AppointmentStatus
