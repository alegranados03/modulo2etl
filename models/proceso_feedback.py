import models.db as db

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProcesoFeedback(db.Database):
    __tablename__ = 'proceso_feedback'
    
    # Propiedades comunes
    id = Column(Integer, primary_key = True)
    estado = Column(String, nullable = False)
    datos = Column(String, nullable = True)
    

    # Propiedades relationship
    usuario_id = Column(Integer, nullable = False)
    intento_id = Column(Integer, nullable = True)
    seccion_id = Column(Integer, nullable = True)
    fecha_inicio = Column(DateTime, nullable = True)
    fecha_fin = Column(DateTime, nullable = True)

    def __init__(self, 
        estado, datos, usuario_id, intento_id,
        seccion_id, fecha_inicio, fecha_fin):
        
        self.estado = estado
        self.datos = datos
        self.usuario_id = usuario_id
        self.intento_id = intento_id
        self.seccion_id = seccion_id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin