import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Etiqueta(db.Database):
    __tablename__ = "etiquetas"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    enunciado = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    def __init__(self, enunciado, created_at, updated_at):
        self.enunciado = enunciado
        self.created_at = created_at
        self.updated_at = updated_at