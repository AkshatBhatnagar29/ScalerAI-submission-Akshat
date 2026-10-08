from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..database.models import DNSRecord, HostedZone, utc_now
from ..repositories.dns_record import dns_record_repository
from ..repositories.hosted_zone import hosted_zone_repository
from ..schemas.dns_record import DNSRecordCreate, DNSRecordUpdate, RecordType


class DNSRecordService:
    def zone(self, db: Session, zone_id: int, user: str) -> HostedZone:
        zone = hosted_zone_repository.get(db, zone_id, user)
        if zone is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hosted zone not found")
        return zone

    def create(self, db: Session, zone_id: int, payload: DNSRecordCreate, user: str) -> DNSRecord:
        self.zone(db, zone_id, user)
        self._validate_type_fields(payload)
        record = DNSRecord(hosted_zone_id=zone_id, **payload.model_dump())
        result = dns_record_repository.create(db, record)
        self._refresh_count(db, zone_id)
        return result

    def get(self, db: Session, zone_id: int, record_id: int, user: str) -> DNSRecord:
        self.zone(db, zone_id, user)
        record = dns_record_repository.get(db, zone_id, record_id)
        if record is None:
            raise HTTPException(status_code=404, detail="DNS record not found")
        return record

    def list(self, db: Session, zone_id: int, search: str | None, record_type: RecordType | None, page: int, page_size: int, user: str) -> tuple[list[DNSRecord], int]:
        self.zone(db, zone_id, user)
        return dns_record_repository.list(db, zone_id, search.strip() if search else None, record_type, page, page_size)

    def update(self, db: Session, zone_id: int, record_id: int, payload: DNSRecordUpdate, user: str) -> DNSRecord:
        record = self.get(db, zone_id, record_id, user)
        self._validate_type_fields(payload)
        for key, value in payload.model_dump().items():
            setattr(record, key, value)
        record.updated_at = utc_now()
        return dns_record_repository.update(db, record)

    def delete(self, db: Session, zone_id: int, record_id: int, user: str) -> None:
        record = self.get(db, zone_id, record_id, user)
        dns_record_repository.delete(db, record)
        self._refresh_count(db, zone_id)

    def _refresh_count(self, db: Session, zone_id: int) -> None:
        zone = db.get(HostedZone, zone_id)
        if zone is not None:
            zone.record_count = len(zone.records)
            db.commit()

    @staticmethod
    def _validate_type_fields(payload: DNSRecordCreate) -> None:
        """Retained as the service boundary for future business-rule validation."""
        return None


dns_record_service = DNSRecordService()
