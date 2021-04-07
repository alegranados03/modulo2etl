import threading
import time
import logging
import datetime
import models.db as db
import sys
from models import *


class EtlWorker(threading.Thread):
    def __init__(self, id_proceso_etl):
        threading.Thread.__init__(self)
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
        examen_existente = db.session.query(ExamenAdmision).filter(ExamenAdmision.anio == generalidades.anio,
            ExamenAdmision.fase == generalidades.fase, 
            ExamenAdmision.id_area_conocimiento == generalidades.id_area_conocimiento)
        
        if (examen_existente.count() > 0):
            self.log("INFO", "Se encontro un examen de admision ya existente")
            self.log("INFO", "Obteniendo examen de admision...")
            examen = examen_existente[0]
            self.log("INFO", "Se obtuvo el examen de admision con ID = " + str(examen.id))

            # Paso 1.1: En base al tipo, decidir si eliminar datos de simple o complejo
            if (tipo == "COMPLEX"):
                db.session.query(PreguntaExamenAdmision).filter(PreguntaExamenAdmision.id_examen_admision == examen.id).delete()
            else:
                db.session.query(ResumenExamenAdmision).filter(ResumenExamenAdmision.id_examen_admision == examen.id).delete()
            
            db.session.commit()
        else:
            self.log("INFO", "Creando examen de admision")
            examen = ExamenAdmision(generalidades.anio, generalidades.fase, generalidades.id_area_conocimiento,
                datetime.datetime.now(), datetime.datetime.now())
            db.session.add(examen)
            db.session.commit()
            self.log("INFO", "Examen de admision con ID = " + str(examen.id) +  " creado con exito")
        
        return examen
    
    def cambiar_estado_proceso(self, estado):
        proceso = self.obtener_proceso()
        self.log("INFO", "Seteando estado = " + estado)
        proceso.estado = estado
        proceso.ejecutar_ahora = 1
        db.session.commit()
        self.log("INFO", "Estado del proceso ETL cambiado con exito")
        
        return proceso
    
    def actualizar_estado_error_proceso(self, proceso, error_pregunta = 0, 
        error_literal = 0, error_respuesta = 0, error_resumen = 0):

        proceso.error_preg = error_pregunta
        proceso.error_lit = error_literal
        proceso.error_resp = error_respuesta
        proceso.error_resu = error_resumen

        db.session.commit()
    
    def revertir_cambios_etl(self, proceso):
        generalidades = proceso.proceso_etl_generalidades[0]
        examen_existente = db.session.query(ExamenAdmision).filter(ExamenAdmision.anio == generalidades.anio,
            ExamenAdmision.fase == generalidades.fase, 
            ExamenAdmision.id_area_conocimiento == generalidades.id_area_conocimiento)

        try:
            db.session.commit()
        except:
            d = None
        
        if (examen_existente):
            examen_existente.delete()
            db.session.commit()

    
    def actualizar_progeso_proceso(self, proceso, pcj = None):
        porcentaje = pcj
        if (pcj is None):
            porcentaje = self.lineas_procesadas / self.lineas
            
        proceso.pcj_etl = int(porcentaje*100)
        db.session.commit()
        
    
    def obtener_proceso(self):
        self.log("INFO", "Obteniendo proceso ETL con ID: " + str(self.id_proceso_etl))
        proceso = db.session.query(ProcesoEtl).get(self.id_proceso_etl)
        
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
                db.session.commit()
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
        db.session.query(ProcesoEtlLog).filter(ProcesoEtlLog.id_proceso_etl == self.id_proceso_etl).delete()
        db.session.commit()
        log = ProcesoEtlLog(
                self.id_proceso_etl,
                self.log_data,
                self.log_data_warning,
                self.log_data_error,
                datetime.datetime.now(), datetime.datetime.now())
        db.session.add(log)
        db.session.commit()

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
            if (self.id_proceso_etl is not None):
                EtlWorker.cambiar_estado_proceso(self, "TERMINADO-ERROR-CODIGO")
            self.log("ERROR", str(err))
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
        f = open(db.RUTA_ARCHIVOS + carga_preguntas.nombre_archivo_fisico, "r", encoding="latin-1")
        
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

            pregunta = PreguntaExamenAdmision(
                examen.id,
                datos[index_id_pregunta],
                datos[index_texto_pregunta], None, 
                datetime.datetime.now(), datetime.datetime.now())
            db.session.add(pregunta)
            self.log("INFO", "Pregunta con ID=" + str(datos[index_id_pregunta]) + " agregada con exito")
            line = f.readline()
            
            contador = contador + 1
            linea_archivo = linea_archivo + 1
            contador = self.calcular_proceso_batch(proceso, contador)
        
        # Paso 4: Commit changes al final de la extraccion
        #         mas un poco de cleanup
        db.session.commit()
        f.close()
        
        # Paso 5: Obtenemos datos de examen solo si no hemos entrado en un estado de error
        if (self.error_state == False):
            examen = db.session.query(ExamenAdmision).get(examen.id)
        else:
            examen = None
        
        return examen
        
    
    def crear_literales_examen(self, proceso, examen):
        # Paso 1: dada la informacion del proceso ETL
        #         buscar el archivo de preguntas
        self.log("INFO", "Iniciando cargado de CSV preguntas")
        carga_literales = proceso.proceso_etl_carga_literales[0]
        f = open(db.RUTA_ARCHIVOS + carga_literales.nombre_archivo_fisico, "r", encoding="latin-1")
        
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

            correcto = 1 if datos[index_correcto] == "SI" else 0 
            literal = LiteralExamenAdmision(
                list(filter(lambda x: x.id_referencia == int(datos[index_id_pregunta]), examen.preguntas))[0].id,
                datos[index_id_literal],
                datos[index_texto_literal], None, correcto,
                datetime.datetime.now(), datetime.datetime.now())
            db.session.add(literal)
            self.log("INFO", "Literal con ID=" + datos[index_id_literal] + " para la pregunta con  ID=" + datos[index_id_pregunta] +  " agregada con exito")
            line = f.readline()
            
            contador = contador + 1
            linea_archivo = linea_archivo + 1
            contador = self.calcular_proceso_batch(proceso, contador)
        
        
        # Paso 4: Commit changes al final de la extraccion
        #         mas un poco de cleanup
        db.session.commit()
        f.close()

        # Paso 5: Obtenemos datos de examen solo si no hemos entrado en un estado de error
        if (self.error_state == False):
            examen = db.session.query(ExamenAdmision).get(examen.id)
        else:
            examen = None
        
        return examen
    
    def crear_respuestas_examen(self, proceso, examen):
        # Paso 1: dada la informacion del proceso ETL
        #         buscar el archivo de preguntas
        self.log("INFO", "Iniciando cargado de CSV respuestas")
        carga_respuestas = proceso.proceso_etl_carga_respuestas[0]
        f = open(db.RUTA_ARCHIVOS + carga_respuestas.nombre_archivo_fisico, "r", encoding="latin-1")
        
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
                    literal = list(filter(lambda x: x.id_referencia == int(datos[index_id_literal]), pregunta.literales))[0]
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
                
                db.session.add(respuesta)

                if (id_estudiante_previo == -1):
                    id_estudiante_previo = int(datos[index_num_aspirante])
                else:
                    if (id_estudiante_previo != int(datos[index_num_aspirante])):
                        #self.log("INFO", "Respuestas para el alumno con ID=" + datos[index_num_aspirante] + " agregadas con exito")
                        id_estudiante_previo = int(datos[index_num_aspirante])

            #self.log("INFO", "Respuesta a la pregunta con ID=" + datos[index_id_pregunta] + " del estudiante con ID=" + datos[index_num_aspirante] +  " agregada con exito")
            line = f.readline()
            
            contador = contador + 1
            linea_archivo= linea_archivo + 1
            contador = self.calcular_proceso_batch(proceso, contador)
        
        # Paso 4: Commit changes al final de la extraccion
        #         mas un poco de cleanup
        db.session.commit()
        f.close()


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
        f = open(db.RUTA_ARCHIVOS + carga_resumen.nombre_archivo_fisico, "r", encoding="latin-1")
        
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

            resumen = ResumenExamenAdmision(
                datos[index_num_aspirante],
                datos[index_numero_preguntas],
                datos[index_numero_respuestas_correctas],
                "",
                examen.id,
                datetime.datetime.now(), datetime.datetime.now())
            db.session.add(resumen)    
            self.log("INFO", "Resumen para el estudiante con ID=" + datos[index_num_aspirante] + " agregado con exito")
            line = f.readline()
            
            contador = contador + 1
            linea_archivo = linea_archivo + 1
            contador = self.calcular_proceso_batch(proceso, contador)
            
        # Paso 4: Commit changes al final de la extraccion
        #         mas un poco de cleanup
        db.session.commit()
        f.close()
        
        # Paso 5: Obtenemos datos de examen solo si no hemos entrado en un estado de error
        if (self.error_state == False):
            examen = db.session.query(ExamenAdmision).get(examen.id)
        else:
            examen = None
        
        return examen