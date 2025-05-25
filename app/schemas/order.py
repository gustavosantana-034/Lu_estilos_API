from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.order import OrderStatus  # your enum defined in the ORM model

# Base schema for order items with automatic calculation of total price
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

# Schema for creating order items
class OrderItemCreate(OrderItemBase):
    pass

# Schema representing an order item stored in the database
class OrderItem(OrderItemBase):
    id: str
    order_id: str
    created_at: datetime

    class Config:
        orm_mode = True  # allows using ORM objects directly

# Base schema for orders with main fields
class OrderBase(BaseModel):
    client_id: str
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None
    total_amount: Optional[float] = None

# Schema for creating an order with its items
class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    @validator('total_amount', always=True)
    def calculate_total_amount(cls, v, values):
        if 'items' in values:
            return sum(item.total_price for item in values['items'])
        return v or 0

# Schema for partial update of the order
class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for returning the order with its items, using ORM mode for serialization
class OrderInDBBase(OrderBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    items: List[OrderItem] = []  # list of order items

    class Config:
        orm_mode = True

# Final schema to be used in responses
class Order(OrderInDBBase):
    pass
