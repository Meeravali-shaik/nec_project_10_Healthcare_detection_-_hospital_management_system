from datetime import date, datetime

from pydantic import Field

from app.models.operations import (
    AlertSeverity,
    BedStatus,
    BedType,
    NotificationChannel,
    NotificationStatus,
    ResourceMaintenanceStatus,
    StaffRole,
    StaffStatus,
    WardType,
)
from app.schemas.common import ORMBaseModel


class WardBase(ORMBaseModel):
    ward_name: str
    ward_type: WardType
    capacity: int
    occupied_beds: int = 0
    available_beds: int = 0


class WardCreate(WardBase):
    pass


class WardUpdate(ORMBaseModel):
    ward_name: str | None = None
    ward_type: WardType | None = None
    capacity: int | None = None
    occupied_beds: int | None = None
    available_beds: int | None = None


class WardRead(WardBase):
    ward_id: int
    created_at: datetime


class BedBase(ORMBaseModel):
    ward_id: int
    bed_number: str
    bed_type: BedType
    status: BedStatus = BedStatus.available
    patient_id: int | None = None
    admission_date: date | None = None
    discharge_date: date | None = None


class BedCreate(BedBase):
    pass


class BedUpdate(ORMBaseModel):
    ward_id: int | None = None
    bed_number: str | None = None
    bed_type: BedType | None = None
    status: BedStatus | None = None
    patient_id: int | None = None
    admission_date: date | None = None
    discharge_date: date | None = None


class BedRead(BedBase):
    bed_id: int
    created_at: datetime


class ResourceBase(ORMBaseModel):
    resource_name: str
    category: str
    quantity_available: int = 0
    quantity_in_use: int = 0
    maintenance_status: ResourceMaintenanceStatus = ResourceMaintenanceStatus.operational
    last_service_date: date | None = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(ORMBaseModel):
    resource_name: str | None = None
    category: str | None = None
    quantity_available: int | None = None
    quantity_in_use: int | None = None
    maintenance_status: ResourceMaintenanceStatus | None = None
    last_service_date: date | None = None


class ResourceRead(ResourceBase):
    resource_id: int
    created_at: datetime


class ResourceUsageBase(ORMBaseModel):
    resource_id: int
    usage_date: date
    quantity_used: int
    reason: str | None = None


class ResourceUsageCreate(ResourceUsageBase):
    pass


class ResourceUsageRead(ResourceUsageBase):
    usage_id: int
    created_at: datetime


class ResourceForecastBase(ORMBaseModel):
    resource_name: str
    forecast_date: date
    horizon: str
    model_used: str
    predicted_demand: float
    lower_bound: float
    upper_bound: float


class ResourceForecastRead(ResourceForecastBase):
    forecast_id: int
    created_at: datetime


class StaffBase(ORMBaseModel):
    name: str
    role: StaffRole
    department: str
    shift: str
    contact_number: str | None = None
    status: StaffStatus = StaffStatus.active


class StaffCreate(StaffBase):
    pass


class StaffUpdate(ORMBaseModel):
    name: str | None = None
    role: StaffRole | None = None
    department: str | None = None
    shift: str | None = None
    contact_number: str | None = None
    status: StaffStatus | None = None


class StaffRead(StaffBase):
    staff_id: int
    created_at: datetime


class StaffScheduleBase(ORMBaseModel):
    staff_id: int
    schedule_date: date
    start_time: str
    end_time: str
    department: str
    recommendation: str | None = None


class StaffScheduleCreate(StaffScheduleBase):
    pass


class StaffScheduleRead(StaffScheduleBase):
    schedule_id: int
    created_at: datetime


class EmergencyAlertBase(ORMBaseModel):
    alert_type: str
    severity: AlertSeverity
    recipient: str
    message: str
    acknowledged: bool = False


class EmergencyAlertCreate(EmergencyAlertBase):
    pass


class EmergencyAlertRead(EmergencyAlertBase):
    alert_id: int
    timestamp: datetime
    created_at: datetime


class NotificationBase(ORMBaseModel):
    recipient: str
    channel: NotificationChannel
    subject: str
    message: str
    status: NotificationStatus = NotificationStatus.pending
    reference_type: str | None = None
    reference_id: str | None = None


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    notification_id: int
    created_at: datetime


class OptimizationRecommendationBase(ORMBaseModel):
    recommendation_type: str
    title: str
    message: str
    priority: AlertSeverity
    metadata_json: dict = Field(default_factory=dict)


class OptimizationRecommendationRead(OptimizationRecommendationBase):
    recommendation_id: int
    created_at: datetime


class OperationsSummary(ORMBaseModel):
    total_beds: int
    available_beds: int
    occupied_beds: int
    icu_occupancy: float
    resource_usage: dict[str, float]
    staff_available: int
    emergency_alerts: int
