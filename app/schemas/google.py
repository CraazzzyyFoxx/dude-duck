import datetime
import typing

from pydantic import BaseModel, ConfigDict, AnyHttpUrl, field_validator, Field

__all__ = (
    "OrderSheetUpdate",
    "OrderSheetParseItem",
    "OrderSheetParse",
    "OrderSheetParseItemList",
    "OrderSheetParseID",
    "OrderSheetParseBase",
    "OrderSheetParseCreate",
    "OrderSheetParseUpdate",
    "allowed_types"
)

allowed_types = ["int", "str", "timedelta", "datetime", "SecretStr", "EmailStr", "HttpUrl", "float", 'PhoneNumber',
                 'PaymentCardNumber']


class OrderSheetParseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    row: int
    null: bool = Field(default=False)
    generated: bool = Field(default=False)

    valid_values: list[typing.Any] = Field(examples=[["Completed", "InProgress", "Refund"]])
    type: str = Field(examples=allowed_types)

    @field_validator("type")
    def validate_type(cls, v: str):
        if '|' in v:
            vs = v.split("|")
        else:
            vs = [v]
        for x in vs:
            if x.strip() not in allowed_types:
                raise ValueError(f"Type can be [{' | '.join(allowed_types)}]")
        return v


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


class OrderSheetUpdate(BaseModel):
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
    game: str | None = None
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
    auth_date: datetime.datetime | None = None
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
