import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class BucketTemaExamenPrueba(db.Database):
    __tablename__ = "bucket_tema_exp"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    anio = Column(Integer)
    seccion_id = Column(Integer)
    #created_at = Column(DateTime, nullable = True)
    #updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    temas =  relationship("Tema", secondary=db.bucket_tema_exp_detalle)
    deficiencias = relationship("BucketDeficienciaExamenPrueba")
    
    def __init__(self, anio, seccion_id):
        self.anio = anio
        self.seccion_id = seccion_id