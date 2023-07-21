from __future__ import annotations

import typing
import urllib
from dataclasses import dataclass


@dataclass
class Callback:
    base: str

    path_template: typing.AbstractSet[str]
    """Template string for this endpoint."""

    path_regex: typing.Iterable[str]
    """Template regex for this endpoint."""

    def compile(
            self,
            **kwargs: typing.Any,
    ) -> str:
        url = self.base + "|".join(["{" + s + "}" for s in self.path_template])
        kwargs = {k: urllib.parse.quote(str(v)) for k, v in kwargs.items()}
        return url.format(**kwargs)

    def regex(
            self
    ) -> str:
        return rf"^{self.base}" + "|".join(self.path_regex) + "$"

    def parse(
            self,
            url: str
    ) -> typing.Any:
        data = []
        args = url[len(self.base):].split("|")
        for arg in args:
            if arg.isdigit():
                data.append(int(arg))

        if not data:
            return None

        if len(data) == 1:
            return data[0]

        return data


NUMBER_REGEX: typing.Final[str] = "(\d+)"

RESPOND_ORDER_CALLBACK = Callback("respond_order", {"order_id"}, [NUMBER_REGEX])
ORDER_CONFIRM_YES_CALLBACK = Callback("order_confirm_yes", {"order_id"}, [NUMBER_REGEX])
ORDER_CONFIRM_NO_CALLBACK = Callback("order_confirm_no", {"order_id"}, [NUMBER_REGEX])
ORDER_CONFIRM_YES_ARBITRARY_CALLBACK = Callback("order_confirm_arbitrary_yes", {"order_id"}, [NUMBER_REGEX])
ORDER_CONFIRM_NO_ARBITRARY_CALLBACK = Callback("order_confirm_arbitrary_no", {"order_id"}, [NUMBER_REGEX])
CONFIRM_ORDER_RESPONSE_CALLBACK = Callback("order_admin_confirm", {"order_id", "user_id"},
                                           [NUMBER_REGEX, NUMBER_REGEX])
