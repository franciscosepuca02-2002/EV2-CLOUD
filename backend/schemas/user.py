from pydantic import BaseModel

class UserCreate(BaseModel):

    nombre: str
    correo: str
    password: str


class UserLogin(BaseModel):

    correo: str
    password: str