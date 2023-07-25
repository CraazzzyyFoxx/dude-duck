import sentry_sdk
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app.middlewares import TimeMiddleware
from app.bot import bot, dp
from app.bot.handlers import router as tg_router
from app.crud import OrderRenderCRUD
from app.schemas import RenderConfig
from app.common.logger import logger
from app.common.webhook import setup_application, SimpleRequestHandler
from app.services.google import GoogleSheetsServiceManager
from app.routes import router

import config

app = FastAPI()
app.include_router(router)

app.add_middleware(TimeMiddleware)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
                   allow_headers=["*"]
                   )
app.add_middleware(ServerErrorMiddleware, debug=config.app.debug)

srh = SimpleRequestHandler(dp, bot, handle_in_background=False, _bot=bot)
srh.register(app, "/api/telegram/webhook")
setup_application(app, dp, _bot=bot, bot=bot)

if not config.app.debug:
    sentry_sdk.init(
        dsn=config.app.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0
    )

register_tortoise(
    app,
    config=config.tortoise,
    add_exception_handlers=True,
    generate_schemas=True
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(content={"error": exc.detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def http_exception_handler(_: Request, exc: Exception):
    logger.error(exc)


@app.on_event("startup")
async def startup_event():
    await GoogleSheetsServiceManager.init()
    configs = await OrderRenderCRUD.get_multi()
    if not configs:
        from app.common.constants import OrderRenderBase, OrderRenderEtaPrice, OrderRenderResp, OrderRenderAdminResp
        await OrderRenderCRUD.create(obj_in=RenderConfig.model_validate(OrderRenderBase))
        await OrderRenderCRUD.create(obj_in=RenderConfig.model_validate(OrderRenderEtaPrice))
        await OrderRenderCRUD.create(obj_in=RenderConfig.model_validate(OrderRenderResp))
        await OrderRenderCRUD.create(obj_in=RenderConfig.model_validate(OrderRenderAdminResp))

    dp.include_router(tg_router)
    # webhook_info = await bot.get_webhook_info()
    # if webhook_info != f"{config.app.webhook_url}/api/telegram/webhook":
    await bot.set_webhook(url=f"{config.app.webhook_url}/api/telegram/webhook",
                          secret_token=config.app.api_token_bot,
                          drop_pending_updates=True)

    logger.info("Bot API... Online !")


@app.on_event("shutdown")
async def shutdown_event():
    await bot.session.close()
    pass


if __name__ == '__main__':
    uvicorn.run(
        "starter:app",
        host=config.app.host,
        port=config.app.port,
    )
