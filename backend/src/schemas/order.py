from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    menu_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    customer_name: str = Field(min_length=1, max_length=255)
    customer_phone: str = Field(min_length=1, max_length=50)
    delivery_address: str = Field(min_length=1, max_length=500)
    items: list[OrderItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def menu_items_must_be_unique(self) -> "OrderCreate":
        menu_item_ids = [item.menu_item_id for item in self.items]
        if len(menu_item_ids) != len(set(menu_item_ids)):
            raise ValueError("Each menu item can be included only once")
        return self


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    quantity: int
    price_at_order: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    items: list[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus
