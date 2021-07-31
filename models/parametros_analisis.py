import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ParametrosAnalisis(db.Database):
    __tablename__ = 'parametros_analisis'
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    estado = Column(String)
    datos = Column(String)
    pcj_analisis = Column(Integer)
    enlace = Column(String, nullable = True)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    def __init__(self, 
        estado, datos, pcj_analisis, enlace,
        created_at, updated_at):
        
        self.estado = estado
        self.datos = datos
        self.pcj_analisis = pcj_analisis
        self.enlace = enlace
        self.created_at = created_at
        self.updated_at = updated_at