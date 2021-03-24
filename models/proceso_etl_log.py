import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProcesoEtlLog(db.Database):
    __tablename__ = 'proceso_etl_log'
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    texto_log = Column(String)
    warning_log = Column(String)
    error_log = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    id_proceso_etl = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_FK))
    
    
    def __init__(self, id_proceso_etl,
        texto_log, warning_log, error_log, created_at, updated_at):
        
        self.id_proceso_etl = id_proceso_etl
        self.texto_log = texto_log
        self.warning_log = warning_log
        self.error_log = error_log
        self.created_at = created_at
        self.updated_at = updated_at
        