from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    image: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    image_id: Optional[str] = None
    category_id: int


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    category: Optional[Category] = None
    
    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    item_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    item: Optional[Item] = None
    
    class Config:
        from_attributes = True


class PaymentData(BaseModel):
    card_number: str
    card_holder_name: str
    expiry_month: int = Field(ge=1, le=12)
    expiry_year: int
    cvv: str
    billing_address: Optional[Dict[str, Any]] = None


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    total: float = Field(gt=0, description="Total must be greater than 0")
    payment: PaymentData


class Order(BaseModel):
    id: int
    timestamp: datetime
    total: float
    payment_key: str
    order_items: List[OrderItem] = []
    
    class Config:
        from_attributes = True


class MenuResponse(BaseModel):
    categories: List[Category]
    items: List[Item]
