from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ZoneType = Literal["PUBLIC", "PRIVATE"]


class HostedZoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=253)
    type: ZoneType
    description: str | None = Field(default=None, max_length=2000)


class HostedZoneUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=253)
    type: ZoneType | None = None
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("name must not be blank")
        return value


class HostedZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: ZoneType
    description: str | None
    created_by: str
    record_count: int
    zone_id: str
    created_at: datetime
    updated_at: datetime


class HostedZoneListResponse(BaseModel):
    items: list[HostedZoneResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
