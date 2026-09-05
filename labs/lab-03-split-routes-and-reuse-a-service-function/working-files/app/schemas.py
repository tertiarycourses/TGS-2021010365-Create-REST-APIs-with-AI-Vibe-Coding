from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

ProductStatus = Literal["active", "inactive", "discontinued"]
OrderStatus = Literal["pending", "paid", "fulfilled", "cancelled"]


class ProductCreate(BaseModel):
    sku: str = Field(min_length=3, max_length=24, pattern=r"^[A-Z0-9-]+$")
    name: str = Field(min_length=3, max_length=120)
    description: str = Field(default="", max_length=500)
    price: Decimal = Field(ge=0, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0, le=100_000)
    status: ProductStatus = "active"


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0, le=100_000)
    status: ProductStatus | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    description: str
    price: Decimal
    stock_quantity: int
    status: ProductStatus
    created_at: datetime


class ProductList(BaseModel):
    items: list[ProductRead]
    total: int


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    company: str = Field(default="", max_length=120)


class CustomerRead(CustomerCreate):
    id: int
    created_at: datetime


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderItemCreate] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def unique_products(self):
        ids = [item.product_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Each product may appear only once per order")
        return self


class OrderItemRead(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderRead(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    status: OrderStatus
    total: Decimal
    created_at: datetime
    items: list[OrderItemRead]


class DashboardSummary(BaseModel):
    products: int
    customers: int
    orders: int
    revenue: Decimal
    low_stock: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
