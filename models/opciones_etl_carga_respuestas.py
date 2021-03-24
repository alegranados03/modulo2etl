import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class OpcionesEtlCargaRespuestas(db.Database):
    __tablename__ = "opciones_etl_carga_respuestas"
    
    id_opcion_etl_carga_respuesta = Column(Integer, primary_key = True)
    nombre_columna = Column(String)
    seleccionado_numero_aspirante = Column(String)
    seleccionado_id_pregunta = Column(String)
    seleccionado_id_literal = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    
    # Propiedades relationship
    id_proceso_carga_respuesta = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_CARGA_RESPUESTAS_FK))
    proceso_etl_carga_respuestas = relationship("ProcesoEtlCargaRespuestas", back_populates = "opciones_carga_respuestas")
    