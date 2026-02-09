from datetime import datetime
from typing import Annotated
from pydantic import (
    UUID4, 
    AfterValidator, 
    BaseModel, 
    ConfigDict, 
    Field,
    validate_call
)


@validate_call
def validate_username(username: str) -> str:
    if not username.isalnum():
        raise ValueError("Username must be alphanumeric")
    return username


@validate_call
def validate_password(password: str) -> str:
    validations = [
        (
            lambda p: any(char.isdigit() for char in p),
            "Password must contain at least one digit"
        ),
        (
            lambda p: any(char.isupper() for char in p),
            "Password must contain at least one uppercase letter"
        ),
        (
            lambda p: any(char.islower() for char in p),
            "Password must contain at least one lowercase letter"
        )
    ]
    for condition, error_msg in validations:
        if not condition(password):
            raise ValueError(error_msg)
    
    return password

ValidUsername = Annotated[
    str, Field(min_length=3, max_length=20), AfterValidator(validate_username)
]

ValidPassword = Annotated[
    str, Field(min_length=8, max_digits=64), AfterValidator(validate_password)
]



class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: ValidUsername
    is_active: bool = True
    role: str = "USER"

class UserCreate(UserBase):
    password: ValidPassword

class UserInDB(UserBase):
    hashed_password: str


class UserOut(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
