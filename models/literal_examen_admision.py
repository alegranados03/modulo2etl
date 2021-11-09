import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class LiteralExamenAdmision(db.Database):
    __tablename__ = "literal_examen_admision"
    
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    id_referencia = Column(Integer)
    texto_literal = Column(String)
    imagen_literal = Column(String, nullable = True)
    literal_correcto = Column(Integer)
    created_at = Column(DateTime, nullable = True)
    updated_at = Column(DateTime, nullable = True)
    
    
    # Propiedades relationship
    id_pregunta_examen_admision = Column(Integer, ForeignKey(db.TBL_PREGUNTA_EXAMEN_ADMISION_FK))

    etiqueta_id = Column(Integer, ForeignKey(db.TBL_ETIQUETA_FK), nullable = True)
    etiqueta = relationship("Etiqueta")
    
    
    def __init__(self, id_pregunta_examen_admision, id_referencia,
        texto_literal, imagen_literal, literal_correcto, 
        created_at, updated_at):
        
        self.id_pregunta_examen_admision = id_pregunta_examen_admision
        self.id_referencia = id_referencia
        self.texto_literal = texto_literal
        self.imagen_literal = imagen_literal
        self.literal_correcto = literal_correcto
        self.created_at = created_at
        self.updated_at = updated_at