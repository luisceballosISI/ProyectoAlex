# base_datos/modelos_sql.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

# Usamos SQLite para guardar los datos en un archivo local
SQLALCHEMY_DATABASE_URL = "sqlite:///./historial_asistente.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definimos la tabla de nuestra base de datos
class Interaccion(Base):
    __tablename__ = "interacciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, index=True)      # aaron, aide o luis
    pregunta_texto = Column(String)           # Lo que transcriba el STT
    respuesta_ia = Column(String)             # Lo que conteste el sistema
    fecha = Column(DateTime, default=datetime.datetime.utcnow)


Base.metadata.create_all(bind=engine)

# guardar un registro
def guardar_interaccion(usuario, pregunta, respuesta):
    db = SessionLocal()
    nueva_interaccion = Interaccion(
        usuario=usuario, 
        pregunta_texto=pregunta, 
        respuesta_ia=respuesta
    )
    db.add(nueva_interaccion)
    db.commit()
    db.refresh(nueva_interaccion)
    db.close()
    return nueva_interaccion.id