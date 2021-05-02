import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProcesoAnalisis(db.Database):
    __tablename__ = 'proceso_analisis'
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    estado = Column(String)
    tipo_analisis = Column(String)
    fecha_hora = Column(DateTime, nullable = True)
    pcj_analisis = Column(Integer)
    ejecutar_ahora = Column(Integer)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)

    # Propiedades relationship
    id_examen_admision = Column(Integer, ForeignKey(db.TBL_EXAMEN_ADMISION_FK), nullable=True)
    seccion_id = Column(Integer, ForeignKey(db.TBL_SECCION_FK), nullable=True)
    
    def __init__(self, 
        estado, tipo_analisis, 
        fecha_hora, pcj_analisis, ejecutar_ahora,
        created_at, updated_at):
        
        self.estado = estado
        self.tipo_analisis = tipo_analisis
        self.fecha_hora = fecha_hora
        self.pcj_analisis = pcj_analisis
        self.ejecutar_ahora = ejecutar_ahora
        self.pcj_etl = pcj_etl
        self.created_at = created_at
        self.updated_at = updated_at