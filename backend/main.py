from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

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