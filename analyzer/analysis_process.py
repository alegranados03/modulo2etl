import models.db as db

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import *

class AnalysisProcess:
    def __init__(self, id_proceso_analisis):
        self.id_proceso_analisis = id_proceso_analisis
        self.proceso_analisis = None
        self.numero_instituciones = 0
        self.instituciones_procesadas = 0

        self.engine = create_engine(db.connection_string)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()
    
    def inicializar_proceso_analisis(self):
        self.obtener_proceso()
        self.cambiar_estado("EJECUTANDO")
        self.calcular_instituciones()
        self.actualizar_progreso(0)
    
    def obtener_proceso(self):
        self.proceso_analisis = self.session.query(ProcesoAnalisis).get(self.id_proceso_analisis)
    
    def cambiar_estado(self, estado):
        self.proceso_analisis.estado = estado
        self.proceso_analisis.ejecutar_ahora = 1
        self.session.commit()
    
    def actualizar_progreso(self, pcj = None):
        porcentaje = pcj

        if pcj is None:
            porcentaje = self.instituciones_procesadas / self.numero_instituciones
        
        self.proceso_analisis.pcj_analisis = int(porcentaje*100)
        self.session.commit()

    
    def calcular_instituciones(self):
        self.numero_instituciones = self.session.query(Institucion.id).count()
        self.instituciones_procesadas = 0