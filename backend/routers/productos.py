from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import SessionLocal
from models.producto import Producto

router = APIRouter(prefix="/productos", tags=["productos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return [
        {"id": p.id, "nombre": p.nombre, "precio": p.precio, "descripcion": p.descripcion}
        for p in productos
    ]


@router.get("/{id_producto}")
def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "descripcion": producto.descripcion,
    }
