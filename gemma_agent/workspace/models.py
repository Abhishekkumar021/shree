from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class MenuItem(BaseModel):
    id: str
    name: str
    price: float
    description: Optional[str] = None

class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int
    price_at_order: float

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    items: List[OrderItem]

class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class OrderUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None

class TrackingResponse(BaseModel):
    order_id: str
    status: OrderStatus
    last_updated: datetime
    tracking_info: Optional[str] = None
