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

class EtlComplexWorker(EtlWorker):
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
            examen = EtlWorker.crear_examen_admision(self, proceso, "COMPLEX")
            
            # Paso 2.1: Calculamos la cantidad de lineas a leer, para 
            #           reflejar el procentaje de avance
            self.lineas = self.calcular_total_lineas(proceso, "COMPLEX")

            # Paso 2.2: Procedemos a chequear si hemos entrado en un estado de error
            #           En caso de ser asi, detenemos el trabajo
            if (self.error_state or examen is None):
                sys.exit()
                return
            
            # Paso 3: procedemos a insertar las preguntas del examen
            #         de admision
            examen = self.crear_preguntas_examen(proceso, examen)
            self.actualizar_progeso_proceso(proceso)

            # Paso 3.1: Procedemos a chequear si hemos entrado en un estado de error
            #           En caso de ser asi, detenemos el trabajo
            if (self.error_state or examen is None):
                sys.exit()
                return
            
            # Paso 4: procedemos a insertar los literales del examen
            #         de admision
            examen = self.crear_literales_examen(proceso, examen)
            self.actualizar_progeso_proceso(proceso)

            # Paso 4.1: Procedemos a chequear si hemos entrado en un estado de error
            #           En caso de ser asi, detenemos el trabajo
            if (self.error_state or examen is None):
                sys.exit()
                return
            
            # Paso 5: procedemos a insertar las respuestas del examen
            #         de admision
            self.crear_respuestas_examen(proceso, examen)
            self.actualizar_progeso_proceso(proceso, 1.0)

            # Paso 5.1: Procedemos a chequear si hemos entrado en un estado de error
            #           En caso de ser asi, detenemos el trabajo
            if (self.error_state or examen is None):
                sys.exit()
                return
            
            # Paso 5.2: Procedemos a setear todos los flag de error a 0
            #           en caso que hayan quedado residuos de errores pasados
            self.actualizar_estado_error_proceso(proceso, 0, 0, 0, 0)

            # Paso 6: procedemos a notificar que el etl ha sido
            #         terminado exitosamente
            EtlWorker.cambiar_estado_proceso(self, "TERMINADO")
            
            self.log("INFO", "proceso ETL ejecutado exitosamente")
            self.guardar_log()

        except Exception as err:
            self.session.rollback()
            if (self.id_proceso_etl is not None):
                EtlWorker.cambiar_estado_proceso(self, "TERMINADO-ERROR-CODIGO")
            self.log("ERROR", str(err))
            self.log("ERROR", traceback.format_exc())
            self.log("ERROR", "Error en el proceso etl, abortando la operacion")
            self.guardar_log()
    
    
    """
        FUNCIONES LOGICA ETL
    """    
    def crear_preguntas_examen(self, proceso, examen):
        # Paso 1: dada la informacion del proceso ETL
        #         buscar el archivo de preguntas
        self.log("INFO", "Iniciando cargado de CSV preguntas")
        carga_preguntas = proceso.proceso_etl_carga_preguntas[0]
        f = open(db.RUTA_ARCHIVOS + carga_preguntas.nombre_archivo_fisico, "r", encoding="utf-8")
        
        if (f is not None):
            self.log("INFO", "Carga de CSV de preguntas realizado con exito")
        else:
            raise Exception("Fallo al cargar CSV de preguntas: Archivo no encontrado")
        
        # Paso 2: Localizando los indices que corresponden a cada una de las columnas
        #         que conforman la pregunta en si mismo
        cabecera = f.readline().strip().split(";")
        opciones = carga_preguntas.opciones_carga_preguntas

        index_id_pregunta = -1
        nombre_columna_id_pregunta = list(filter(lambda x: x.seleccionado_id_pregunta == "Y", opciones))[0].nombre_columna
        index_texto_pregunta = -1
        nombre_columna_texto_pregunta = list(filter(lambda x: x.seleccionado_texto_pregunta == "Y", opciones))[0].nombre_columna
        linea_archivo = 1

        try:
            index_id_pregunta = cabecera.index(nombre_columna_id_pregunta)
            self.log("INFO", "Index de ID_PREG: " + str(index_id_pregunta))
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_id_pregunta, 
                    error_pregunta = 1)
            return
        
        try:
            index_texto_pregunta = cabecera.index(nombre_columna_texto_pregunta)
            self.log("INFO", "Index de TEXTO: " + str(index_texto_pregunta))
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_texto_pregunta, 
                    error_pregunta = 1)
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
                    error_pregunta = 1)
                break
            
            # Paso 3.2: Comprobando si el ID de referencia de pregunta, es un entero
            try:
                prueba_numero = int(datos[index_id_pregunta])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " ID de pregunta debe ser entero, se encontro: " + datos[index_id_pregunta], 
                    error_pregunta = 1)
                break

            pregunta = PreguntaExamenAdmision(
                examen.id,
                datos[index_id_pregunta],
                datos[index_texto_pregunta], None, 
                datetime.datetime.now(), datetime.datetime.now())
            self.session.add(pregunta)
            self.log("INFO", "Pregunta con ID=" + str(datos[index_id_pregunta]) + " agregada con exito")
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
        
    
    def crear_literales_examen(self, proceso, examen):
        # Paso 1: dada la informacion del proceso ETL
        #         buscar el archivo de preguntas
        self.log("INFO", "Iniciando cargado de CSV preguntas")
        carga_literales = proceso.proceso_etl_carga_literales[0]
        f = open(db.RUTA_ARCHIVOS + carga_literales.nombre_archivo_fisico, "r", encoding="utf-8")
        
        if (f is not None):
            self.log("INFO", "Carga de CSV de preguntas realizado con exito")
        else:
            raise Exception("Fallo al cargar CSV literales: Archivo no encontrado")
        
        # Paso 2: Localizando los indices que corresponden a cada una de las columnas
        #         que conforman el literal en si mismo
        cabecera = f.readline().strip().split(";")
        opciones = carga_literales.opciones_carga_literales

        index_id_pregunta = -1
        nombre_columna_id_pregunta = list(filter(lambda x: x.seleccionado_id_pregunta == "Y", opciones))[0].nombre_columna
        index_id_literal = -1
        nombre_columna_id_literal = list(filter(lambda x: x.seleccionado_id_literal == "Y", opciones))[0].nombre_columna
        index_correcto = -1
        nombre_columna_correcto = list(filter(lambda x: x.seleccionado_correcto == "Y", opciones))[0].nombre_columna
        index_texto_literal = -1
        nombre_columna_texto_literal = list(filter(lambda x: x.seleccionado_texto_literal == "Y", opciones))[0].nombre_columna
        linea_archivo = 1

        try:
            index_id_pregunta = cabecera.index(nombre_columna_id_pregunta)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_id_pregunta, 
                    error_literal = 1)
            return
        
        try:
            index_id_literal = cabecera.index(nombre_columna_id_literal)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_id_literal, 
                    error_literal = 1)
            return
        
        try:
            index_correcto = cabecera.index(nombre_columna_correcto)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_correcto, 
                    error_literal = 1)
            return

        try:
            index_texto_literal = cabecera.index(nombre_columna_texto_literal)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_texto_literal, 
                    error_literal = 1)
            return
        
        # Paso 3: Realizar la insercion de literales
        line = f.readline()
        contador = 0
        linea_archivo = 2
        while (line):
            datos = line.strip().split(";")
            print(datos)

            # Paso 3.1: Comprobamos si el numero de elementos de la fila es el mismo que
            #           el de la cabecera, en caso de no ser asi, lo consideramos como
            #           un problema de corrupcion
            if (len(cabecera) != len(datos)):
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " Se esperaban " + str(len(cabecera)) + " columnas, se detectaron: " + str(len(datos)), 
                    error_literal = 1)
                break
            
            # Paso 3.2: Comprobando si el ID de referencia de literal, es un entero
            try:
                prueba_numero = int(datos[index_id_literal])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " ID de literal debe ser entero, se encontro: " + datos[index_id_literal], 
                    error_literal = 1)
                break
            
            # Paso 3.3: Comprobando si el ID de referencia de pregunta, es un entero
            try:
                prueba_numero = int(datos[index_id_pregunta])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " ID de pregunta debe ser entero, se encontro: " + datos[index_id_pregunta], 
                    error_literal = 1)
                break

            correcto = 1 if datos[index_correcto] == "SI" else 0 
            literal = LiteralExamenAdmision(
                list(filter(lambda x: x.id_referencia == int(datos[index_id_pregunta]), examen.preguntas))[0].id,
                datos[index_id_literal],
                datos[index_texto_literal], None, correcto,
                datetime.datetime.now(), datetime.datetime.now())
            self.session.add(literal)
            self.log("INFO", "Literal con ID=" + datos[index_id_literal] + " para la pregunta con  ID=" + datos[index_id_pregunta] +  " agregada con exito")
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
    
    def crear_respuestas_examen(self, proceso, examen):
        # Paso 1: dada la informacion del proceso ETL
        #         buscar el archivo de preguntas
        self.log("INFO", "Iniciando cargado de CSV respuestas")
        carga_respuestas = proceso.proceso_etl_carga_respuestas[0]
        f = open(db.RUTA_ARCHIVOS + carga_respuestas.nombre_archivo_fisico, "r", encoding="utf-8")
        
        if (f is not None):
            self.log("INFO", "Carga de CSV de respuestas realizado con exito")
        else:
            raise Exception("Fallo al cargar CSV de respuestas: Archivo no encontrado")
        
        # Paso 2: Localizando los indices que corresponden a cada una de las columnas
        #         que conforman el literal en si mismo
        cabecera = f.readline().strip().split(";")
        opciones = carga_respuestas.opciones_carga_respuestas

        index_id_pregunta = -1
        nombre_columna_id_pregunta = list(filter(lambda x: x.seleccionado_id_pregunta == "Y", opciones))[0].nombre_columna
        index_id_literal = -1
        nombre_columna_id_literal = list(filter(lambda x: x.seleccionado_id_literal == "Y", opciones))[0].nombre_columna
        index_num_aspirante = -1
        nombre_columna_num_aspirante = list(filter(lambda x: x.seleccionado_numero_aspirante == "Y", opciones))[0].nombre_columna
        linea_archivo = 1

        try:
            index_id_pregunta = cabecera.index(nombre_columna_id_pregunta)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_id_pregunta, 
                    error_respuesta = 1)
            return
        
        try:
            index_id_literal = cabecera.index(nombre_columna_id_literal)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_id_literal, 
                    error_respuesta = 1)
            return
        
        try:
            index_num_aspirante = cabecera.index(nombre_columna_num_aspirante)
        except:
            # Hay excepcion cuando no encuentra la columna dentro de la cabecera
            self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " No se ha encontrado la columna " + nombre_columna_num_aspirante, 
                    error_respuesta = 1)
            return
        
        # Paso 3: Realizar la insercion de literales
        line = f.readline()
        contador = 0
        linea_archivo = 2
        id_estudiante_previo = -1
        while (line):
            datos = line.strip().split(";")

            # Paso 3.1: Comprobamos si el numero de elementos de la fila es el mismo que
            #           el de la cabecera, en caso de no ser asi, lo consideramos como
            #           un problema de corrupcion
            if (len(cabecera) != len(datos)):
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " Se esperaban " + str(len(cabecera)) + " columnas, se detectaron: " + str(len(datos)), 
                    error_respuesta = 1)
                break
            
            # Paso 3.2: Comprobando si el ID de referencia de literal, es un entero
            try:
                prueba_numero = int(datos[index_id_literal])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " ID de literal debe ser entero, se encontro: " + datos[index_id_literal], 
                    error_respuesta = 1)
                break
            
            # Paso 3.3: Comprobando si el ID de referencia de pregunta, es un entero
            try:
                prueba_numero = int(datos[index_id_pregunta])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " ID de pregunta debe ser entero, se encontro: " + datos[index_id_pregunta], 
                    error_respuesta = 1)
                break
            
            # Paso 3.4: Comprobando si el ID de referencia de pregunta, es un entero
            try:
                prueba_numero = int(datos[index_num_aspirante])
            except:
                print("Entramos a la rutina de error")
                self.rutina_corrupcion_datos(proceso, linea_archivo,
                    " Num aspirante/ NIE debe ser entero, se encontro: " + datos[index_num_aspirante], 
                    error_respuesta = 1)
                break
            
            pregunta = None
            literal = None
            saltar_agregado = False

            try:
                pregunta = list(filter(lambda x: x.id_referencia == int(datos[index_id_pregunta]), examen.preguntas))[0]
            except:
                self.log("WARNING", "Linea " + str(linea_archivo) + ": No se ha encontrado la pregunta con ID=" + datos[index_id_pregunta] + ", se ha procedido a saltarse la pregunta")
                saltar_agregado = True
            
            if (saltar_agregado == False):
                try:
                    literal = list(filter(lambda x: x.id_referencia == int(datos[index_id_literal]), pregunta.respuestas))[0]
                except:
                    self.log("WARNING", "Linea " + str(linea_archivo) + ": No se ha encontrado el literal con ID=" + datos[index_id_literal] + " para la pregunta con ID=" + str(pregunta.id) + ", se ha procedido a saltarse la pregunta")
                    saltar_agregado = True
            
            if (saltar_agregado == False):
                respuesta = RespuestaExamenAdmision(
                    datos[index_num_aspirante],
                    examen.id,
                    pregunta.id,
                    literal.id,
                    datetime.datetime.now(), datetime.datetime.now())
                
                self.session.add(respuesta)

                if (id_estudiante_previo == -1):
                    id_estudiante_previo = int(datos[index_num_aspirante])
                else:
                    if (id_estudiante_previo != int(datos[index_num_aspirante])):
                        self.log("INFO", "Respuestas para el alumno con ID=" + datos[index_num_aspirante] + " agregadas con exito")
                        id_estudiante_previo = int(datos[index_num_aspirante])

            #self.log("INFO", "Respuesta a la pregunta con ID=" + datos[index_id_pregunta] + " del estudiante con ID=" + datos[index_num_aspirante] +  " agregada con exito")
            line = f.readline()
            
            contador = contador + 1
            linea_archivo= linea_archivo + 1
            contador = self.calcular_proceso_batch(proceso, contador)
        
        # Paso 4: Commit changes al final de la extraccion
        #         mas un poco de cleanup
        self.session.commit()
        f.close()