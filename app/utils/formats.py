import datetime
from dataclasses import dataclass, field

from loguru import logger

from app.schemas import OrderRespond, OrderID, RenderConfigID



def format_error(msg: str):
    return f"<b>Error:</b> {msg}"


@dataclass(kw_only=True)
class OrderRender:
    d: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return "".join(self.d)

    def process_markdown(self, mk: str, value: str):
        return f"{mk}{value}</{mk[1:]}"

    def render(self, order: OrderID, configs: list[RenderConfigID], respond: OrderRespond = None):
        data = dict(order=order.model_dump())
        if respond:
            data["respond"] = respond.model_dump()
        for i, config in enumerate(configs, 1):
            for index, field in enumerate(config.fields.items, 1):
                attrs = []
                for field_field in field.fields:
                    d = data.copy()
                    for st in field_field.storage:
                        d = d[st]
                    attr = d.get(field_field.attr)
                    if attr:
                        if field_field.format:
                            attr = f"{attr:{field_field.format}}"
                        if field_field.before_value:
                            attr = f"{field_field.before_value}{attr}"
                        if field_field.after_value:
                            attr = f"{attr}{field_field.after_value}"
                        if not isinstance(attr, str):
                            attr = str(attr)
                        attrs.append(attr)

                if attrs:
                    name = field.name
                    value = field.separator.join(attrs)

                    if field.markdown_name:
                        name = self.process_markdown(field.markdown_name, name)
                    if field.markdown_value:
                        value = self.process_markdown(field.markdown_value, value)

                    rendered = f"{name}: {value}"
                    self.d.append(rendered)

                if index < len(config.fields.items):
                    self.d.append(config.separator_field)

            if i < len(configs):
                self.d.append(config.separator)
        return self

    def approved(self, state: bool, count: int):
        self.d.append(f"<b>Approved: </b><code>{'YES' if state else 'NO'}</code>")
        self.d.append(f"<b>Total responses: </b><code>{count}</code>")
        return self
