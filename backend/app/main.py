from fastapi import FastAPI

from app.database.base import Base
from app.database.session import engine
from app.models import (
    Provider,
    Tariff,
    Commission,
    Customer,
    Contract,
    User,
    UserRole,
    ContractStatus,
    ContractStatusHistory,
    Document,
    DocumentType,
)

app = FastAPI(
    title="gigawatt-portal API",
    version="0.1.0",
    description="Energy tariff comparison and sales platform"
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "application": "gigawatt-portal",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }