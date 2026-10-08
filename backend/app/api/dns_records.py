from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..database.session import get_db
from ..schemas.dns_record import DNSRecordCreate, DNSRecordListResponse, DNSRecordResponse, DNSRecordUpdate, RecordType
from ..services.dns_record import dns_record_service

router = APIRouter(prefix="/api/hosted-zones/{hosted_zone_id}/records", tags=["dns records"])


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
