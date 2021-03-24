import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProcesoEtl(db.Database):
    __tablename__ = 'proceso_etls'
    
    # Propiedades comunes
    id_proceso_etl = Column(Integer, primary_key = True)
    estado = Column(String)
    datos_previos_cargados = Column(String)
    estrategia_datos_previos = Column(String, nullable = True)
    tipo_etl = Column(String)
    fecha_hora = Column(DateTime, nullable = True)
    ejecutar_ahora = Column(Integer)
    pcj_etl = Column(Integer)
    error_preg = Column(Integer)
    error_lit = Column(Integer)
    error_resp = Column(Integer)
    error_resu = Column(Integer)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    proceso_etl_generalidades = relationship("ProcesoEtlPasoGeneralidades", back_populates = "proceso_etl")
    proceso_etl_carga_preguntas = relationship("ProcesoEtlCargaPreguntas", back_populates = "proceso_etl")
    proceso_etl_carga_literales = relationship("ProcesoEtlCargaLiterales", back_populates = "proceso_etl")
    proceso_etl_carga_respuestas = relationship("ProcesoEtlCargaRespuestas", back_populates = "proceso_etl")
    
    # Propiedades relationship resumen (etl simple)
    proceso_etl_resumen_simple = relationship("ProcesoEtlCargaResumenSimple", back_populates = "proceso_etl")
    
    
    def __init__(self, 
        estado, datos_previos_cargados, 
        estrategia_datos_previos, tipo_etl, fecha_hora,
        ejecutar_ahora, pcj_etl, error_preg, error_lit, error_resp, error_resu, created_at, updated_at):
        
        self.estado = estado
        self.estrategia_datos_previos = estrategia_datos_previos
        self.tipo_etl = tipo_etl
        self.fecha_hora = fecha_hora
        self.ejecutar_ahora = ejecutar_ahora
        self.pcj_etl = pcj_etl
        self.error_preg = error_preg
        self.error_lit = error_lit
        self.error_resp = error_resp
        self.error_resu = error_resu
        self.created_at = created_at
        self.updated_at = updated_at
        