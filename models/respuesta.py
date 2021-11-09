import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Respuesta(db.Database):
    __tablename__ = "respuestas"
    
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    enunciado = Column(String)
    correcta = Column(Integer)
    tipo_respuesta = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    
    # Propiedades relationship
    pregunta_id = Column(Integer, ForeignKey(db.TBL_PREGUNTA_FK))

    etiqueta_id = Column(Integer, ForeignKey(db.TBL_ETIQUETA_FK), nullable = True)
    etiqueta = relationship("Etiqueta")
    
    
    def __init__(self, enunciado, correcta, tipo_respuesta, 
        created_at, updated_at):
        
        self.enunciado = enunciado
        self.correcta = correcta
        self.tipo_respuesta = tipo_respuesta
        self.created_at = created_at
        self.updated_at = updated_at