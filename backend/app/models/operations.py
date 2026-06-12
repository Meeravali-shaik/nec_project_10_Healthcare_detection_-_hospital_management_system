from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BedType(str, Enum):
    general = "General Ward Bed"
    icu = "ICU Bed"
    emergency = "Emergency Bed"
    isolation = "Isolation Bed"
    pediatric = "Pediatric Bed"


class BedStatus(str, Enum):
    available = "Available"
    occupied = "Occupied"
    reserved = "Reserved"
    maintenance = "Maintenance"


class WardType(str, Enum):
    general = "General"
    icu = "ICU"
    emergency = "Emergency"
    isolation = "Isolation"
    pediatric = "Pediatric"


class ResourceMaintenanceStatus(str, Enum):
    operational = "Operational"
    needs_service = "Needs Service"
    under_maintenance = "Under Maintenance"


class StaffRole(str, Enum):
    doctor = "Doctor"
    nurse = "Nurse"
    technician = "Technician"
    receptionist = "Receptionist"
    administrator = "Administrator"


class StaffStatus(str, Enum):
    active = "Active"
    on_leave = "On Leave"
    off_duty = "Off Duty"


class AlertSeverity(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class NotificationChannel(str, Enum):
    email = "Email"
    sms = "SMS"
    whatsapp = "WhatsApp"
    in_app = "In-App"


class NotificationStatus(str, Enum):
    pending = "Pending"
    sent = "Sent"
    failed = "Failed"


class Bed(Base):
    __tablename__ = "beds"

    bed_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.ward_id"), nullable=False, index=True)
    bed_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    bed_type: Mapped[BedType] = mapped_column(SQLEnum(BedType), nullable=False)
    status: Mapped[BedStatus] = mapped_column(SQLEnum(BedStatus), default=BedStatus.available, nullable=False)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.patient_id"), nullable=True, index=True)
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    discharge_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    ward = relationship("Ward", back_populates="beds")
    patient = relationship("Patient")


class Ward(Base):
    __tablename__ = "wards"

    ward_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ward_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    ward_type: Mapped[WardType] = mapped_column(SQLEnum(WardType), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    occupied_beds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_beds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    beds = relationship("Bed", back_populates="ward", cascade="all, delete-orphan")


class Resource(Base):
    __tablename__ = "resources"

    resource_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quantity_in_use: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    maintenance_status: Mapped[ResourceMaintenanceStatus] = mapped_column(SQLEnum(ResourceMaintenanceStatus), default=ResourceMaintenanceStatus.operational, nullable=False)
    last_service_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    usages = relationship("ResourceUsage", back_populates="resource", cascade="all, delete-orphan")


class ResourceUsage(Base):
    __tablename__ = "resource_usages"

    usage_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.resource_id"), nullable=False, index=True)
    usage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity_used: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    resource = relationship("Resource", back_populates="usages")


class ResourceForecast(Base):
    __tablename__ = "resource_forecasts"

    forecast_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_name: Mapped[str] = mapped_column(String(150), nullable=False)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(50), nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_demand: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[float] = mapped_column(Float, nullable=False)
    upper_bound: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Staff(Base):
    __tablename__ = "staff"

    staff_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[StaffRole] = mapped_column(SQLEnum(StaffRole), nullable=False)
    department: Mapped[str] = mapped_column(String(150), nullable=False)
    shift: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[StaffStatus] = mapped_column(SQLEnum(StaffStatus), default=StaffStatus.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    schedules = relationship("StaffSchedule", back_populates="staff", cascade="all, delete-orphan")


class StaffSchedule(Base):
    __tablename__ = "staff_schedules"

    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.staff_id"), nullable=False, index=True)
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[str] = mapped_column(String(20), nullable=False)
    end_time: Mapped[str] = mapped_column(String(20), nullable=False)
    department: Mapped[str] = mapped_column(String(150), nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    staff = relationship("Staff", back_populates="schedules")


class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    alert_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_type: Mapped[str] = mapped_column(String(150), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    recipient: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipient: Mapped[str] = mapped_column(String(150), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(SQLEnum(NotificationChannel), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), default=NotificationStatus.pending, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recommendation_type: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity), nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

