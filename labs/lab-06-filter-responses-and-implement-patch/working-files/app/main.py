from __future__ import annotations

import logging
import os
import secrets
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import repository
from .db import database_path, init_db
from .schemas import (
    CustomerCreate,
    CustomerRead,
    DashboardSummary,
    ErrorEnvelope,
    OrderCreate,
    OrderRead,
    ProductCreate,
    ProductList,
    ProductPatch,
    ProductRead,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("northstar-commerce")
BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"


def db_path() -> Path:
    return database_path()


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed = os.getenv("APP_SEED_DEMO", "1").lower() not in {"0", "false", "no"}
    init_db(db_path(), seed=seed)
    yield


app = FastAPI(
    title="Northstar Commerce API",
    version="1.0.0",
    openapi_version="3.1.0",
    description="A classroom e-commerce and CRM service: browser to FastAPI to SQLite.",
    contact={"name": "Tertiary Infotech Academy", "url": "https://www.tertiaryinfotech.com/"},
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("APP_ALLOWED_ORIGINS", "http://127.0.0.1:8000").split(",")],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
)


def require_api_key(x_api_key: str = Header(default="")) -> None:
    configured = os.getenv("APP_API_KEY", "course-demo-key")
    if not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.middleware("http")
async def request_trace(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    log.info(
        "request_id=%s method=%s path=%s status=%s elapsed_ms=%.1f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(HTTPException)
async def public_http_error(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unavailable")
    code = {401: "unauthorized", 404: "not_found", 409: "conflict"}.get(exc.status_code, "request_error")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail), "request_id": request_id}},
    )


@app.get("/health/live", tags=["health"], summary="Check service liveness")
def live():
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"], summary="Check SQLite readiness")
def ready(path: Path = Depends(db_path)):
    try:
        with sqlite3.connect(path) as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "ready"}
    except sqlite3.Error as exc:
        raise HTTPException(503, "Database unavailable") from exc


@app.get("/api/v1/dashboard", response_model=DashboardSummary, tags=["dashboard"], summary="Read commerce KPIs")
def summary(path: Path = Depends(db_path)):
    return repository.dashboard_summary(path)


@app.get("/api/v1/products", response_model=ProductList, tags=["products"], summary="List products")
def list_products(
    status_filter: str | None = Query(default=None, alias="status", pattern="^(active|inactive|discontinued)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    path: Path = Depends(db_path),
):
    items, total = repository.list_products(path, status_filter, limit, offset)
    return {"items": items, "total": total}


@app.post(
    "/api/v1/products",
    response_model=ProductRead,
    status_code=201,
    tags=["products"],
    summary="Create a product",
    dependencies=[Depends(require_api_key)],
    responses={409: {"model": ErrorEnvelope, "description": "Duplicate SKU"}},
)
def create_product(payload: ProductCreate, path: Path = Depends(db_path)):
    try:
        return repository.create_product(path, payload.model_dump())
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "A product with this SKU already exists") from exc


@app.get("/api/v1/products/{product_id}", response_model=ProductRead, tags=["products"], summary="Get one product")
def get_product(product_id: int, path: Path = Depends(db_path)):
    product = repository.get_product(path, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@app.patch(
    "/api/v1/products/{product_id}",
    response_model=ProductRead,
    tags=["products"],
    summary="Partially update a product",
    dependencies=[Depends(require_api_key)],
)
def patch_product(product_id: int, payload: ProductPatch, path: Path = Depends(db_path)):
    product = repository.update_product(path, product_id, payload.model_dump(exclude_unset=True))
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@app.delete(
    "/api/v1/products/{product_id}",
    status_code=204,
    tags=["products"],
    summary="Delete a product",
    dependencies=[Depends(require_api_key)],
)
def delete_product(product_id: int, path: Path = Depends(db_path)):
    try:
        if not repository.delete_product(path, product_id):
            raise HTTPException(404, "Product not found")
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "A product used by an order cannot be deleted") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/v1/customers", response_model=list[CustomerRead], tags=["customers"], summary="List CRM customers")
def list_customers(path: Path = Depends(db_path)):
    return repository.list_customers(path)


@app.post(
    "/api/v1/customers",
    response_model=CustomerRead,
    status_code=201,
    tags=["customers"],
    summary="Create a CRM customer",
    dependencies=[Depends(require_api_key)],
)
def create_customer(payload: CustomerCreate, path: Path = Depends(db_path)):
    try:
        return repository.create_customer(path, payload.model_dump())
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "A customer with this email already exists") from exc


@app.get("/api/v1/orders", response_model=list[OrderRead], tags=["orders"], summary="List orders")
def list_orders(path: Path = Depends(db_path)):
    return repository.list_orders(path)


@app.post(
    "/api/v1/orders",
    response_model=OrderRead,
    status_code=201,
    tags=["orders"],
    summary="Create an order and decrement stock atomically",
    dependencies=[Depends(require_api_key)],
    responses={409: {"model": ErrorEnvelope, "description": "Insufficient stock"}},
)
def create_order(payload: OrderCreate, path: Path = Depends(db_path)):
    try:
        return repository.create_order(path, payload.model_dump())
    except repository.CommerceNotFound as exc:
        raise HTTPException(404, str(exc)) from exc
    except repository.CommerceConflict as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
