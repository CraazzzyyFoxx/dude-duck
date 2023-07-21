from pydantic import BaseModel, Field, field_validator, ConfigDict

__all__ = (
    "RenderConfig",
    "RenderFieldConfig",
    "RenderField",
    "RenderConfigID",
    "RenderConfigCreate",
    "RenderConfigUpdate",
    'RenderFieldConfigList'
)


class RenderField(BaseModel):
    attr: str = Field(strict=True)
    storage: list[str]
    format: str | None = Field(default=None, strict=True)
    before_value: str | None = Field(default=None, min_length=1, max_length=20, strict=True)
    after_value: str | None = Field(default=None, min_length=1, max_length=20, strict=True)


class RenderFieldConfig(BaseModel):
    name: str = Field(strict=True)
    fields: list[RenderField]
    markdown_name: str | None = Field(default=None, strict=True)
    markdown_value: str | None = Field(default=None, strict=True)
    separator: str = Field(default=' ', min_length=1, max_length=20, strict=True)

    @field_validator('markdown_name', 'markdown_value')
    def parse_markdown(cls, v: str):
        if v is None:
            return v
        if not v.startswith('<'):
            raise ValueError(f"Invalid markdown element Example: <code>")
        if not v.endswith('>'):
            raise ValueError(f"Invalid markdown element Example: <code>")
        if v[1:-1] not in ["b", "i", "code", "s", "u", "pre"]:
            raise ValueError(f"Type can be [b|i|code|s|u|pre]")
        return v


class RenderFieldConfigList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[RenderFieldConfig]


class RenderConfig(BaseModel):
    name: str = Field(strict=True, min_length=1, max_length=20)
    fields: RenderFieldConfigList
    separator: str = Field(default='\n', min_length=1, max_length=20, strict=True)
    separator_field: str = Field(default='\n', min_length=1, max_length=20, strict=True)


class RenderConfigCreate(RenderConfig):
    pass


class RenderConfigUpdate(RenderConfig):
    pass


class RenderConfigID(RenderConfig):
    model_config = ConfigDict(from_attributes=True)

    id: int
