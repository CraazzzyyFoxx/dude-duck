import os

import sentry_sdk
import uvicorn
from beanie import init_beanie

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app.middlewares import TimeMiddleware
from app.bot import bot, dp
from app.bot.handlers import router as tg_router
from app.common.logging import logger
from app.common.webhook import setup_application, SimpleRequestHandler
from app.services.google import GoogleSheetsServiceManager
from app.schemas import get_beanie_models, Order, RenderConfig
from app.routes import router
from app import config

app = FastAPI()
app.include_router(router)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
                   allow_headers=["*"]
                   )
app.add_middleware(TimeMiddleware)
app.add_middleware(ServerErrorMiddleware, debug=config.app.debug)

client = AsyncIOMotorClient("mongodb://root:root@localhost:27017/?authMechanism=DEFAULT", )
srh = SimpleRequestHandler(dp, bot, handle_in_background=False, _bot=bot)
srh.register(app, "/api/telegram/webhook")
setup_application(app, dp, _bot=bot, bot=bot)

if not config.app.debug:
    sentry_sdk.init(
        dsn=config.app.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(content={"error": exc.detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def http_exception_handler(_: Request, exc: Exception):
    logger.error(exc)


@app.on_event("startup")
async def startup_event():
    await init_beanie(database=client.db_name, document_models=get_beanie_models())
    await GoogleSheetsServiceManager.init()
    # orders = await GoogleSheetsServiceManager.get().get_orders("Copy of B2B order", 0)
    # for order in orders:
    #     await order.create()
    configs = await RenderConfig.find().to_list()
    if not configs:
        from app.common.constants import OrderRenderBase, OrderRenderEtaPrice, OrderRenderResp, OrderRenderAdminResp
        await RenderConfig.model_validate(OrderRenderBase).create()
        await RenderConfig.model_validate(OrderRenderEtaPrice).create()
        await RenderConfig.model_validate(OrderRenderResp).create()
        await RenderConfig.model_validate(OrderRenderAdminResp).create()

    dp.include_router(tg_router)
    # webhook_info = await bot.get_webhook_info()
    # if webhook_info != f"{config.app.webhook_url}/api/telegram/webhook":
    await bot.set_webhook(url=f"{config.app.bot_webhook_url}/api/telegram/webhook",
                          secret_token=config.app.bot_api_token,
                          drop_pending_updates=True)

    logger.info("Bot API... Online !")


@app.on_event("shutdown")
async def shutdown_event():
    await bot.session.close()
    pass


if __name__ == '__main__':
    if os.name != "nt":
        import uvloop
        uvloop.install()

    uvicorn.run(
        "starter:app",
        host=config.app.host,
        port=config.app.port,
    )
