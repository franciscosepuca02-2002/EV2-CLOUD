from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from database.database import engine
from models.user import User
from routers.auth import router as auth_router


app = FastAPI()
User.metadata.create_all(bind=engine)
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

productos = [
    {
        "id":1,
        "nombre":"Notebook",
        "precio":800000
    },
    {
        "id":2,
        "nombre":"Teclado",
        "precio":30000
    },
    {
        "id":3,
        "nombre":"Monitor",
        "precio":50000
    },
    {
        "id":4,
        "nombre":"Mouse Logitech",
        "precio":20000
    },
    {
        "id":5,
        "nombre":"Monitor Samsung",
        "precio":60000
    }
]

@app.get("/productos")
def listar_productos():
    return productos

@app.post("/crear-pago")
def crear_pago():

    try:

        url = "http://app-pagos:8002/pagos/crear"

        payload = {
            "id_usuario": 1,
            "descripcion": "Compra Tienda Cloud",
            "monto": 5000,
            "email_pagador": "test@test.cl"
        }

        response = requests.post(url, json=payload)

        print("STATUS:", response.status_code)
        print("RESPUESTA:", response.text)

        return response.json()

    except Exception as e:

        return {
            "error": str(e)
        }