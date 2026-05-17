from sqlalchemy import Column, Integer, String

from database.database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(100))

    correo = Column(String(100), unique=True)

    password = Column(String(255))