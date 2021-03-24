import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class RespuestaExamenAdmision(db.Database):
    __tablename__ = "respuesta_examen_admision"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    numero_aspirante = Column(Integer)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    id_examen_admision = Column(Integer, ForeignKey(db.TBL_EXAMEN_ADMISION_FK))
    id_pregunta_examen_admision = Column(Integer, ForeignKey(db.TBL_PREGUNTA_EXAMEN_ADMISION_FK))
    id_literal_pregunta = Column(Integer, ForeignKey(db.TBL_LITERAL_EXAMEN_ADMISION_FK))
    
    
    def __init__(self, numero_aspirante, id_examen_admision, id_pregunta_examen_admision,
        id_literal_pregunta, created_at, updated_at):
        
        self.numero_aspirante = numero_aspirante
        self.id_examen_admision = id_examen_admision
        self.id_pregunta_examen_admision = id_pregunta_examen_admision
        self.id_literal_pregunta = id_literal_pregunta
        self.created_at = created_at
        self.updated_at = updated_at