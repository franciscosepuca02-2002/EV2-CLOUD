import os
import logging
import requests
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import SessionLocal
from models.pedido import Pedido

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagos", tags=["pagos"])

APP_PAGOS_URL = os.getenv("APP_PAGOS_URL", "http://app-pagos:8002")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ItemCarrito(BaseModel):
    id: int
    nombre: str
    precio: float


class IniciarPagoRequest(BaseModel):
    id_usuario: int
    email: str
    items: List[ItemCarrito]


@router.post("/iniciar")
def iniciar_pago(payload: IniciarPagoRequest, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Carrito vacío")

    total = sum(item.precio for item in payload.items)
    descripcion = f"Compra Tienda Cloud ({len(payload.items)} producto(s))"

    try:
        response = requests.post(
            f"{APP_PAGOS_URL}/pagos/crear",
            json={
                "id_usuario": payload.id_usuario,
                "descripcion": descripcion,
                "monto": total,
                "email_pagador": payload.email,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error("Error llamando a app-pagos: %s", e)
        raise HTTPException(status_code=502, detail="Error contactando servicio de pagos")

    external_reference = data.get("data", {}).get("external_reference")
    pedido = Pedido(
        id_usuario=payload.id_usuario,
        total=total,
        estado="PENDIENTE",
        external_reference=external_reference,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    return {
        "pedido_id": pedido.id,
        "url_pago": data.get("data", {}).get("url_pago"),
        "external_reference": external_reference,
        "total": total,
    }


@router.get("/pedido/{pedido_id}")
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {
        "id": pedido.id,
        "id_usuario": pedido.id_usuario,
        "total": pedido.total,
        "estado": pedido.estado,
        "external_reference": pedido.external_reference,
        "creado_en": pedido.creado_en.isoformat() if pedido.creado_en else None,
    }
