from pydantic import BaseModel


__all__ = ("User", "UserID")


class User(BaseModel):
    user_id: int
    activated: bool
    respond_mode: bool


class UserID(User):
    id: int