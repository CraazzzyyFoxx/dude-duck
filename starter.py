import time
import uvicorn
from aiogram import types, Router, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

# from app.crud import OrderRenderCRUD
# from app.schemas import RenderConfig
from app.utils.logging import logger
#  app.routes import router

import config


router = APIRouter(
    prefix='/telegram',
    tags=['telegram'],
    # dependencies=[Depends(AuthService.requires_authorization_telegram)]
)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram(update: dict):
    # await application.update_queue.put(
    #     Update.de_json(data=payload, bot=application.bot)
    # )
    # return Response()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


app = FastAPI()
app.include_router(router)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
#     allow_headers=["*"]
# )
# app.add_middleware(ServerErrorMiddleware, debug=config.app.DEBUG)

# # sentry_sdk.init(
# #     dsn=config.app.SENTRY_DSN,
# #     traces_sample_rate=1.0
# # )
#
register_tortoise(
    app,
    config=config.tortoise,
    add_exception_handlers=True,
    generate_schemas=True
)


storage = MemoryStorage()
bot = Bot(token=config.app.TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=storage)
start_router = Router()


@start_router.message(Command('start'))
async def start(message: types.Message) -> None:
    await message.answer(config.START_MESSAGE)
    logger.info(f"Started a conversation with a user {message.from_user.username} [ID: {message.from_user.id}]")


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     logger.info(f"{request.url} process time: {process_time}")
#     return response
#
#
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(content={"error": exc.detail}, status_code=exc.status_code)


@app.on_event("startup")
async def startup_event():
    # configs = await OrderRenderCRUD.get_multi()
    # if not configs:
    #     from app.utils.constants import OrderRenderBase, OrderRenderEtaPrice
    #     model_1 = RenderConfig.model_validate(OrderRenderBase)
    #     model_2 = RenderConfig.model_validate(OrderRenderEtaPrice)
    #     await OrderRenderCRUD.create(obj_in=model_1)
    #     await OrderRenderCRUD.create(obj_in=model_2)

    dp.include_router(start_router)

    webhook_info = await bot.get_webhook_info()
    if webhook_info != f"{config.app.WEBHOOK_URL}/telegram/webhook":
        await bot.set_webhook(url=f"{config.app.WEBHOOK_URL}/telegram/webhook")

    logger.info("Bot API... Online !")
    pass


@app.on_event("shutdown")
async def shutdown_event():
    await bot.session.close()
    pass


if __name__ == '__main__':
    uvicorn.run(
        "starter:app",
        host=config.app.HOST,
        port=config.app.PORT,
    )
