import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import engine, SessionLocal, Base
from models.user import User  # noqa
from models.producto import Producto
from models.pedido import Pedido  # noqa

from routers.auth import router as auth_router
from routers.productos import router as productos_router
from routers.pagos import router as pagos_router







logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_productos():
    """Inserta productos iniciales si la tabla está vacía."""
    db = SessionLocal()
    try:
        if db.query(Producto).count() == 0:
            productos_iniciales = [
                Producto(nombre="Notebook Lenovo", precio=800000, descripcion="Notebook 14'' i5 16GB RAM"),
                Producto(nombre="Teclado Mecánico", precio=30000, descripcion="Teclado mecánico RGB"),
                Producto(nombre="Monitor LG 24''", precio=120000, descripcion="Monitor IPS Full HD"),
                Producto(nombre="Mouse Logitech", precio=20000, descripcion="Mouse inalámbrico"),
                Producto(nombre="Monitor Samsung 27''", precio=180000, descripcion="Monitor curvo QHD"),
                Producto(nombre="Audífonos HyperX", precio=55000, descripcion="Audífonos gamer 7.1"),
            ]
            db.add_all(productos_iniciales)
            db.commit()
            logger.info("Productos sembrados en BD")
    except Exception as e:
        logger.error("Error sembrando productos: %s", e)
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_productos()
    yield


app = FastAPI(title="Tienda Cloud API", lifespan=lifespan)

# CORS abierto para demo (en producción restringir a dominio del frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(productos_router)
app.include_router(pagos_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "backend"}
