from pydantic import BaseModel, validator
from typing import Optional, List, Union
from datetime import datetime, date

class ProductImageBase(BaseModel):
    image_url: str
    is_primary: bool = False

class ProductImageCreate(ProductImageBase):
    pass

class ProductImage(ProductImageBase):
    id: str
    product_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    description: str
    price: float
    barcode: Optional[str] = None
    section: str
    stock: int = 0
    expiration_date: Optional[date] = None
    is_active: bool = True

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('stock')
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stock cannot be negative')
        return v

class ProductCreate(ProductBase):
    images: Optional[List[ProductImageCreate]] = []

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = None
    barcode: Optional[str] = None
    section: Optional[str] = None
    stock: Optional[int] = None
    expiration_date: Optional[Union[date, None]] = None
    is_active: Optional[bool] = None
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('stock')
    def stock_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Stock cannot be negative')
        return v

    class Config:
        orm_mode = True

class ProductInDBBase(ProductBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    images: List[ProductImage] = []

    class Config:
        orm_mode = True

class Product(ProductInDBBase):
    pass