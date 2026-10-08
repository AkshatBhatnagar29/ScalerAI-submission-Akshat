from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from .api.auth import router as auth_router
from .api.hosted_zones import router as hosted_zones_router
from .api.dns_records import router as dns_records_router
from .core.config import FRONTEND_ORIGIN
from .database.base import Base
from .database.models import DNSRecord, HostedZone  # noqa: F401 - registers model metadata
from .database.session import engine

app = FastAPI(title="Route 53 Clone API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(auth_router)
app.include_router(hosted_zones_router)
app.include_router(dns_records_router)


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    # Phase 4 databases may already exist; add the Phase 5 structured fields in place.
    columns = {column["name"] for column in inspect(engine).get_columns("dns_records")}
    additions = {"weight": "INTEGER", "port": "INTEGER", "flag": "INTEGER", "tag": "VARCHAR(64)"}
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE dns_records ADD COLUMN {name} {definition}"))

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
