import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProcesoEtlCargaLiterales(db.Database):
    __tablename__ = 'proceso_etl_carga_literales'
    
    id_proceso_carga_literales = Column(Integer, primary_key = True)
    nombre_archivo_original = Column(String)
    nombre_archivo_fisico = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    id_proceso_etl = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_FK))
    proceso_etl = relationship("ProcesoEtl", back_populates = "proceso_etl_carga_literales")
    
    opciones_carga_literales = relationship("OpcionesEtlCargaLiterales", back_populates = "proceso_etl_carga_literales")
    
    def __init__(self, nombre_archivo_original, 
        nombre_archivo_fisico, created_at, updated_at):
        
        self.nombre_archivo_original = nombre_archivo_original
        self.nombre_archivo_fisico = nombre_archivo_fisico
        self.created_at = created_at
        self.updated_at = updated_at