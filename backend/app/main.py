from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.database.base import Base
from app.database.session import engine
from app.api.users import router as users_router
from app.api.providers import router as providers_router
from app.api.tariffs import router as tariffs_router
from app.api.calculator import router as calculator_router
from app.api.network import router as network_router
from app.api.tariff_network import router as tariff_network_router
from app.api.customers import router as customers_router
from app.api.contracts import router as contracts_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(providers_router)
app.include_router(tariffs_router)
app.include_router(calculator_router)
app.include_router(network_router)
app.include_router(tariff_network_router)
app.include_router(customers_router)
app.include_router(contracts_router)

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