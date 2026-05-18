from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(Float, nullable=False)
    estado = Column(String(50), default="PENDIENTE")
    external_reference = Column(String(100), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
