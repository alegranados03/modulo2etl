import models.db as db
import analyzer.constantes as constantes

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import *

class FeedbackProcess:
    def __init__(self, id_proceso_feedback):
        self.id_proceso_feedback = id_proceso_feedback
        self.proceso_feedback = None
        self.numero_examenes = 0
        self.examenes_procesados = 0

        self.engine = create_engine(db.connection_string)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()

        self.log_data = ""
        self.log_warning = ""
        self.log_error = ""
    
    def inicializar_proceso_feedback(self):
        self.obtener_proceso()
        self.cambiar_estado("EJECUTANDO")
    
    def obtener_proceso(self):
        print("Obteniendo proceso con ID=" +  str(self.id_proceso_feedback))
        self.proceso_feedback = self.session.query(ProcesoFeedback).get(self.id_proceso_feedback)
    
    def cambiar_estado(self, estado):
        print("CAMBIANDO ESTADO DEL PROCESO FEEDBACK")
        self.proceso_feedback.estado = estado
        self.session.commit()
    
    def almacenar_datos(self, datos):
        print("ALMACENANDO DATOS DEL PROCESO FEEDBACK")
        self.cambiar_estado("TERMINADO")
        self.proceso_feedback.datos = datos
        self.session.commit()
        
    
    def actualizar_progreso(self, pcj = None):
        porcentaje = pcj

        if pcj is None:
            porcentaje = self.examenes_procesados / self.numero_examenes
        
        # TODO: cambiar el estado en DB del proceso feedback
        """self.proceso_feedback.pcj_analisis = int(porcentaje*100)
        self.session.commit()"""
    
    def calcular_examenes(self):
        self.numero_examenes = 1
        self.examenes_procesados = 0
    
    def log(self, msg_type, msg):
        if (msg_type == constantes.MSG_INFO):
            self.log_data = self.log_data + ";" + msg
        elif (msg_type == costantes.MSG_WARN):
            self.log_warning = self.log_warning + ";" + msg
        elif (msg_type == costantes.ERROR):
            self.log_error = self.log_error + ";" + msg
        
        print(msg)
    
    def guardar_log(self):
        print("FUNCION A IMPLEMENTAR, GUARDAR LOG")
