from typing import Annotated

from pydantic import UrlConstraints
from pydantic_core import Url

__all__ = ("TelegramUserUrl", )

TelegramUserUrl = Annotated[Url, UrlConstraints(max_length=2083, allowed_schemes=['https'], host_required=True)]