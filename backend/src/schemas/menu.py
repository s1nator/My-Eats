from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MenuItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=100)
    is_available: bool = True
    image_url: HttpUrl | None = None


class MenuItemUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    category: str | None = Field(default=None, min_length=1, max_length=100)
    is_available: bool | None = None
    image_url: HttpUrl | None = None


class MenuItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    price: Decimal
    category: str
    is_available: bool
    image_url: HttpUrl | None
