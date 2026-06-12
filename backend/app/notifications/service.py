from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.operations import Notification, NotificationStatus
from app.models.user import User, UserRole
from app.schemas.operations import NotificationCreate


class NotificationService:
    def list_notifications(self, db: Session, current_user: User) -> list[Notification]:
        if current_user.role == UserRole.patient and current_user.patient_profile:
            recipient = f"patient:{current_user.patient_profile.patient_id}"
            stmt = select(Notification).where(Notification.recipient == recipient).order_by(Notification.created_at.desc())
        else:
            stmt = select(Notification).order_by(Notification.created_at.desc())
        return list(db.scalars(stmt).all())

    def create_notification(self, db: Session, current_user: User, payload: NotificationCreate) -> Notification:
        if current_user.role not in {UserRole.admin, UserRole.staff, UserRole.doctor}:
            raise AppError("Access denied.", 403)
        notification = Notification(**payload.model_dump())
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    def mark_sent(self, db: Session, notification: Notification) -> Notification:
        notification.status = NotificationStatus.sent
        db.commit()
        db.refresh(notification)
        return notification

