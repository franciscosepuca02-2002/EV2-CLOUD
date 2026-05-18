from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database.database import SessionLocal
from models.user import User
from schemas.user import UserCreate, UserLogin

router = APIRouter(tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/registro")
def registro(user: UserCreate, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.correo == user.correo).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    password_hash = pwd_context.hash(user.password)
    nuevo_usuario = User(
        nombre=user.nombre,
        correo=user.correo,
        password=password_hash
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "message": "Usuario registrado",
        "usuario": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "correo": nuevo_usuario.correo,
        }
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.correo == user.correo).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    if not pwd_context.verify(user.password, usuario.password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    return {
        "message": "Login correcto",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo
        }
    }
