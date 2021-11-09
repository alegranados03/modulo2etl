import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Pregunta(db.Database):
    __tablename__ = "preguntas"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    enunciado = Column(String)
    tipo_pregunta = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    seccion_id = Column(Integer, ForeignKey(db.TBL_SECCION_FK))
    seccion = relationship("Seccion")
    respuestas = relationship("Respuesta")

    temas =  relationship("Tema", secondary=db.preguntas_temas)
    
    def __init__(self, enunciado, tipo_pregunta,
        created_at, updated_at):
        
        self.enunciado = enunciado
        self.tipo_pregunta = tipo_pregunta
        self.created_at = created_at
        self.updated_at = updated_at