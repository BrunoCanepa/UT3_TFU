from pydantic import BaseModel
from datetime import datetime
from typing import TypeVar, Generic, List

# PRODUCT
class ProductBase(BaseModel):
    name: str
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True

# CUSTOMER
class CustomerBase(BaseModel):
    name: str
    email: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    class Config:
        from_attributes = True

# ORDER
class OrderBase(BaseModel):
    customer_id: int
    total: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    date: datetime
    class Config:
        from_attributes = True

# RESPONSE WITH PROCESSING TIME
T = TypeVar('T')

class ResponseWithTime(BaseModel, Generic[T]):
    data: T
    processing_time_ms: float

class ListResponseWithTime(BaseModel, Generic[T]):
    data: List[T]
    processing_time_ms: float
