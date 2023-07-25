import json
import typing
import datetime

from loguru import logger
from fastapi.encoders import jsonable_encoder
from gspread_asyncio import AsyncioGspreadClientManager
from google.oauth2.service_account import Credentials
from gspread.utils import ValueRenderOption, DateTimeOption
from pydantic import create_model, SecretStr, EmailStr, field_validator, BaseModel, HttpUrl
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.schemas import OrderSheetUpdate, Order, Booster, AdminID
from app.crud import OrderSheetsCRUD, AdminCRUD
from app.services.time import TimeService, ConversionMode

import config

__all__ = ("GoogleSheetsService", "GoogleSheetsServiceManager")

BM = typing.TypeVar("BM", bound=BaseModel)
type_map = {"int": int,
            'str': str,
            'float': float,
            'timedelta': datetime.timedelta,
            'datetime': datetime.datetime,
            'SecretStr': SecretStr,
            'EmailStr': EmailStr,
            'HttpUrl': HttpUrl,
            'PhoneNumber': PhoneNumber,
            'PaymentCardNumber': PaymentCardNumber}


def enum_parse(field, extra):
    def decorator(v: str, ):
        if v not in extra:
            raise ValueError(f"The {field} must be [{' | '.join(extra)}]")
        return v

    return decorator


def parse_datetime(v: str) -> typing.Any:
    return TimeService.convert_time(v, conversion_mode=ConversionMode.ABSOLUTE)


def parse_timedelta(v: str) -> typing.Any:
    now = datetime.datetime.utcnow()
    time = TimeService.convert_time(v, now=now, conversion_mode=ConversionMode.RELATIVE)
    return time - now


class GoogleSheetsServiceManagerMeta:
    def __init__(self):
        self.managers: dict[int, GoogleSheetsService] = {}
        with open(config.GOOGLE_CONFIG_FILE) as file:
            self.creds = json.loads(file.read())

    async def init(self):
        self.managers[0] = GoogleSheetsService(AsyncioGspreadClientManager(self.get_creds()))

        admins = await AdminCRUD.get_multi()
        for admin in admins:
            admin = AdminID.model_validate(admin, from_attributes=True)
            self.managers[admin.google.client_id] = GoogleSheetsService(AsyncioGspreadClientManager
                                                                        (self.get_creds(admin=admin)))
        logger.info("GoogleSheetsServiceManager... Ready!")

    async def admin_create(self, admin: AdminID):
        admin = AdminID.model_validate(admin, from_attributes=True)
        self.managers[admin.google.client_id] = GoogleSheetsService(
            AsyncioGspreadClientManager(self.get_creds(admin=admin)))

    async def admin_delete(self, admin: AdminID):
        del self.managers[admin.google.client_id]

    async def admin_update(self, admin: AdminID):
        admin = AdminID.model_validate(admin, from_attributes=True)
        self.managers[admin.google.client_id] = GoogleSheetsService(
            AsyncioGspreadClientManager(self.get_creds(admin=admin)))

    def get_creds(self, *, admin: AdminID = None):
        def wrapped():
            if admin:
                data = admin.google.model_dump()
            else:
                data = self.creds
            creds = Credentials.from_service_account_info(data)
            scoped = creds.with_scopes([
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ])
            return scoped

        return wrapped

    def get(self, *, admin: AdminID = None):
        if admin:
            return self.managers[admin.google.client_id]
        else:
            return self.managers[0]


class GoogleSheetsService:

    def __init__(self, manager: AsyncioGspreadClientManager):
        self.manager = manager

    def n2a(self, n: int):
        d, m = divmod(n, 26)  # 26 is the number of ASCII letters
        return '' if n < 0 else self.n2a(d - 1) + chr(m + 65)  # chr(65) = 'A'

    def get_type(self, type_name: str, null: bool):
        if '|' in type_name:
            names = type_name.split('|')
            return self.get_type(names[0].strip(), False) | self.get_type(names[1].strip(), null)

        if null:
            return type_map[type_name] | None
        return type_map[type_name]

    @staticmethod
    async def get_parser(spreadsheet: str, sheet_id: int):
        if parser := await OrderSheetsCRUD.get_by_spreadsheet(spreadsheet, sheet_id):
            return parser
        raise ValueError(f"No data for parser [spreadsheet={spreadsheet} sheet_id={sheet_id}]")

    async def parse_row(
            self,
            model: typing.Type[BaseModel],
            spreadsheet: str,
            sheet_id: int,
            row: list[typing.Any],
            apply_model: bool
    ) -> BM:
        parser = await self.get_parser(spreadsheet, sheet_id)
        for i in range(len(parser.extra.items) - len(row)):
            row.append(None)

        _fields = {}
        _validators = {}
        data_for_valid = {}
        for getter in parser.extra.items:
            value = row[getter.row]
            if value in ["", " "]:
                value = None
            data_for_valid[getter.name] = value
            _fields[getter.name] = (self.get_type(getter.type, getter.null), None if getter.null else ...)
            if value:
                if getter.valid_values:
                    _validators[f"{getter.name}_parse"] = (field_validator(getter.name, mode="before")
                                                           (enum_parse(getter.name, getter.valid_values)))
                if getter.type == "datetime":
                    _validators[f"{getter.name}_parse"] = (field_validator(getter.name, mode="before")
                                                           (parse_datetime))
                if getter.type == "timedelta":
                    _validators[f"{getter.name}_parse"] = (field_validator(getter.name, mode="before")
                                                           (parse_timedelta))

        check_model = create_model("check_model", **_fields, __validators__=_validators)  # type: ignore
        valid_model = check_model.model_validate(data_for_valid, strict=False)
        if apply_model:
            validated_data = valid_model.model_dump()
            model_fields = [field[0] for field in model.model_fields.items()]
            data = dict(info={})

            for getter in parser.extra.items:
                if getter.name in model_fields:
                    data[getter.name] = validated_data[getter.name]
                else:
                    data["info"][getter.name] = validated_data[getter.name]

            return model(**data)
        else:
            return valid_model

    async def data_to_row(
            self,
            spreadsheet: str,
            sheet_id: int,
            data: BaseModel
    ) -> dict[int, typing.Any]:
        parser = await self.get_parser(spreadsheet, sheet_id)
        to_dict: dict = jsonable_encoder(data)
        row = {}

        if info := to_dict.get("info"):
            for name, value in info.items():
                to_dict[name] = value

        for getter in parser.extra.items:
            if to_dict.get(getter.name) is not None and not getter.generated:
                row[getter.row] = to_dict[getter.name]
        return row

    async def get_row_data(
            self,
            model: typing.Type[BaseModel],
            spreadsheet: str,
            sheet_id: int,
            row_id: int,
            apply_model: bool
    ):
        agc = await self.manager.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)
        parser = await self.get_parser(spreadsheet, sheet_id)
        columns = max(p.row for p in parser.extra.items)
        start = min(p.row for p in parser.extra.items)

        row = await sheet.get(range_name=f"{self.n2a(start)}{row_id}:{self.n2a(columns)}{row_id}",
                              value_render_option=ValueRenderOption.unformatted,
                              date_time_render_option=DateTimeOption.formatted_string)
        return await self.parse_row(model, spreadsheet, sheet_id, row[0], apply_model)

    async def get_all_data(
            self,
            model: typing.Type[BaseModel],
            spreadsheet: str,
            sheet_id: int,
            apply_model: bool
    ):
        agc = await self.manager.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)
        values_list = await sheet.col_values(2, value_render_option=ValueRenderOption.unformatted)
        parser = await self.get_parser(spreadsheet, sheet_id)
        columns = max(p.row for p in parser.extra.items)
        start = min(p.row for p in parser.extra.items)
        index = 1

        for value in values_list:
            if not value:
                break
            index += 1

        rows = await sheet.get(range_name=f"{self.n2a(start)}1:{self.n2a(columns)}{index}",
                               value_render_option=ValueRenderOption.unformatted,
                               date_time_render_option=DateTimeOption.formatted_string)
        return [await self.parse_row(model, spreadsheet, sheet_id, row, apply_model) for row in rows]

    async def create_row_data(
            self,
            model: typing.Type[BaseModel],
            spreadsheet: str,
            sheet_id: int,
            data: BaseModel,
            apply_model: bool
    ) -> BM:
        agc = await self.manager.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)
        values_list = await sheet.col_values(2, value_render_option=ValueRenderOption.unformatted)
        index = 1

        for value in values_list:
            if not value:
                break
            index += 1

        return await self.update_row_data(model, spreadsheet, sheet_id, index, data, apply_model)

    async def update_row_data(
            self,
            model: typing.Type[BaseModel],
            spreadsheet: str,
            sheet_id: int,
            row_id: int,
            data: BaseModel,
            apply_model: bool
    ) -> BM:
        agc = await self.manager.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)
        row = await self.data_to_row(spreadsheet, sheet_id, data)
        await sheet.batch_update(
            [{"range": f"{self.n2a(col)}{row_id}", "values": [[value]]} for col, value in row.items()],
            response_value_render_option=ValueRenderOption.formatted,
            response_date_time_render_option=DateTimeOption.formatted_string
        )

        return await self.get_row_data(model, spreadsheet, sheet_id, row_id, apply_model)

    async def get_order(self, spreadsheet: str, sheet_id: int, row_id: int, *, apply_model=True) -> Order:
        return await self.get_row_data(Order, spreadsheet, sheet_id, row_id, apply_model=apply_model)

    async def get_orders(self, spreadsheet: str, sheet_id: int, *, apply_model=True) -> list[Order]:
        return await self.get_all_data(Order, spreadsheet, sheet_id, apply_model=apply_model)

    async def create_order(self, spreadsheet: str, sheet_id: int, data: Order, *, apply_model=True) -> Order:
        return await self.create_row_data(Order, spreadsheet, sheet_id, data, apply_model)

    async def update_order(
            self,
            spreadsheet: str,
            sheet_id: int,
            row_id: int,
            data: OrderSheetUpdate,
            *,
            apply_model=True
    ) -> Order:
        return await self.update_row_data(Order, spreadsheet, sheet_id, row_id, data, apply_model)

    async def get_booster(self, spreadsheet: str, sheet_id: int, row_id: int, *, apply_model=True) -> Booster:
        return await self.get_row_data(Booster, spreadsheet, sheet_id, row_id, apply_model=apply_model)

    async def get_booster_by_cell(
            self,
            spreadsheet: str,
            sheet_id: int,
            value: str,
            *,
            apply_model=True
    ) -> Booster | None:
        agc = await self.manager.authorize()
        sh = await agc.open(spreadsheet)
        sheet = await sh.get_worksheet_by_id(sheet_id)
        cell_list = await sheet.findall(value)
        if cell_list:
            return await self.get_row_data(Booster, spreadsheet, sheet_id, cell_list[0].row, apply_model=apply_model)

    async def get_boosters(self, spreadsheet: str, sheet_id: int, *, apply_model=True) -> list[Booster]:
        return await self.get_all_data(Booster, spreadsheet, sheet_id, apply_model=apply_model)

    async def update_booster(
            self,
            spreadsheet: str,
            sheet_id: int,
            row_id: int,
            data: OrderSheetUpdate,
            *,
            apply_model=True
    ) -> Booster:
        return await self.update_row_data(Booster, spreadsheet, sheet_id, row_id, data, apply_model)


GoogleSheetsServiceManager = GoogleSheetsServiceManagerMeta()
