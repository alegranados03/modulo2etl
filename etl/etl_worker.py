import threading
import time
import logging
import datetime
import models.db as db
import sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import *

class EtlWorker(threading.Thread):
    def __init__(self, id_proceso_etl):
        threading.Thread.__init__(self)
        self.engine = create_engine(db.connection_string)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()
        self.id_proceso_etl = id_proceso_etl
        self.log_data = ""
        self.log_data_warning = ""
        self.log_data_error = ""
        self.lineas = 0
        self.lineas_procesadas = 0
        self.BULK_SIZE = 100
        self.error_state = False
        logging.basicConfig(format='%(asctime)s %(message)s')
    
    """ 
        FUNCIONES RELACIONADAS A LA CREACION Y OBTENCION DE EXAMEN DE ADMISION
        Y PROCESO ETL
    """
    def crear_examen_admision(self, proceso, tipo):
        generalidades = proceso.proceso_etl_generalidades[0]
        examen = None

        # Paso 1: Obtener si existe otro examen de admision con las caracteristicas
        #         Dadas
        examen_existente = self.session.query(ExamenAdmision).filter(ExamenAdmision.anio == generalidades.anio,
            ExamenAdmision.fase == generalidades.fase, 
            ExamenAdmision.id_area_conocimiento == generalidades.id_area_conocimiento)
        
        if (examen_existente.count() > 0):
            self.log("INFO", "Se encontro un examen de admision ya existente")
            self.log("INFO", "Obteniendo examen de admision...")
            examen = examen_existente[0]
            self.log("INFO", "Se obtuvo el examen de admision con ID = " + str(examen.id))

            # Paso 1.1: En base al tipo, decidir si eliminar datos de simple o complejo
            if (tipo == "COMPLEX"):
                self.session.query(PreguntaExamenAdmision).filter(PreguntaExamenAdmision.id_examen_admision == examen.id).delete()
            else:
                self.session.query(ResumenExamenAdmision).filter(ResumenExamenAdmision.id_examen_admision == examen.id).delete()
            
            self.session.commit()
        else:
            self.log("INFO", "Creando examen de admision")
            examen = ExamenAdmision(generalidades.anio, generalidades.fase, generalidades.id_area_conocimiento,
                datetime.datetime.now(), datetime.datetime.now())
            self.session.add(examen)
            self.session.commit()
            self.log("INFO", "Examen de admision con ID = " + str(examen.id) +  " creado con exito")
        
        return examen
    
    def cambiar_estado_proceso(self, estado):
        proceso = self.obtener_proceso()
        self.log("INFO", "Seteando estado = " + estado)
        proceso.estado = estado
        proceso.ejecutar_ahora = 1
        self.session.commit()
        self.log("INFO", "Estado del proceso ETL cambiado con exito")
        
        return proceso
    
    def actualizar_estado_error_proceso(self, proceso, error_pregunta = 0, 
        error_literal = 0, error_respuesta = 0, error_resumen = 0):

        proceso.error_preg = error_pregunta
        proceso.error_lit = error_literal
        proceso.error_resp = error_respuesta
        proceso.error_resu = error_resumen

        self.session.commit()
    
    def revertir_cambios_etl(self, proceso):
        generalidades = proceso.proceso_etl_generalidades[0]
        examen_existente = self.session.query(ExamenAdmision).filter(ExamenAdmision.anio == generalidades.anio,
            ExamenAdmision.fase == generalidades.fase, 
            ExamenAdmision.id_area_conocimiento == generalidades.id_area_conocimiento)

        try:
            self.session.commit()
        except:
            d = None
        
        if (examen_existente):
            examen_existente.delete()
            self.session.commit()

    
    def actualizar_progeso_proceso(self, proceso, pcj = None):
        porcentaje = pcj
        if (pcj is None):
            porcentaje = self.lineas_procesadas / self.lineas
            
        proceso.pcj_etl = int(porcentaje*100)
        self.session.commit()
        
    
    def obtener_proceso(self):
        self.log("INFO", "Obteniendo proceso ETL con ID: " + str(self.id_proceso_etl))
        proceso = self.session.query(ProcesoEtl).get(self.id_proceso_etl)
        
        if (proceso is not None):
            self.log("INFO", "Proceso obtenido exitosamente")
        else:
            raise Exception("Error al obtener proceso ETL: proceso con ID: " + str(self.id_proceso_etl) + " no encontrado, abortando operacion")
            
        return proceso

    """
        FUNCIONES RELACIONADAS AL MANEJO DE ERRORES A NIVEL ETL
    """
    def rutina_corrupcion_datos(self, proceso, linea, msg, error_pregunta = 0, 
        error_literal = 0, error_respuesta = 0, error_resumen = 0):
        # Paso 1: Reflejar la corrupcion en el proceso
        if (error_pregunta != 0):
            self.actualizar_estado_error_proceso(proceso, error_pregunta = error_pregunta)
            self.log("ERROR", "Error en el archivo de preguntas, linea: " + str(linea) + msg)
        elif (error_literal != 0):
            self.actualizar_estado_error_proceso(proceso, error_literal = error_literal)
            self.log("ERROR", "Error en el archivo de literales, linea: " + str(linea) + msg)
        elif (error_respuesta != 0):
            self.actualizar_estado_error_proceso(proceso, error_respuesta = error_respuesta)
            self.log("ERROR", "Error en el archivo de respuestas, linea: " + str(linea) + msg)
        elif (error_resumen != 0):
            self.actualizar_estado_error_proceso(proceso, error_resumen = error_resumen)
            self.log("ERROR", "Error en el archivo de resumen de notas, linea: " + str(linea) + msg)
        
        # Paso 2: Actualizar el ETL a un estado de error controlado
        self.cambiar_estado_proceso("TERMINADO-ERROR")
        self.revertir_cambios_etl(proceso)
        self.guardar_log()
        self.error_state = True
    
    """ 
        HELPER FUNCTIONS
    """
    
    def calcular_proceso_batch(self, proceso, contador):
        self.lineas_procesadas = self.lineas_procesadas + 1
        if (contador == self.BULK_SIZE):
                self.session.commit()
                self.actualizar_progeso_proceso(proceso)
                self.log("INFO", "Progreso ETL: " + str(proceso.pcj_etl))
                return 0
        return contador
    
    def calcular_total_lineas(self, proceso, modo):
        suma = 0
        
        if (modo == "SIMPLE"):
            try:
                carga_resumen = proceso.proceso_etl_resumen_simple[0]
                suma = suma + self.calcular_lineas_archivo(db.RUTA_ARCHIVOS + carga_resumen.nombre_archivo_fisico)
            except:
                self.rutina_corrupcion_datos(proceso, -1,
                    " No se ha encontrado el archivo " + carga_resumen.nombre_archivo_original + ", por favor vuelva a subir el archivo", 
                    error_resumen = 1)
                return
        else:
            try:
                carga_preguntas = proceso.proceso_etl_carga_preguntas[0]
                suma = suma + self.calcular_lineas_archivo(db.RUTA_ARCHIVOS + carga_preguntas.nombre_archivo_fisico)
            except:
                self.rutina_corrupcion_datos(proceso, -1,
                    " No se ha encontrado el archivo " + carga_preguntas.nombre_archivo_original + ", por favor vuelva a subir el archivo", 
                    error_pregunta = 1)
                return
            
            try:
                carga_literales = proceso.proceso_etl_carga_literales[0]
                suma = suma + self.calcular_lineas_archivo(db.RUTA_ARCHIVOS + carga_literales.nombre_archivo_fisico)
            except:
                self.rutina_corrupcion_datos(proceso, -1,
                    " No se ha encontrado el archivo " + carga_literales.nombre_archivo_original + ", por favor vuelva a subir el archivo", 
                    error_literal = 1)
                return
            
            try:
                carga_respuestas = proceso.proceso_etl_carga_respuestas[0]
                suma = suma + self.calcular_lineas_archivo(db.RUTA_ARCHIVOS + carga_respuestas.nombre_archivo_fisico)
            except:
                self.rutina_corrupcion_datos(proceso, -1,
                    " No se ha encontrado el archivo " + carga_respuestas.nombre_archivo_original + ", por favor vuelva a subir el archivo", 
                    error_respuesta = 1)
                return
        
        return suma
            
    def calcular_lineas_archivo(self, file):
        return sum(1 for i in open(file, 'rb'))
        
    def log(self, msg_type, msg):
        if (msg_type == "INFO"):
            self.log_data = self.log_data + ";" + msg_type + " " + msg
        elif (msg_type == "WARNING"):
            self.log_data_warning = self.log_data_warning + ";" + msg_type + " " + msg
        elif (msg_type == "ERROR"):
            self.log_data_error = self.log_data_error + ";" + msg_type + " " + msg
        
        print(msg)
    
    def guardar_log(self):
        self.session.query(ProcesoEtlLog).filter(ProcesoEtlLog.id_proceso_etl == self.id_proceso_etl).delete()
        self.session.commit()
        log = ProcesoEtlLog(
                self.id_proceso_etl,
                self.log_data,
                self.log_data_warning,
                self.log_data_error,
                datetime.datetime.now(), datetime.datetime.now())
        self.session.add(log)
        self.session.commit()