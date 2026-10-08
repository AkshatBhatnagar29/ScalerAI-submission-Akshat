from datetime import datetime
import ipaddress
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


RecordType = Literal["A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR", "SRV", "CAA"]
HOSTNAME_RE = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?)(?:\.(?:[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?))*\.?$")


def valid_hostname(value: str) -> bool:
    return bool(HOSTNAME_RE.fullmatch(value)) and ".." not in value


class DNSRecordCreate(BaseModel):
    name: str = Field(min_length=1, max_length=253)
    type: RecordType
    ttl: int = Field(gt=0)
    value: str = Field(min_length=1)
    priority: int | None = Field(default=None, ge=0)
    weight: int | None = Field(default=None, ge=0)
    port: int | None = Field(default=None, ge=0, le=65535)
    flag: int | None = Field(default=None, ge=0, le=255)
    tag: str | None = Field(default=None, min_length=1, max_length=64)
    routing_policy: str | None = Field(default=None, max_length=64)
    comment: str | None = None

    @field_validator("name", "value")
    @classmethod
    def non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @field_validator("tag")
    @classmethod
    def non_blank_tag(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def validate_type_fields(self) -> "DNSRecordCreate":
        if self.type == "A":
            try:
                if ipaddress.ip_address(self.value).version != 4:
                    raise ValueError
            except ValueError as exc:
                raise ValueError("A records require a valid IPv4 address") from exc
        elif self.type == "AAAA":
            try:
                if ipaddress.ip_address(self.value).version != 6:
                    raise ValueError
            except ValueError as exc:
                raise ValueError("AAAA records require a valid IPv6 address") from exc
        elif self.type == "CNAME" and not valid_hostname(self.value):
            raise ValueError("CNAME records require a valid hostname")
        elif self.type == "MX":
            if self.priority is None:
                raise ValueError("MX records require priority")
            if not valid_hostname(self.value):
                raise ValueError("MX records require a valid mail server hostname")
        elif self.type == "SRV":
            if any(value is None for value in (self.priority, self.weight, self.port)):
                raise ValueError("SRV records require priority, weight, and port")
            if not valid_hostname(self.value):
                raise ValueError("SRV records require a valid target hostname")
        elif self.type == "CAA":
            if self.flag is None or self.tag is None:
                raise ValueError("CAA records require flag and tag")
        return self


class DNSRecordUpdate(DNSRecordCreate):
    pass


class DNSRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hosted_zone_id: int
    name: str
    type: RecordType
    ttl: int
    value: str
    priority: int | None
    weight: int | None
    port: int | None
    flag: int | None
    tag: str | None
    routing_policy: str | None
    comment: str | None
    created_at: datetime
    updated_at: datetime


class DNSRecordListResponse(BaseModel):
    items: list[DNSRecordResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
