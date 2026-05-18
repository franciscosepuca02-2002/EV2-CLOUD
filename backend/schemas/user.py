from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str


class UserLogin(BaseModel):
    correo: EmailStr
    password: str
