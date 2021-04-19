import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class BucketTemaAdmisionInstituto(db.Database):
    __tablename__ = "bucket_tema_adm_instituto"
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    preguntas = Column(Integer)
    preguntas_masculino = Column(Integer)
    preguntas_femenino = Column(Integer)
    aciertos = Column(Integer)
    aciertos_masculino = Column(Integer)
    aciertos_femenino = Column(Integer)
    fallos = Column(Integer)
    fallos_masculino = Column(Integer)
    fallos_femenino = Column(Integer)
    #created_at = Column(DateTime, nullable = True)
    #updated_at = Column(DateTime, nullable = True)
    
    # Propiedades relationship
    bucket_tema_adm_id = Column(Integer, ForeignKey(db.TBL_BUCKET_TEMA_ADMISION_FK))
    institucion_id = Column(Integer, ForeignKey(db.TBL_INSTITUCION_FK))

    deficiencias = relationship("BucketDeficienciaAdmisionInstituto")
    
    def __init__(self, bucket_tema_adm_id, institucion_id,
        preguntas, preguntas_masculino, preguntas_femenino,
        aciertos, aciertos_masculino, aciertos_femenino,
        fallos, fallos_masculino, fallos_femenino):

        self.bucket_tema_adm_id = bucket_tema_adm_id
        self.institucion_id = institucion_id
        self.preguntas = preguntas
        self.preguntas_masculino = preguntas_masculino
        self.preguntas_femenino = preguntas_femenino
        self.aciertos = aciertos
        self.aciertos_masculino = aciertos_masculino
        self.aciertos_femenino = aciertos_femenino
        self.fallos = fallos
        self.fallos_masculino = fallos_masculino
        self.fallos_femenino = fallos_femenino