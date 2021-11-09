import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class BucketDeficienciaExamenPrueba(db.Database):
    __tablename__ = "bucket_def_exp"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    #created_at = Column(DateTime, nullable = True)
    #updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    bucket_tema_exp_id = Column(Integer, ForeignKey(db.TBL_BUCKET_TEMA_EXAMEN_PRUEBA_FK))
    etiqueta_id = Column(Integer, ForeignKey(db.TBL_ETIQUETA_FK))

    etiqueta =  relationship("Etiqueta")
    
    def __init__(self, bucket_tema_exp_id, etiqueta_id):
        self.bucket_tema_exp_id = bucket_tema_exp_id
        self.etiqueta_id = etiqueta_id