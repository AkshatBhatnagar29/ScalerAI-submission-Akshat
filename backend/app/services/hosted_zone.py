import re
import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from ..database.models import HostedZone, utc_now
from ..repositories.hosted_zone import hosted_zone_repository
from ..schemas.hosted_zone import HostedZoneCreate, HostedZoneUpdate


DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$")


def normalize_name(value: str) -> str:
    name = value.strip().rstrip(".").lower()
    if not name or not DOMAIN_RE.fullmatch(name) or "." not in name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid hosted zone name")
    return name


def generate_zone_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "/hostedzone/Z" + "".join(secrets.choice(alphabet) for _ in range(12))


class HostedZoneService:
    def create(self, db: Session, payload: HostedZoneCreate, user: str) -> HostedZone:
        name = normalize_name(payload.name)
        if hosted_zone_repository.exists_by_name_type(db, name, payload.type, user):
            raise HTTPException(status_code=409, detail="Hosted zone already exists")
        zone = HostedZone(name=name, type=payload.type, description=payload.description, created_by=user, zone_id=generate_zone_id())
        return hosted_zone_repository.create(db, zone)

    def get(self, db: Session, zone_id: int, user: str) -> HostedZone:
        self._ensure_record_columns(db)
        zone = hosted_zone_repository.get(db, zone_id, user)
        if zone is None:
            raise HTTPException(status_code=404, detail="Hosted zone not found")
        zone.record_count = len(zone.records)
        return zone

    @staticmethod
    def _ensure_record_columns(db: Session) -> None:
        bind = db.get_bind()
        columns = {column["name"] for column in inspect(bind).get_columns("dns_records")}
        additions = {"weight": "INTEGER", "port": "INTEGER", "flag": "INTEGER", "tag": "VARCHAR(64)"}
        with bind.begin() as connection:
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE dns_records ADD COLUMN {name} {definition}"))

    def update(self, db: Session, zone_id: int, payload: HostedZoneUpdate, user: str) -> HostedZone:
        zone = self.get(db, zone_id, user)
        values = payload.model_dump(exclude_unset=True)
        name = normalize_name(values["name"]) if "name" in values and values["name"] is not None else zone.name
        zone_type = values.get("type", zone.type)
        if hosted_zone_repository.exists_by_name_type(db, name, zone_type, user, exclude_id=zone.id):
            raise HTTPException(status_code=409, detail="Hosted zone already exists")
        zone.name = name
        zone.type = zone_type
        if "description" in values:
            zone.description = values["description"]
        zone.updated_at = utc_now()
        return hosted_zone_repository.update(db, zone)

    def delete(self, db: Session, zone_id: int, user: str) -> None:
        zone = self.get(db, zone_id, user)
        hosted_zone_repository.delete(db, zone)


hosted_zone_service = HostedZoneService()
