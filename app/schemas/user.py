from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole, UserStatus


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    phone: str | None = None
    role: UserRole
    status: UserStatus
    is_donor: bool
    join_date: date


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
