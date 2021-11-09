import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Examen(db.Database):
    __tablename__ = "examenes"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    nombre = Column(String)
    descripcion = Column(String)
    cantidad_intentos = Column(Integer)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    # id_proceso_etl = Column(Integer, ForeignKey(db.TBL_PROCESO_ETL_FK))
    #id_area_conocimiento = Column(Integer, ForeignKey(db.TBL_AREA_CONOCIMIENTO_FK))
    
    preguntas = relationship("Pregunta", secondary=db.examen_preguntas)
    
    def __init__(self, nombre, descripcion, cantidad_intentos,
        created_at, updated_at):
        
        # self.id_proceso_etl = id_proceso_etl
        self.nombre = nombre
        self.descripcion = descripcion
        self.cantidad_intentos = cantidad_intentos
        self.created_at = created_at
        self.updated_at = updated_at