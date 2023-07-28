from pydantic import ValidationError

from app.common.logging import logger
from app.schemas import OrderRespond, RenderConfig, Order

__all__ = (
    "format_err",
    "format_pydantic_err",
    "render_order"
)


def format_err(msg: str):
    return f"<b>Error:</b> {msg}"


def render_order(order: Order, configs: list[RenderConfig], *, respond: OrderRespond = None):
    out: list[str] = []

    data = {"order": order.model_dump()}
    if respond:
        data["response"] = respond.model_dump()
    for i, config in enumerate(configs, 1):
        config_d = []
        for index, cf in enumerate(config.fields, 0):
            attrs = []
            for fof in cf.fields:
                d = data.copy()
                for st in fof.storage:
                    d = d[st]
                attr = d.get(fof.attr)
                if attr is not None:
                    if fof.format:
                        attr = f"{attr:{fof.format}}"
                    if fof.before_value:
                        attr = f"{fof.before_value}{attr}"
                    if fof.after_value:
                        attr = f"{attr}{fof.after_value}"
                    if not isinstance(attr, str):
                        attr = str(attr)
                    attrs.append(attr)

            if attrs:
                name = cf.name
                value = cf.separator.join(attrs)

                if cf.markdown_name:
                    name = f"{cf.markdown_name}{name}</{cf.markdown_name[1:]}"
                if cf.markdown_value:
                    value = f"{cf.markdown_value}{value}</{cf.markdown_value[1:]}"

                if len(config_d) != 0:
                    rendered = f"{config.separator_field}{name}: {value}"
                else:
                    rendered = f"{name}: {value}"
                config_d.append(rendered)

        out.append("".join(config_d))

        if i < len(configs) and config_d:
            out.append(config.separator)

    return "".join(out)


def format_pydantic_err(err: ValidationError):
    msg = []
    for e in err.errors(include_url=False, include_context=False):
        msg.append(f'{", ".join([loc for loc in e["loc"]])}: {e["msg"]}')

    return '\n'.join(msg)
