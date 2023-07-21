import html
import json
import logging
import traceback
from typing import Optional, cast

import sentry_sdk

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

import config

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, cast(Exception, context.error).__traceback__
    )
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    sentry_sdk.capture_exception(error=context.error)
    sentry_sdk.capture_message(json.dumps(update_str, indent=2, ensure_ascii=False))
    logger.error(context.error)
