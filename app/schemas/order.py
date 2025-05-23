from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.order import OrderStatus

class OrderItemBase(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    total_price: Optional[float] = None

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @validator('unit_price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('total_price', always=True)
    def calculate_total_price(cls, v, values):
        if 'quantity' in values and 'unit_price' in values:
            return values['quantity'] * values['unit_price']
        return v

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: str
    order_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    client_id: str
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None
    total_amount: Optional[float] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    @validator('total_amount', always=True)
    def calculate_total_amount(cls, v, values):
        if 'items' in values:
            return sum(item.total_price for item in values['items'])
        return v or 0

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True

class OrderInDBBase(OrderBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    items: List[OrderItem] = []

    class Config:
        orm_mode = True

class Order(OrderInDBBase):
    pass