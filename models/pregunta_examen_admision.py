import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class PreguntaExamenAdmision(db.Database):
    __tablename__ = "pregunta_examen_admision"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    id_referencia = Column(Integer)
    texto_pregunta = Column(String)
    imagen_pregunta = Column(String, nullable = True)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    id_examen_admision = Column(Integer, ForeignKey(db.TBL_EXAMEN_ADMISION_FK))
    literales = relationship("LiteralExamenAdmision")

    temas =  relationship("Tema", secondary=db.preguntas_examen_admision_temas)
    
    def __init__(self, id_examen_admision, id_referencia,
        texto_pregunta, imagen_pregunta, 
        created_at, updated_at):
        
        self.id_examen_admision = id_examen_admision
        self.id_referencia = id_referencia
        self.texto_pregunta = texto_pregunta
        self.imagen_pregunta = imagen_pregunta
        self.created_at = created_at
        self.updated_at = updated_at