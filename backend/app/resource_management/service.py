from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.operations import Bed, BedStatus, BedType, EmergencyAlert, Notification, OptimizationRecommendation, Resource, ResourceUsage, Staff, StaffStatus, Ward
from app.models.user import User, UserRole
from app.schemas.operations import BedCreate, BedUpdate, ResourceCreate, ResourceUpdate, ResourceUsageCreate, StaffCreate, StaffUpdate, WardCreate, WardUpdate


def _require_ops_access(current_user: User) -> None:
    if current_user.role not in {UserRole.admin, UserRole.staff}:
        raise AppError("Access denied.", 403)


def _require_admin(current_user: User) -> None:
    if current_user.role != UserRole.admin:
        raise AppError("Admin access required.", 403)


def list_wards(db: Session) -> list[Ward]:
    return list(db.scalars(select(Ward).order_by(Ward.ward_name.asc())).all())


def create_ward(db: Session, current_user: User, payload: WardCreate) -> Ward:
    _require_ops_access(current_user)
    ward = Ward(**payload.model_dump())
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


def update_ward(db: Session, current_user: User, ward: Ward, payload: WardUpdate) -> Ward:
    _require_ops_access(current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(ward, key, value)
    db.commit()
    db.refresh(ward)
    return ward


def list_beds(db: Session, ward_id: int | None = None) -> list[Bed]:
    stmt = select(Bed).order_by(Bed.bed_number.asc())
    if ward_id is not None:
        stmt = stmt.where(Bed.ward_id == ward_id)
    return list(db.scalars(stmt).all())


def create_bed(db: Session, current_user: User, payload: BedCreate) -> Bed:
    _require_ops_access(current_user)
    bed = Bed(**payload.model_dump())
    db.add(bed)
    db.commit()
    db.refresh(bed)
    _sync_ward_bed_counts(db, bed.ward_id)
    return bed


def update_bed(db: Session, current_user: User, bed: Bed, payload: BedUpdate) -> Bed:
    _require_ops_access(current_user)
    previous_ward_id = bed.ward_id
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(bed, key, value)
    db.commit()
    db.refresh(bed)
    _sync_ward_bed_counts(db, previous_ward_id)
    _sync_ward_bed_counts(db, bed.ward_id)
    return bed


def allocate_bed(db: Session, current_user: User, bed: Bed, patient_id: int, admission_date) -> Bed:
    _require_ops_access(current_user)
    bed.patient_id = patient_id
    bed.admission_date = admission_date
    bed.discharge_date = None
    bed.status = BedStatus.occupied
    db.commit()
    db.refresh(bed)
    _sync_ward_bed_counts(db, bed.ward_id)
    return bed


def discharge_bed(db: Session, current_user: User, bed: Bed, discharge_date) -> Bed:
    _require_ops_access(current_user)
    bed.discharge_date = discharge_date
    bed.patient_id = None
    bed.status = BedStatus.available
    db.commit()
    db.refresh(bed)
    _sync_ward_bed_counts(db, bed.ward_id)
    return bed


def reserve_bed(db: Session, current_user: User, bed: Bed, patient_id: int | None, reservation_date: date | None) -> Bed:
    _require_ops_access(current_user)
    bed.patient_id = patient_id
    bed.admission_date = reservation_date or date.today()
    bed.discharge_date = None
    bed.status = BedStatus.reserved
    db.commit()
    db.refresh(bed)
    _sync_ward_bed_counts(db, bed.ward_id)
    return bed


def transfer_bed(
    db: Session,
    current_user: User,
    source_bed: Bed,
    target_bed: Bed,
    patient_id: int | None,
    transfer_date: date,
) -> tuple[Bed, Bed]:
    _require_ops_access(current_user)
    target_patient_id = patient_id if patient_id is not None else source_bed.patient_id
    source_bed.discharge_date = transfer_date
    source_bed.patient_id = None
    source_bed.status = BedStatus.available
    target_bed.patient_id = target_patient_id
    target_bed.admission_date = transfer_date
    target_bed.discharge_date = None
    target_bed.status = BedStatus.occupied
    db.commit()
    db.refresh(source_bed)
    db.refresh(target_bed)
    _sync_ward_bed_counts(db, source_bed.ward_id)
    _sync_ward_bed_counts(db, target_bed.ward_id)
    return source_bed, target_bed


def list_resources(db: Session) -> list[Resource]:
    return list(db.scalars(select(Resource).order_by(Resource.resource_name.asc())).all())


def create_resource(db: Session, current_user: User, payload: ResourceCreate) -> Resource:
    _require_ops_access(current_user)
    resource = Resource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def update_resource(db: Session, current_user: User, resource: Resource, payload: ResourceUpdate) -> Resource:
    _require_ops_access(current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)
    db.commit()
    db.refresh(resource)
    return resource


def record_resource_usage(db: Session, current_user: User, payload: ResourceUsageCreate) -> ResourceUsage:
    _require_ops_access(current_user)
    resource = db.get(Resource, payload.resource_id)
    if not resource:
        raise AppError("Resource not found.", 404)
    usage = ResourceUsage(**payload.model_dump())
    resource.quantity_available = max(resource.quantity_available - payload.quantity_used, 0)
    resource.quantity_in_use += payload.quantity_used
    db.add(usage)
    db.commit()
    db.refresh(usage)
    db.refresh(resource)
    return usage


def list_staff(db: Session) -> list[Staff]:
    return list(db.scalars(select(Staff).order_by(Staff.name.asc())).all())


def create_staff(db: Session, current_user: User, payload: StaffCreate) -> Staff:
    _require_admin(current_user)
    staff = Staff(**payload.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def update_staff(db: Session, current_user: User, staff: Staff, payload: StaffUpdate) -> Staff:
    _require_admin(current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff


def operations_summary(db: Session) -> dict:
    total_beds = db.scalar(select(func.count()).select_from(Bed)) or 0
    available_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.status == BedStatus.available)) or 0
    occupied_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.status == BedStatus.occupied)) or 0
    icu_occupancy = 0.0
    icu_total = db.scalar(select(func.count()).select_from(Bed).where(Bed.bed_type == BedType.icu)) or 0
    icu_occ = db.scalar(select(func.count()).select_from(Bed).where(Bed.bed_type == BedType.icu, Bed.status == BedStatus.occupied)) or 0
    if icu_total:
        icu_occupancy = round((icu_occ / icu_total) * 100, 2)
    resource_usage = {
        row[0]: float(row[1] or 0)
        for row in db.execute(select(Resource.category, func.coalesce(func.sum(Resource.quantity_in_use), 0)).group_by(Resource.category)).all()
    }
    staff_available = db.scalar(select(func.count()).select_from(Staff).where(Staff.status == StaffStatus.active)) or 0
    emergency_alerts = db.scalar(select(func.count()).select_from(EmergencyAlert).where(EmergencyAlert.acknowledged.is_(False))) or 0
    return {
        "total_beds": total_beds,
        "available_beds": available_beds,
        "occupied_beds": occupied_beds,
        "icu_occupancy": icu_occupancy,
        "resource_usage": resource_usage,
        "staff_available": staff_available,
        "emergency_alerts": emergency_alerts,
    }


def bed_statistics(db: Session) -> dict:
    total = db.scalar(select(func.count()).select_from(Bed)) or 0
    by_status = {
        status.value: db.scalar(select(func.count()).select_from(Bed).where(Bed.status == status)) or 0
        for status in BedStatus
    }
    by_type = {
        bed_type.value: db.scalar(select(func.count()).select_from(Bed).where(Bed.bed_type == bed_type)) or 0
        for bed_type in BedType
    }
    occupancy = round(((by_status[BedStatus.occupied.value] / total) * 100), 2) if total else 0.0
    return {
        "total_beds": total,
        "occupancy_rate": occupancy,
        "by_status": by_status,
        "by_type": by_type,
    }


def ward_analytics(db: Session) -> list[dict]:
    wards = list(db.scalars(select(Ward).order_by(Ward.ward_name.asc())).all())
    analytics: list[dict] = []
    for ward in wards:
        utilization = round((ward.occupied_beds / ward.capacity) * 100, 2) if ward.capacity else 0.0
        analytics.append(
            {
                "ward_id": ward.ward_id,
                "ward_name": ward.ward_name,
                "ward_type": ward.ward_type.value,
                "capacity": ward.capacity,
                "occupied_beds": ward.occupied_beds,
                "available_beds": ward.available_beds,
                "utilization": utilization,
            }
        )
    return analytics


def _sync_ward_bed_counts(db: Session, ward_id: int) -> None:
    ward = db.get(Ward, ward_id)
    if not ward:
        return
    total = db.scalar(select(func.count()).select_from(Bed).where(Bed.ward_id == ward_id)) or 0
    occupied = db.scalar(select(func.count()).select_from(Bed).where(Bed.ward_id == ward_id, Bed.status == BedStatus.occupied)) or 0
    ward.capacity = max(ward.capacity, total)
    ward.occupied_beds = occupied
    ward.available_beds = max(total - occupied, 0)
    db.commit()
