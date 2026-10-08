from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..database.models import HostedZone


class HostedZoneRepository:
    def exists_by_name_type(self, db: Session, name: str, zone_type: str, user: str, exclude_id: int | None = None) -> bool:
        query = select(HostedZone.id).where(
            HostedZone.name == name, HostedZone.type == zone_type, HostedZone.created_by == user
        )
        if exclude_id is not None:
            query = query.where(HostedZone.id != exclude_id)
        return db.scalar(query) is not None

    def create(self, db: Session, zone: HostedZone) -> HostedZone:
        db.add(zone)
        db.commit()
        db.refresh(zone)
        return zone

    def get(self, db: Session, zone_id: int, user: str) -> HostedZone | None:
        return db.scalar(select(HostedZone).where(HostedZone.id == zone_id, HostedZone.created_by == user))

    def list(self, db: Session, user: str, search: str | None, page: int, page_size: int) -> tuple[list[HostedZone], int]:
        query = select(HostedZone).where(HostedZone.created_by == user)
        if search:
            pattern = f"%{search}%"
            query = query.where(or_(HostedZone.name.ilike(pattern), HostedZone.description.ilike(pattern), HostedZone.zone_id.ilike(pattern)))
        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = db.scalars(query.order_by(HostedZone.created_at.desc(), HostedZone.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
        return items, total

    def update(self, db: Session, zone: HostedZone) -> HostedZone:
        db.commit()
        db.refresh(zone)
        return zone

    def delete(self, db: Session, zone: HostedZone) -> None:
        db.delete(zone)
        db.commit()


hosted_zone_repository = HostedZoneRepository()
