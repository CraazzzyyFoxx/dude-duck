from dataclasses import dataclass, field

from pydantic import ValidationError

from app.schemas import OrderRespond, OrderID, RenderConfigID, Order

__all__ = (
    "format_error",
    "OrderRender",
    "format_pydantic_error"
)


def format_error(msg: str):
    return f"<b>Error:</b> {msg}"


@dataclass(kw_only=True)
class OrderRender:
    d: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return "".join(self.d)

    @staticmethod
    def process_markdown(mk: str, value: str):
        return f"{mk}{value}</{mk[1:]}"

    def render(self, order: Order, configs: list[RenderConfigID], respond: OrderRespond = None):
        data = dict(order=order.model_dump())
        if respond:
            data["response"] = respond.model_dump()
        for i, config in enumerate(configs, 1):
            config_d = []
            for index, cf in enumerate(config.fields.items, 0):
                attrs = []
                for fof in cf.fields:
                    d = data.copy()
                    for st in fof.storage:
                        d = d[st]
                    attr = d.get(fof.attr)
                    if attr:
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
                        name = self.process_markdown(cf.markdown_name, name)
                    if cf.markdown_value:
                        value = self.process_markdown(cf.markdown_value, value)

                    if len(config_d) != 0:
                        rendered = f"{config.separator_field}{name}: {value}"
                    else:
                        rendered = f"{name}: {value}"
                    config_d.append(rendered)

            self.d.append("".join(config_d))

            if i < len(configs) and config_d:
                self.d.append(config.separator)

        return self


def format_pydantic_error(err: ValidationError):
    msg = []
    for e in err.errors(include_url=False, include_context=False):
        msg.append(f'{", ".join([loc for loc in e["loc"]])}: {e["msg"]}')

    return '\n'.join(msg)
