import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ExamenAdmision(db.Database):
    __tablename__ = "examen_admision"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    anio = Column(Integer)
    fase = Column(Integer)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    # id_proceso_etl = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_FK))
    id_area_conocimiento = Column(Integer, ForeignKey(db.TBL_AREA_CONOCIMIENTO_FK))
    
    preguntas = relationship("PreguntaExamenAdmision")
    
    def __init__(self, anio, fase, id_area_conocimiento,
        created_at, updated_at):
        
        # self.id_proceso_etl = id_proceso_etl
        self.anio = anio
        self.fase = fase
        self.id_area_conocimiento = id_area_conocimiento
        self.created_at = created_at
        self.updated_at = updated_at
    