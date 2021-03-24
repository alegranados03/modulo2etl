import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ResumenExamenAdmision(db.Database):
    __tablename__ = "resumen_examen_admision"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    numero_aspirante = Column(Integer)
    numero_preguntas = Column(Integer)
    preguntas_correctas = Column(Integer)
    materia = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    id_examen_admision = Column(Integer, ForeignKey(db.TBL_EXAMEN_ADMISION_FK))
    
    def __init__(self, numero_aspirante, numero_preguntas,
        preguntas_correctas, materia, id_examen_admision,
        created_at, updated_at):
        
        self.numero_aspirante = numero_aspirante
        self.numero_preguntas = numero_preguntas
        self.preguntas_correctas = preguntas_correctas
        self.materia = materia
        self.id_examen_admision = id_examen_admision
        self.created_at = created_at
        self.updated_at = updated_at