from pydantic import BaseModel

class CalculationBase(BaseModel):
    name: str
    a: float
    b: float
    result: float

class CalculationCreate(CalculationBase):
    pass

class Calculation(CalculationBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    calculations: list[Calculation] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
