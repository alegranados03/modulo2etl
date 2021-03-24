import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProcesoEtlPasoGeneralidades(db.Database):
    __tablename__ = 'proceso_etl_paso_generalidades'
    
    id_proceso_generalidades = Column(Integer, primary_key=True)
    id_area_conocimiento = Column(Integer, nullable = True)
    anio = Column(Integer)
    fase = Column(Integer)
    tipo_proceso_etl = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    id_proceso_etl = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_FK))
    proceso_etl = relationship("ProcesoEtl", back_populates = "proceso_etl_generalidades")
    
    def __init__(self, id_etl, id_area, anio, fase, tipo, created, updated):
        self.id_proceso_etl = id_etl
        self.id_area_conocimiento = id_area
        self.anio = anio
        self.fase = fase
        self.tipo_proceso_etl = tipo
        self.created_at = created
        self.updated_at = updated
        
        
    