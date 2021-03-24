import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class OpcionesEtlCargaPreguntas(db.Database):
    __tablename__ = "opciones_etl_carga_preguntas"
    
    id_opcion_etl_carga_pregunta = Column(Integer, primary_key = True)
    nombre_columna = Column(String)
    seleccionado_id_pregunta = Column(String)
    seleccionado_texto_pregunta = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    
    # Propiedades relationship
    id_proceso_carga_preguntas = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_CARGA_PREGUNTAS))
    proceso_etl_carga_preguntas = relationship("ProcesoEtlCargaPreguntas", back_populates = "opciones_carga_preguntas")
    