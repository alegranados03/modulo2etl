import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class BucketTemaAdmision(db.Database):
    __tablename__ = "bucket_tema_adm"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    id_examen_admision = Column(Integer)
    #created_at = Column(DateTime, nullable = True)
    #updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    temas =  relationship("Tema", secondary=db.bucket_tema_adm_detalle)
    deficiencias = relationship("BucketDeficienciaAdmision")
    
    def __init__(self, id_examen_admision):
        self.id_examen_admision = id_examen_admision