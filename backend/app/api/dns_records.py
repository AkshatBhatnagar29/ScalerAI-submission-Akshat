from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..database.session import get_db
from ..schemas.dns_record import DNSRecordCreate, DNSRecordListResponse, DNSRecordResponse, DNSRecordUpdate, RecordType
from pydantic import BaseModel, Field
from ..services.dns_record import dns_record_service
from ..services.dns_zone_transfer import parse_zone_file

router = APIRouter(prefix="/api/hosted-zones/{hosted_zone_id}/records", tags=["dns records"])


class ZoneFileImport(BaseModel):
    zone_file: str = Field(min_length=1)


class ZoneFileImportResponse(BaseModel):
    imported_count: int
    records: list[DNSRecordResponse]


class ZoneFilePreviewRecord(BaseModel):
    name: str
    type: RecordType
    ttl: int
    value: str
    priority: int | None = None
    weight: int | None = None
    port: int | None = None
    flag: int | None = None
    tag: str | None = None


class ZoneFilePreviewResponse(BaseModel):
    imported_count: int
    records: list[ZoneFilePreviewRecord]


@router.post("/import/preview", response_model=ZoneFilePreviewResponse)
def preview_zone_file(hosted_zone_id: int, payload: ZoneFileImport, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> ZoneFilePreviewResponse:
    zone = dns_record_service.zone(db, hosted_zone_id, user)
    parsed = parse_zone_file(payload.zone_file, zone.name)
    if parsed.errors:
        raise HTTPException(status_code=422, detail={"message": "Zone file contains invalid records", "errors": parsed.errors})
    return ZoneFilePreviewResponse(imported_count=len(parsed.records), records=parsed.records)


@router.post("/import", response_model=ZoneFileImportResponse, status_code=status.HTTP_201_CREATED)
def import_zone_file(hosted_zone_id: int, payload: ZoneFileImport, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> ZoneFileImportResponse:
    records, _ = dns_record_service.import_zone_file(db, hosted_zone_id, payload.zone_file, user)
    return ZoneFileImportResponse(imported_count=len(records), records=records)


@router.get("", response_model=DNSRecordListResponse)
def list_records(hosted_zone_id: int, search: str | None = Query(default=None), type: RecordType | None = Query(default=None), page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> DNSRecordListResponse:
    items, total = dns_record_service.list(db, hosted_zone_id, search, type, page, page_size, user)
    return DNSRecordListResponse(items=items, page=page, page_size=page_size, total=total, total_pages=ceil(total / page_size) if total else 0)


@router.get("/{record_id}", response_model=DNSRecordResponse)
def get_record(hosted_zone_id: int, record_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> DNSRecordResponse:
    return dns_record_service.get(db, hosted_zone_id, record_id, user)


@router.post("", response_model=DNSRecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(hosted_zone_id: int, payload: DNSRecordCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> DNSRecordResponse:
    return dns_record_service.create(db, hosted_zone_id, payload, user)


@router.put("/{record_id}", response_model=DNSRecordResponse)
def update_record(hosted_zone_id: int, record_id: int, payload: DNSRecordUpdate, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> DNSRecordResponse:
    return dns_record_service.update(db, hosted_zone_id, record_id, payload, user)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(hosted_zone_id: int, record_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> Response:
    dns_record_service.delete(db, hosted_zone_id, record_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
