import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Tema(db.Database):
    __tablename__ = "temas"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    nombre = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    def __init__(self, nombre, created_at, updated_at):
        self.nombre = nombre
        self.created_at = created_at
        self.updated_at = updated_at