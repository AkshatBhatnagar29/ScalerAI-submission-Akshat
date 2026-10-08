from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..database.models import DNSRecord


class DNSRecordRepository:
    def create(self, db: Session, record: DNSRecord) -> DNSRecord:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get(self, db: Session, zone_id: int, record_id: int) -> DNSRecord | None:
        return db.scalar(select(DNSRecord).where(DNSRecord.id == record_id, DNSRecord.hosted_zone_id == zone_id))

    def list(self, db: Session, zone_id: int, search: str | None, record_type: str | None, page: int, page_size: int) -> tuple[list[DNSRecord], int]:
        query = select(DNSRecord).where(DNSRecord.hosted_zone_id == zone_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(or_(DNSRecord.name.ilike(pattern), DNSRecord.type.ilike(pattern), DNSRecord.value.ilike(pattern)))
        if record_type:
            query = query.where(DNSRecord.type == record_type)
        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = db.scalars(query.order_by(DNSRecord.name, DNSRecord.id).offset((page - 1) * page_size).limit(page_size)).all()
        return items, total

    def update(self, db: Session, record: DNSRecord) -> DNSRecord:
        db.commit()
        db.refresh(record)
        return record

    def delete(self, db: Session, record: DNSRecord) -> None:
        db.delete(record)
        db.commit()


dns_record_repository = DNSRecordRepository()
