import datetime
import typing

from enum import IntEnum

from pydantic import BaseModel, ConfigDict, AnyHttpUrl, field_validator, Field

from app.schemas.order import OrderMeta


__all__ = ("OrderStatusEnum",
           "OrderStatusPaid",
           "OrderTypeEnum",
           "OrderSheetUpdate",
           "OrderSheetParseItem",
           "OrderSheetParse",
           "OrderSheetParseItemList",
           "OrderSheetParseID",
           "OrderSheetParseBase",
           "OrderSheetParseCreate",
           "OrderSheetParseUpdate")


class OrderStatusEnum(IntEnum):
    InProgress = 0
    Completed = 1
    Refund = 2


class OrderStatusPaid(IntEnum):
    Paid = 1
    NotPaid = 0


class OrderTypeEnum(IntEnum):
    Pilot = 0
    Self = 1


class OrderSheetUpdate(OrderMeta):
    order_id: int

    date: datetime.datetime | None = None
    exchange: float | None = None
    shop: str | None = None
    shop_order_id: str | None = None
    boost_type: str | None = None
    region_fraction: str | None = None
    server: str | None = None
    character_class: str | None = None
    nickname: str | None = None
    armory: str | None = None
    game: str
    tg_channels: list[int] | None = None
    category: str | None = None
    purchase: str | None = None
    comment: str | None = None
    battle_tag: str | None = None
    login: str | None = None
    password: str | None = None
    vpn: str | None = None
    contact: str | None = None
    script_payload: str | None = None
    script_share: str | None = None
    script_request: str | None = None
    booster: str | None = None
    auth_date: str | None = None
    status: str | None = None
    screenshot: AnyHttpUrl | None = None
    end_date: datetime.datetime | None = None
    price_dollar: float | None = None
    eta: str | None = None
    price_booster_rub: float | None = None
    price_booster_dollar: float | None = None
    price_booster_dollar_fee: float | None = None
    costs_rub: float | None = None
    costs_dollar: float | None = None
    profit: float | None = None
    percent: float | None = None
    status_paid: str | None = None


class OrderSheetParseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    row: int
    null: bool

    valid_values: list[typing.Any] = Field(examples=[["Completed", "InProgress", "Refund"]])
    type: str = Field(examples=["int", "str", "timedelta", "datetime", "SecretStr", "EmailStr", "AnyHttpUrl", "float"])

    # @field_validator("type")
    # def validate_type(cls, v: str):
    #     if v not in ["int", "str", "timedelta", "datetime", "SecretStr", "EmailStr", "AnyHttpUrl", "float"]:
    #         raise ValueError(f"Type can be [int | str | timedelta | datetime | SecretStr | EmailStr | float]")
    #     return v


class OrderSheetParseItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[OrderSheetParseItem]


class OrderSheetParseBase(BaseModel):
    spreadsheet: str | None
    sheet_id: int | None
    extra: OrderSheetParseItemList


class OrderSheetParse(OrderSheetParseBase):
    spreadsheet: str
    sheet_id: int
    extra: OrderSheetParseItemList


class OrderSheetParseUpdate(OrderSheetParseBase):
    pass


class OrderSheetParseID(OrderSheetParse):
    model_config = ConfigDict(from_attributes=True)

    id: int


class OrderSheetParseCreate(OrderSheetParse):
    pass
