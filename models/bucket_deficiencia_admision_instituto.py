import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class BucketDeficienciaAdmisionInstituto(db.Database):
    __tablename__ = "bucket_deficiencia_adm_instituto"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    fallos = Column(Integer)
    fallos_masculino = Column(Integer)
    fallos_femenino = Column(Integer)
    #created_at = Column(DateTime, nullable = True)
    #updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    bucket_deficiencia_adm_id = Column(Integer, ForeignKey(db.TBL_BUCKET_DEFICIENCIA_ADMISION_FK))
    bucket_tema_adm_instituto_id = Column(Integer, ForeignKey(db.TBL_BUCKET_TEMA_ADMISION_INSTITUTO_FK))
    
    def __init__(self, bucket_tema_adm_instituto_id, bucket_deficiencia_adm_id, 
        fallos, fallos_masculino, fallos_femenino):
        self.bucket_tema_adm_instituto_id = bucket_tema_adm_instituto_id
        self.bucket_deficiencia_adm_id = bucket_deficiencia_adm_id
        self.fallos = fallos
        self.fallos_masculino = fallos_masculino
        self.fallos_femenino = fallos_femenino