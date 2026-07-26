from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


UserRole = Literal["operator", "admin_auditor"]


class UserRead(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    role: UserRole = "operator"
    is_active: bool = True

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        username = value.strip()
        if not username:
            raise ValueError("El usuario es obligatorio.")
        return username


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=8)
    role: UserRole | None = None
    is_active: bool | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        username = value.strip()
        if not username:
            raise ValueError("El usuario es obligatorio.")
        return username

    @model_validator(mode="after")
    def reject_null_control_fields(self):
        for field_name in ("username", "role", "is_active"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"El campo {field_name} no puede ser nulo.")
        return self


class UserPasswordUpdate(BaseModel):
    new_password: str = Field(min_length=8)
