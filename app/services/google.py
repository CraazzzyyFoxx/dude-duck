import typing
import datetime

import gspread_asyncio

from google.oauth2.service_account import Credentials
from gspread.utils import ValueRenderOption, DateTimeOption
from loguru import logger
from pydantic import create_model, SecretStr, AnyHttpUrl, EmailStr, field_validator

import config

from app.schemas import OrderSheetUpdate, Order, OrderMeta, OrderBase
from app.crud import OrderSheetsCRUD, OrderCRUD
from app.services.time import TimeService, ConversionMode

__all__ = ("GoogleSheetsService",)


def enum_parse(field, extra):
    def decorator(v: str, config):
        if v not in extra:
            raise ValueError(f"The {field} must be [{' | '.join(extra)}]")
        return v

    return decorator


def parse_datetime(v: str, config) -> typing.Any:
    return TimeService.convert_time(v, conversion_mode=ConversionMode.ABSOLUTE)


def parse_timedelta(v: str, config) -> typing.Any:
    now = datetime.datetime.utcnow()
    time = TimeService.convert_time(v, now=now, conversion_mode=ConversionMode.RELATIVE)
    return time - now


def get_creds():
    creds = Credentials.from_service_account_file(config.GOOGLE_CONFIG_FILE)
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


class GoogleSheetsService:
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

    @classmethod
    def n2a(cls, n: int):
        d, m = divmod(n, 26)  # 26 is the number of ASCII letters
        return '' if n < 0 else cls.n2a(d - 1) + chr(m + 65)  # chr(65) = 'A'

    @classmethod
    def get_type(cls, type_name: str):
        if type_name == 'int':
            return int
        elif type_name == 'str':
            return str
        elif type_name == 'float':
            return float
        elif type_name == 'dict':
            return dict
        elif type_name == 'timedelta':
            return datetime.timedelta
        elif type_name == 'datetime':
            return datetime.datetime
        elif type_name == 'SecretStr':
            return SecretStr
        elif type_name == 'EmailStr':
            return EmailStr
        elif type_name == 'AnyHttpUrl':
            return AnyHttpUrl
        elif type_name.startswith('list'):
            name = type_name.replace("list[", "")
            name = name.replace("]", "")
            return list[cls.get_type(name)]
        elif '|' in type_name:
            names = type_name.split('|')
            return typing.Union[cls.get_type(names[0].strip()), cls.get_type(names[1].strip())]

    @classmethod
    async def parse_row(cls, spreadsheet: str, sheet_id: int, row: list[typing.Any]) -> Order:
        model = await OrderSheetsCRUD.get_by_spreadsheet(spreadsheet, sheet_id)

        if not model:
            raise ValueError(f"No data for parser [spreadsheet={spreadsheet} sheet_id={sheet_id}]")

        model_fields = []
        meta_model_fields = []
        _fields = {}
        _validators = {}
        data_for_valid = {}
        data = dict(info={})

        for field in Order.model_fields.items():
            model_fields.append(field[0])

        for field in OrderMeta.model_fields.items():
            meta_model_fields.append(field[0])

        for getter in model.extra.items:
            field_type = cls.get_type(getter.type)
            field_data = row[getter.row]
            if getter.name not in meta_model_fields:
                _fields[getter.name] = (field_type, None if getter.null else ...)

            # if getter.type == "str":
            #     if isinstance(field_data, int):
            #         field_data = str(field_data)

            data_for_valid[getter.name] = field_data

            if getter.valid_values:
                _validators[f"{getter.name}_parse"] = (field_validator(getter.name, mode="before")
                                                       (enum_parse(getter.name, getter.valid_values)))
            if getter.type == "datetime":
                _validators[f"{getter.name}_parse"] = field_validator(getter.name, mode="before")(parse_datetime)
            if getter.type == "timedelta":
                _validators[f"{getter.name}_parse"] = field_validator(getter.name, mode="before")(parse_timedelta)

        Check = create_model("Check", **_fields, __base__=OrderBase, __validators__=_validators)  # type: ignore
        _ = Check.model_validate(data_for_valid, strict=False)

        for getter in model.extra.items:
            if getter.name in model_fields:
                data[getter.name] = row[getter.row]
            else:
                data["info"][getter.name] = row[getter.row]

        return Order(**data)

    @classmethod
    async def order_to_row(cls, spreadsheet: str, sheet_id: int, data: OrderSheetUpdate) -> dict[int, typing.Any]:
        model = await OrderSheetsCRUD.get_by_spreadsheet(spreadsheet, sheet_id)

        if not model:
            raise ValueError(f"No data for parser [spreadsheet={spreadsheet} sheet_id={sheet_id}]")

        order = await OrderCRUD.get_by_game(data.order_id, data.game)
        if not order:
            raise ValueError(f"Order not found [order_id={data.order_id} game={data.game}]")

        to_dict = data.model_dump()
        row = {}
        model_fields = []

        for field in OrderMeta.model_fields.items():
            model_fields.append(field[0])

        for getter in model.extra.items:
            if getter.name not in model_fields and to_dict[getter.name] is not None:
                row[getter.row] = to_dict[getter.name]

        return row

    @classmethod
    async def get_order(cls, spreadsheet: str, sheet_id: int, order_id: int) -> Order:
        agc = await cls.agcm.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)

        row = await sheet.row_values(order_id, value_render_option=ValueRenderOption.unformatted,
                                     date_time_render_option=DateTimeOption.formatted_string)
        return await cls.parse_row(spreadsheet, sheet_id, row)

    @classmethod
    async def get_all_orders(cls, spreadsheet: str, sheet_id: int) -> list[Order]:
        agc = await cls.agcm.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)

        rows = await sheet.get_values(value_render_option=ValueRenderOption.unformatted,
                                      date_time_render_option=DateTimeOption.formatted_string)
        return [await cls.parse_row(spreadsheet, sheet_id, row) for row in rows]

    @classmethod
    async def update_order(cls, spreadsheet: str, sheet_id: int, order: OrderSheetUpdate) -> Order:
        agc = await cls.agcm.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)
        row = await cls.order_to_row(spreadsheet, sheet_id, order)

        await sheet.batch_update([
            {
                "range": f"{cls.n2a(col)}{order.order_id}",
                "values": [[value]]
            }
            for col, value in row.items()])

        return await cls.get_order(spreadsheet, sheet_id, order.order_id)
