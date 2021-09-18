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
from etl import *

class EtlSimpleWorker(EtlWorker):
    def __init__(self, id_proceso_etl):
        EtlWorker.__init__(self, id_proceso_etl)
    
    def run(self):
        try:
            # Paso 1: Obtenemos proceso etl y cambiamos su estado
            #         a "Ejecutando"
            proceso = EtlWorker.cambiar_estado_proceso(self, "EJECUTANDO")
            self.actualizar_progeso_proceso(proceso, 0.0)
            
            # Paso 2: Ahora que obtuvimos el proceso ETL, procedemos
            #         a crear la fila de examen de admision que representa
            examen = EtlWorker.crear_examen_admision(self, proceso, "SIMPLE")
            
            # Paso 2.1: Calculamos la cantidad de lineas a leer, para 
            #           reflejar el procentaje de avance
            self.lineas = self.calcular_total_lineas(proceso, "SIMPLE")

            # Paso 2.2: Procedemos a chequear si hemos entrado en un estado de error
            #           En caso de ser asi, detenemos el trabajo
            if (self.error_state or examen is None):
                sys.exit()
                return
            
            # Paso 3: Realizamos el llenado del resumen
            examen = self.crear_resumen(proceso, examen)
            self.actualizar_progeso_proceso(proceso, 1.0)

            # Paso 3.1: Procedemos a chequear si hemos entrado en un estado de error
            #           En caso de ser asi, detenemos el trabajo
            if (self.error_state or examen is None):
                sys.exit()
                return
            
            # Paso 3.2: Procedemos a setear todos los flag de error a 0
            #           en caso que hayan quedado residuos de errores pasados
            self.actualizar_estado_error_proceso(proceso, 0, 0, 0, 0)

            # Paso 4: procedemos a notificar que el etl ha sido
            #         terminado exitosamente
            EtlWorker.cambiar_estado_proceso(self, "TERMINADO")
            
            self.log("INFO", "ETL ejecutado exitosamente")
            self.guardar_log()
            
        except Exception as err:
            if (self.id_proceso_etl is not None):
                EtlWorker.cambiar_estado_proceso(self, "TERMINADO-ERROR")
            self.log("ERROR", str(err))
            self.log("ERROR", "Error en el proceso etl, abortando la operacion")
            self.guardar_log()
    
    """
        FUNCIONES LOGICA ETL
    """
    def crear_resumen(self, proceso, examen):
        # Paso 1: dada la informacion del proceso ETL
        #         buscar el archivo de preguntas
        self.log("INFO", "Iniciando cargado de CSV resumen area de conocimiento")
        carga_resumen = proceso.proceso_etl_resumen_simple[0]
        f = open(db.RUTA_ARCHIVOS + carga_resumen.nombre_archivo_fisico, "r", encoding="utf-8", errors='ignore')
        
        if (f is not None):
            self.log("INFO", "Carga de CSV de resumen realizado con exito")
        else:
            raise Exception("Fallo al cargar CSV: Archivo no encontrado")
        
        # Paso 2: Localizando los indices que corresponden a cada una de las columnas
        #         que conforman la pregunta en si mismo
        cabecera = f.readline().strip().split(";")
        opciones = carga_resumen.opciones_carga_resumen

        index_num_aspirante = -1
        nombre_columna_num_aspirante = list(filter(lambda x: x.seleccionado_numero_aspirante == "Y", opciones))[0].nombre_columna
        index_numero_preguntas = -1
        nombre_columna_num_preguntas = list(filter(lambda x: x.seleccionado_numero_preguntas == "Y", opciones))[0].nombre_columna
        index_numero_respuestas_correctas = -1
        nombre_columna_numero_respuestas_correctas = list(filter(lambda x: x.seleccionado_respuestas_correctas == "Y", opciones))[0].nombre_columna
        linea_archivo = 1

        try:
            index_num_aspirante = cabecera.index(nombre_columna_num_aspirante)
            self.log("INFO", "Index de NUM_ASPIRANTE: " + str(index_num_aspirante))
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_num_aspirante, 
                    error_resumen = 1)
            return
        
        try:
            index_numero_preguntas = cabecera.index(nombre_columna_num_preguntas)
            self.log("INFO", "Index de NUM_PREG: " + str(index_numero_preguntas))
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_num_preguntas, 
                    error_resumen = 1)
            return
        
        try:
            index_numero_respuestas_correctas = cabecera.index(nombre_columna_numero_respuestas_correctas)
            self.log("INFO", "Index de RESP_CORR: " + str(index_numero_preguntas))
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_numero_respuestas_correctas, 
                    error_resumen = 1)
            return
        
        # Paso 3: Realizar la insercion de preguntas
        line = f.readline()
        contador = 0
        linea_archivo = 2 
        while (line):
            datos = line.strip().split(";")

            # Paso 3.1: Comprobamos si el numero de elementos de la fila es el mismo que
            #           el de la cabecera, en caso de no ser asi, lo consideramos como
            #           un problema de corrupcion
            if (len(cabecera) != len(datos)):
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " Se esperaban " + str(len(cabecera)) + " columnas, se detectaron: " + str(len(datos)), 
                    error_resumen = 1)
                break
            
            # Paso 3.2: Comprobando si el num de aspirante, es un entero
            try:
                prueba_numero = int(datos[index_num_aspirante])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " NUM aspirante/NIE debe ser entero, se encontro: " + datos[index_num_aspirante], 
                    error_resumen = 1)
                break
            
            # Paso 3.3: Comprobando si el num de preguntas, es un entero
            try:
                prueba_numero = int(datos[index_numero_preguntas])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " Num preguntas debe ser entero, se encontro: " + datos[index_numero_preguntas], 
                    error_resumen = 1)
                break
            
            # Paso 3.4: Comprobando si el num de preguntas correctas, es un entero
            try:
                prueba_numero = int(datos[index_numero_respuestas_correctas])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " Num respuestas correctas debe ser entero, se encontro: " + datos[index_numero_respuestas_correctas], 
                    error_resumen = 1)
                break

            resumen = ResumenExamenAdmision(
                datos[index_num_aspirante],
                datos[index_numero_preguntas],
                datos[index_numero_respuestas_correctas],
                "",
                examen.id,
                datetime.datetime.now(), datetime.datetime.now())
            self.session.add(resumen)    
            self.log("INFO", "Resumen para el estudiante con ID=" + datos[index_num_aspirante] + " agregado con exito")
            line = f.readline()
            
            contador = contador + 1
            linea_archivo = linea_archivo + 1
            contador = self.calcular_proceso_batch(proceso, contador)
            
        # Paso 4: Commit changes al final de la extraccion
        #         mas un poco de cleanup
        self.session.commit()
        f.close()
        
        # Paso 5: Obtenemos datos de examen solo si no hemos entrado en un estado de error
        if (self.error_state == False):
            examen = self.session.query(ExamenAdmision).get(examen.id)
        else:
            examen = None
        
        return examen