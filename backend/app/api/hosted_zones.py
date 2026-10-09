from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import Response as RawResponse
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..database.session import get_db
from ..schemas.hosted_zone import HostedZoneCreate, HostedZoneListResponse, HostedZoneResponse, HostedZoneUpdate
from ..repositories.hosted_zone import hosted_zone_repository
from ..services.hosted_zone import hosted_zone_service
from ..services.dns_zone_transfer import export_bind, export_json

router = APIRouter(prefix="/api/hosted-zones", tags=["hosted zones"])


@router.get("/{zone_id}/export")
def export_hosted_zone(zone_id: int, format: str = Query(default="json", pattern="^(json|bind)$"), db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> RawResponse:
    zone = hosted_zone_service.get(db, zone_id, user)
    if format == "bind":
        filename = f"{zone.name}.zone"
        return RawResponse(export_bind(zone), media_type="text/dns", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    filename = f"{zone.name}.json"
    return RawResponse(export_json(zone), media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("", response_model=HostedZoneListResponse, summary="List and search hosted zones")
def list_hosted_zones(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
) -> HostedZoneListResponse:
    items, total = hosted_zone_repository.list(db, user, search.strip() if search else None, page, page_size)
    return HostedZoneListResponse(items=items, page=page, page_size=page_size, total=total, total_pages=ceil(total / page_size) if total else 0)


@router.get("/{zone_id}", response_model=HostedZoneResponse)
def get_hosted_zone(zone_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> HostedZoneResponse:
    return hosted_zone_service.get(db, zone_id, user)


@router.post("", response_model=HostedZoneResponse, status_code=status.HTTP_201_CREATED)
def create_hosted_zone(payload: HostedZoneCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> HostedZoneResponse:
    return hosted_zone_service.create(db, payload, user)


@router.put("/{zone_id}", response_model=HostedZoneResponse)
def update_hosted_zone(zone_id: int, payload: HostedZoneUpdate, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> HostedZoneResponse:
    return hosted_zone_service.update(db, zone_id, payload, user)


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hosted_zone(zone_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)) -> Response:
    hosted_zone_service.delete(db, zone_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
