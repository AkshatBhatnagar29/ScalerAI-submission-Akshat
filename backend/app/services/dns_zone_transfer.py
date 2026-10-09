import ipaddress
import json
import re
import shlex
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..database.models import DNSRecord, HostedZone
from ..schemas.dns_record import DNSRecordCreate, valid_hostname


SUPPORTED_TYPES = {"A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR", "SRV", "CAA"}
TTL_RE = re.compile(r"^(\d+)([smhdw]?)$", re.IGNORECASE)


@dataclass
class ParsedZoneFile:
    records: list[DNSRecordCreate]
    errors: list[str]


def _ttl(value: str) -> int:
    match = TTL_RE.fullmatch(value)
    if not match:
        raise ValueError("TTL must be a positive integer or use s, m, h, d, or w")
    amount = int(match.group(1))
    multiplier = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}[match.group(2).lower()]
    result = amount * multiplier
    if result <= 0:
        raise ValueError("TTL must be greater than zero")
    return result


def _name(value: str, zone_name: str) -> str:
    value = value.strip()
    if value == "@":
        return zone_name
    if value.endswith("."):
        result = value[:-1].lower()
    else:
        result = f"{value}.{zone_name}".lower()
    if not valid_hostname(result):
        raise ValueError("record name is not a valid hostname")
    return result


def _target(value: str, zone_name: str) -> str:
    if value == ".":
        return value
    return _name(value, zone_name)


def parse_zone_file(text: str, zone_name: str) -> ParsedZoneFile:
    records: list[DNSRecordCreate] = []
    errors: list[str] = []
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith(";") or raw_line.lstrip().startswith("#"):
            continue
        try:
            lexer = shlex.shlex(raw_line, posix=True)
            lexer.whitespace_split = True
            lexer.commenters = ";#"
            parts = list(lexer)
            if len(parts) < 4:
                raise ValueError("expected name, TTL, type, and value")
            name, ttl_text, record_type = parts[:3]
            if record_type.upper() == "IN" and len(parts) >= 5:
                ttl_text, record_type = parts[2], parts[3]
                values = parts[4:]
            else:
                values = parts[3:]
            record_type = record_type.upper()
            if record_type not in SUPPORTED_TYPES:
                raise ValueError(f"unsupported record type {record_type}")
            ttl = _ttl(ttl_text)
            record_name = _name(name, zone_name)
            fields: dict[str, object] = {"name": record_name, "type": record_type, "ttl": ttl}
            if record_type in {"A", "AAAA"}:
                if len(values) != 1:
                    raise ValueError("address records require one value")
                address = ipaddress.ip_address(values[0])
                if (record_type == "A" and address.version != 4) or (record_type == "AAAA" and address.version != 6):
                    raise ValueError(f"{record_type} records require the correct IP address family")
                fields["value"] = values[0]
            elif record_type in {"CNAME", "NS", "PTR"}:
                if len(values) != 1:
                    raise ValueError(f"{record_type} records require one target")
                fields["value"] = _target(values[0], zone_name)
            elif record_type == "TXT":
                if not values:
                    raise ValueError("TXT records require a value")
                fields["value"] = " ".join(values)
            elif record_type == "MX":
                if len(values) != 2 or not values[0].isdigit():
                    raise ValueError("MX records require priority and a mail server")
                fields.update(priority=int(values[0]), value=_target(values[1], zone_name))
            elif record_type == "SRV":
                if len(values) != 4 or not all(value.isdigit() for value in values[:3]):
                    raise ValueError("SRV records require priority, weight, port, and target")
                fields.update(priority=int(values[0]), weight=int(values[1]), port=int(values[2]), value=_target(values[3], zone_name))
            elif record_type == "CAA":
                if len(values) != 3 or not values[0].isdigit() or not values[1]:
                    raise ValueError("CAA records require flag, tag, and value")
                fields.update(flag=int(values[0]), tag=values[1], value=values[2])
            records.append(DNSRecordCreate(**fields))
        except (ValueError, TypeError) as exc:
            errors.append(f"Line {line_number}: {exc}")
    return ParsedZoneFile(records, errors)


def _key(record: DNSRecordCreate | DNSRecord) -> tuple[object, ...]:
    return (record.name.lower().rstrip("."), record.type, record.ttl, record.value, record.priority, record.weight, record.port, record.flag, record.tag)


def import_records(db: Session, zone: HostedZone, text: str) -> tuple[list[DNSRecord], list[str]]:
    parsed = parse_zone_file(text, zone.name)
    if parsed.errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"message": "Zone file contains invalid records", "errors": parsed.errors})
    seen: set[tuple[object, ...]] = set()
    for record in parsed.records:
        key = _key(record)
        if key in seen:
            raise HTTPException(status_code=409, detail="The zone file contains duplicate records")
        seen.add(key)
    existing = {_key(record) for record in zone.records}
    if existing.intersection(seen):
        raise HTTPException(status_code=409, detail="One or more imported records already exist in this hosted zone")
    created = [DNSRecord(hosted_zone_id=zone.id, **record.model_dump()) for record in parsed.records]
    db.add_all(created)
    zone.record_count = len(zone.records) + len(created)
    db.commit()
    for record in created:
        db.refresh(record)
    return created, []


def _bind_value(record: DNSRecord) -> str:
    if record.type == "MX":
        return f"{record.priority or 0} {record.value}." if not record.value.endswith(".") else f"{record.priority or 0} {record.value}"
    if record.type == "SRV":
        target = record.value if record.value.endswith(".") else f"{record.value}."
        return f"{record.priority or 0} {record.weight or 0} {record.port or 0} {target}"
    if record.type == "CAA":
        return f'{record.flag or 0} {record.tag or "issue"} "{record.value.replace(chr(34), chr(92)+chr(34))}"'
    if record.type in {"CNAME", "NS", "PTR"} and not record.value.endswith("."):
        return f"{record.value}."
    if record.type == "TXT":
        return '"' + record.value.replace('"', '\\"') + '"'
    return record.value


def export_json(zone: HostedZone) -> str:
    records = []
    for record in zone.records:
        item = {"name": record.name, "type": record.type, "ttl": record.ttl, "value": record.value, "routing_policy": record.routing_policy, "comment": record.comment}
        for field in ("priority", "weight", "port", "flag", "tag"):
            if getattr(record, field) is not None:
                item[field] = getattr(record, field)
        records.append(item)
    return json.dumps({"hosted_zone": {"name": zone.name, "type": zone.type, "description": zone.description, "zone_id": zone.zone_id}, "records": records}, indent=2)


def export_bind(zone: HostedZone) -> str:
    lines = [f"$ORIGIN {zone.name}.", "$TTL 300", ""]
    for record in sorted(zone.records, key=lambda item: (item.name, item.type, item.id)):
        name = "@" if record.name.rstrip(".") == zone.name else record.name.removesuffix(f".{zone.name}")
        lines.append(f"{name} {record.ttl} IN {record.type} {_bind_value(record)}")
    return "\n".join(lines) + "\n"
