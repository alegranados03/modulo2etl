import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class OpcionesEtlCargaResumen(db.Database):
    __tablename__ = "opciones_etl_carga_resumenes"
    
    id_opcion_etl_carga_resumen = Column(Integer, primary_key = True)
    nombre_columna = Column(String)
    seleccionado_numero_aspirante = Column(String)
    seleccionado_numero_preguntas = Column(String)
    seleccionado_respuestas_correctas = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    
    # Propiedades relationship
    id_proceso_carga_resumen = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_CARGA_RESUMENES))
    proceso_etl_carga_resumen = relationship("ProcesoEtlCargaResumenSimple", back_populates = "opciones_carga_resumen")
    
    