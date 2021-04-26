import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class BucketDeficienciaPruebaInstituto(db.Database):
    __tablename__ = "bucket_def_exp_ins"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    fallos = Column(Integer)
    fallos_masculino = Column(Integer)
    fallos_femenino = Column(Integer)
    #created_at = Column(DateTime, nullable = True)
    #updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    bucket_def_exp_id = Column(Integer, ForeignKey(db.TBL_BUCKET_DEFICIENCIA_EXAMEN_PRUEBA_FK))
    bucket_tema_exp_ins_id = Column(Integer, ForeignKey(db.TBL_BUCKET_TEMA_EXAMEN_PRUEBA_INSTITUTO_FK))
    
    def __init__(self, bucket_tema_exp_ins_id, bucket_def_exp_id, 
        fallos, fallos_masculino, fallos_femenino):
        self.bucket_tema_exp_ins_id = bucket_tema_exp_ins_id
        self.bucket_def_exp_id = bucket_def_exp_id
        self.fallos = fallos
        self.fallos_masculino = fallos_masculino
        self.fallos_femenino = fallos_femenino