import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class OpcionesEtlCargaLiterales(db.Database):
    __tablename__ = "opciones_etl_carga_literales"
    
    id_opcion_etl_carga_literal = Column(Integer, primary_key = True)
    nombre_columna = Column(String)
    seleccionado_id_pregunta = Column(String)
    seleccionado_id_literal = Column(String)
    seleccionado_correcto = Column(String)
    seleccionado_texto_literal = Column(String)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    
    # Propiedades relationship
    id_proceso_carga_literales = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_CARGA_LITERALES_FK))
    proceso_etl_carga_literales = relationship("ProcesoEtlCargaLiterales", back_populates = "opciones_carga_literales")
    