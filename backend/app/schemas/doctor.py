from app.schemas.common import ORMBaseModel


class DoctorBase(ORMBaseModel):
    full_name: str
    specialization: str | None = None
    department: str | None = None
    qualification: str | None = None
    experience_years: int | None = None
    consultation_fee: float | None = None
    phone_number: str | None = None
    email: str | None = None
    availability_status: bool = True


class DoctorCreate(DoctorBase):
    user_id: int | None = None


class DoctorUpdate(DoctorBase):
    full_name: str | None = None
    specialization: str | None = None
    department: str | None = None
    qualification: str | None = None
    experience_years: int | None = None
    consultation_fee: float | None = None
    phone_number: str | None = None
    email: str | None = None
    availability_status: bool | None = None


class DoctorRead(DoctorBase):
    doctor_id: int
    user_id: int | None = None
