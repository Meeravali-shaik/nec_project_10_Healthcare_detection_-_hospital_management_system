from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_roles
from app.emergency.service import EmergencyService
from app.forecasting.service import ForecastingService
from app.models.operations import AlertSeverity, Bed, BedStatus, EmergencyAlert, Notification, OptimizationRecommendation, Resource, ResourceForecast, ResourceUsage, Staff, StaffSchedule, Ward
from app.models.user import User, UserRole
from app.notifications.service import NotificationService
from app.optimization.service import OptimizationService
from app.scheduling.service import SchedulingService
from app.resource_management.service import (
    allocate_bed,
    bed_statistics,
    create_bed,
    create_resource,
    create_staff,
    create_ward,
    discharge_bed,
    list_beds,
    list_resources,
    list_staff,
    list_wards,
    operations_summary,
    reserve_bed,
    record_resource_usage,
    transfer_bed,
    update_bed,
    update_resource,
    update_staff,
    update_ward,
    ward_analytics,
)
from app.schemas.operations import (
    BedCreate,
    BedRead,
    BedUpdate,
    EmergencyAlertCreate,
    EmergencyAlertRead,
    NotificationCreate,
    NotificationRead,
    OperationsSummary,
    OptimizationRecommendationRead,
    ResourceCreate,
    ResourceForecastRead,
    ResourceRead,
    ResourceUpdate,
    ResourceUsageCreate,
    ResourceUsageRead,
    StaffCreate,
    StaffRead,
    StaffScheduleCreate,
    StaffScheduleRead,
    StaffUpdate,
    WardCreate,
    WardRead,
    WardUpdate,
)

router = APIRouter()
forecasting_service = ForecastingService()
notification_service = NotificationService()
emergency_service = EmergencyService()
optimization_service = OptimizationService()
scheduling_service = SchedulingService()


def _ops_access(current_user: User) -> None:
    if current_user.role not in {UserRole.admin, UserRole.staff}:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/dashboard/summary", response_model=OperationsSummary)
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return operations_summary(db)


@router.get("/wards", response_model=list[WardRead])
def read_wards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return list_wards(db)


@router.post("/wards", response_model=WardRead, status_code=status.HTTP_201_CREATED)
def create_ward_endpoint(payload: WardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_ward(db, current_user, payload)


@router.put("/wards/{ward_id}", response_model=WardRead)
def update_ward_endpoint(ward_id: int, payload: WardUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ward = db.get(Ward, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    return update_ward(db, current_user, ward, payload)


@router.get("/beds", response_model=list[BedRead])
def read_beds(ward_id: int | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return list_beds(db, ward_id)


@router.post("/beds", response_model=BedRead, status_code=status.HTTP_201_CREATED)
def create_bed_endpoint(payload: BedCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_bed(db, current_user, payload)


@router.put("/beds/{bed_id}", response_model=BedRead)
def update_bed_endpoint(bed_id: int, payload: BedUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bed = db.get(Bed, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return update_bed(db, current_user, bed, payload)


@router.post("/beds/{bed_id}/allocate", response_model=BedRead)
def allocate_bed_endpoint(bed_id: int, patient_id: int, admission_date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bed = db.get(Bed, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return allocate_bed(db, current_user, bed, patient_id, admission_date)


@router.post("/beds/{bed_id}/discharge", response_model=BedRead)
def discharge_bed_endpoint(bed_id: int, discharge_date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bed = db.get(Bed, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return discharge_bed(db, current_user, bed, discharge_date)


@router.post("/beds/{bed_id}/reserve", response_model=BedRead)
def reserve_bed_endpoint(
    bed_id: int,
    patient_id: int | None = None,
    reservation_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bed = db.get(Bed, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return reserve_bed(db, current_user, bed, patient_id, reservation_date)


@router.post("/beds/{bed_id}/transfer")
def transfer_bed_endpoint(
    bed_id: int,
    target_bed_id: int,
    transfer_date: date,
    patient_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source_bed = db.get(Bed, bed_id)
    target_bed = db.get(Bed, target_bed_id)
    if not source_bed or not target_bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    source_bed, target_bed = transfer_bed(db, current_user, source_bed, target_bed, patient_id, transfer_date)
    return {
        "source_bed": BedRead.model_validate(source_bed).model_dump(),
        "target_bed": BedRead.model_validate(target_bed).model_dump(),
    }


@router.get("/resources", response_model=list[ResourceRead])
def read_resources(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return list_resources(db)


@router.post("/resources", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource_endpoint(payload: ResourceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_resource(db, current_user, payload)


@router.put("/resources/{resource_id}", response_model=ResourceRead)
def update_resource_endpoint(resource_id: int, payload: ResourceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return update_resource(db, current_user, resource, payload)


@router.post("/resources/usage", response_model=ResourceUsageRead, status_code=status.HTTP_201_CREATED)
def create_usage_endpoint(payload: ResourceUsageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return record_resource_usage(db, current_user, payload)


@router.get("/staff", response_model=list[StaffRead])
def read_staff(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return list_staff(db)


@router.post("/staff", response_model=StaffRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.admin))])
def create_staff_endpoint(payload: StaffCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_staff(db, current_user, payload)


@router.put("/staff/{staff_id}", response_model=StaffRead, dependencies=[Depends(require_roles(UserRole.admin))])
def update_staff_endpoint(staff_id: int, payload: StaffUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return update_staff(db, current_user, staff, payload)


@router.get("/schedules", response_model=list[StaffScheduleRead])
def read_schedules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    stmt = select(StaffSchedule).order_by(StaffSchedule.schedule_date.desc())
    return list(db.scalars(stmt).all())


@router.post("/schedules", response_model=StaffScheduleRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.admin, UserRole.staff))])
def create_schedule(payload: StaffScheduleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    schedule = StaffSchedule(**payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/alerts", response_model=list[EmergencyAlertRead])
def read_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), severity: AlertSeverity | None = Query(default=None)):
    _ops_access(current_user)
    return emergency_service.list_alerts(db, severity)


@router.post("/alerts", response_model=EmergencyAlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(payload: EmergencyAlertCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return emergency_service.create_alert(db, current_user, payload)


@router.post("/alerts/detect")
def detect_alerts(payload: dict, current_user: User = Depends(get_current_user)):
    if current_user.role not in {UserRole.admin, UserRole.staff, UserRole.doctor}:
        raise HTTPException(status_code=403, detail="Access denied")
    return emergency_service.detect_alerts(payload)


@router.get("/notifications", response_model=list[NotificationRead])
def read_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return notification_service.list_notifications(db, current_user)


@router.post("/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return notification_service.create_notification(db, current_user, payload)


@router.get("/forecast/resource-demand")
def forecast_resource_demand(resource_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    stmt = (
        select(ResourceUsage.usage_date.label("usage_date"), ResourceUsage.quantity_used.label("quantity"))
        .join(Resource, Resource.resource_id == ResourceUsage.resource_id)
        .where(Resource.resource_name == resource_name)
        .order_by(ResourceUsage.usage_date.asc())
    )
    history_rows = db.execute(stmt).all()
    history = [{"usage_date": row.usage_date, "quantity": row.quantity} for row in history_rows]
    result = forecasting_service.train_and_forecast(resource_name, history, horizon_days=7)
    records = []
    for item in result["predictions"]:
        forecast = ResourceForecast(
            resource_name=item["resource_name"],
            forecast_date=date.fromisoformat(item["forecast_date"]),
            horizon=item["horizon"],
            model_used=item["model_used"],
            predicted_demand=item["predicted_demand"],
            lower_bound=item["lower_bound"],
            upper_bound=item["upper_bound"],
        )
        db.add(forecast)
        records.append(forecast)
    db.commit()
    return {
        "model_used": result["model_used"],
        "comparison": result.get("comparison", []),
        "predictions": [ResourceForecastRead.model_validate(record).model_dump() for record in records],
    }


@router.get("/forecast/model-comparison")
def forecast_model_comparison(resource_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    stmt = (
        select(ResourceUsage.usage_date, ResourceUsage.quantity_used)
        .join(Resource, Resource.resource_id == ResourceUsage.resource_id)
        .where(Resource.resource_name == resource_name)
        .order_by(ResourceUsage.usage_date.asc())
    )
    history_rows = db.execute(stmt).all()
    history = [{"usage_date": row.usage_date, "quantity": row.quantity_used} for row in history_rows]
    result = forecasting_service.train_and_forecast(resource_name, history, horizon_days=7)
    return {"model_used": result["model_used"], "comparison": result.get("comparison", [])}


@router.post("/optimization/recommendations")
def optimization_recommendations(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    recommendations = optimization_service.recommend(payload)
    saved = []
    for item in recommendations:
        recommendation = OptimizationRecommendation(**item)
        db.add(recommendation)
        saved.append(recommendation)
    db.commit()
    return [OptimizationRecommendationRead.model_validate(item).model_dump() for item in saved]


@router.get("/optimization/recommendations", response_model=list[OptimizationRecommendationRead])
def list_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    stmt = select(OptimizationRecommendation).order_by(OptimizationRecommendation.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("/scheduling/recommendations")
def schedule_recommendations(payload: dict, current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return scheduling_service.recommend_staffing(payload)


@router.get("/analytics/beds")
def bed_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return bed_statistics(db)


@router.get("/analytics/wards")
def ward_analytics_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ops_access(current_user)
    return ward_analytics(db)
