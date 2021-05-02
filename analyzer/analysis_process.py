import models.db as db
import analyzer.constantes as constantes

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

        self.log_data = ""
        self.log_warning = ""
        self.log_error = ""
    
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
    
    def log(self, msg_type, msg):
        if (msg_type == constantes.MSG_INFO):
            self.log_data = self.log_data + ";" + msg
        else if (msg_type == costantes.MSG_WARN):
            self.log_warning = self.log_warning + ";" + msg
        else if (msg_type == costantes.ERROR):
            self.log_error = self.log_error + ";" + msg
        
        print(msg)
    
    def guardar_log(self):
        print("FUNCION A IMPLEMENTAR, GUARDAR LOG")