import threading
import time
import logging
import datetime
import models.db as db
import sys
import traceback
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import *
from queries import *
import analyzer.constantes as constantes
from analyzer import *

class BaseFeedbackExamAnalyzer(threading.Thread, BaseBucketCalculation, FeedbackProcess):
    def __init__(self, id_usuario, id_proceso_feedback, id_intento, seccion_id, fecha_inicio, fecha_fin):
        threading.Thread.__init__(self)
        BaseBucketCalculation.__init__(self)
        FeedbackProcess.__init__(self, id_proceso_feedback)

        self.ids_examenes = None
        self.examenes = None
        self.ids_intentos = []
        self.id_usuario = id_usuario
        self.id_intento = id_intento
        self.seccion_id = seccion_id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

        self.feedback = Feedback()
<<<<<<< HEAD
        self.jsonData = None
=======
>>>>>>> 24ed7a1ea76bf94e745298bd9389f5c879aaa5ed
    
    '''
        FUNCIONES RELACIONADAS AL CALCULO DE BUCKETS
    '''
    def construir_buckets(self):
         # Paso 1: Imprimir un trace del estado original del examen
        for examen in self.examenes:
            self.imprimir_estado_examen(examen)

        # Paso 2: Por cada uno de los examenes involucrados, calculamos
        #         los buckets de temas y deficiencias involucrados
        for examen in self.examenes:
            self.construir_bucket_examen(examen, constantes.MODO_EXAMENES_PRUEBA, self.seccion_id)
        
        self.imprimir_buckets_temas()
    
    '''
        FUNCIONES RELACIONADAS A LA CREACION DE LOS BUCKETS Y PERSISTENCIA
        EN BASE DE DATOS
    '''
    def almacenar_buckets(self):
        print("ALMACENANDO BUCKETS")
    
    '''
        HELPER FUNCTIONS
    '''
    def obtener_examenes_prueba(self):
        # Paso 2: Ya habiendo obtenido los ids de los examenes involucrados en el calculo
        #         procedemos a obtenerlos como objetos con todas sus relaciones
        self.examenes = self.session.query(Examen).filter(Examen.id.in_(self.ids_examenes)).all()
    

    '''
        DEBUGGER FUNCTIONS
    '''
    def imprimir_estado_examen(self, examen):      
        for pregunta in examen.preguntas:
            print("ORIGINAL: " + str(pregunta.id))
            print("Temas: " + str(len(pregunta.temas)))

            for tema in pregunta.temas:
                print("ID=" + str(tema.id) + " " + tema.nombre)
            
            print("Etiquetas involucradas: ")

            for literal in list(filter(lambda x: x.etiqueta is not None, pregunta.respuestas)):
                print("ID=" + str(literal.etiqueta.id) + " " + literal.etiqueta.enunciado + " LITERAL=" + str(literal.id))
            
            print("")

class FeedbackExamAnalyzer(BaseFeedbackExamAnalyzer):
    def __init__(self, id_usuario, id_proceso_feedback, id_intento, seccion_id, fecha_inicio, fecha_fin):
        BaseFeedbackExamAnalyzer.__init__(self, id_usuario, id_proceso_feedback, id_intento, seccion_id, fecha_inicio, fecha_fin)
    
    def run(self):
        # Paso 0: Es necesario tener validaciones para este punto?

        # Paso 1: Inicializar el proceso de analisis y cambiar su estado
        self.inicializar_proceso_feedback()

        # Paso 2: Obtener los examenes que aplican para este analisis
        #         Como tambien los intentos que aplican al calculo de
        #         fortalezas y deficiencias
        self.calcular_id_examenes_prueba()
        self.obtener_examenes_prueba()
        print(self.ids_examenes)
        print(self.ids_intentos)

        # Paso 3: Construir buckets y sus relaciones
        self.construir_buckets()

        # Paso 4: Procedemos a calcular las frecuencias
        self.calcular_frecuencias_examenes_estudiante()

        # Paso 5: Habiendo calculado los datos, procedemos a almacenar
        self.almacenar_datos(self.jsonData)
    
    def calcular_frecuencias_examenes_estudiante(self):
        print("EMPEZAMOS EL CALCULO DE FRECUENCIAS")
        self.feedback.secciones = []

        # Paso 0: Obtenemos las distintas secciones que aparecen en los
        # Buckets de temas
        secciones = list(set([bucket.seccion.id for bucket in self.buckets_temas]))
        
        for seccion in secciones:
            seccion_feedback = SeccionFeedback()
            seccion_feedback.id_seccion = seccion
            seccion_feedback.fortalezas = []
            seccion_feedback.debilidades = []

            # Paso 1: Previamente ya calculamos los ids de intentos
            #         A ocupar, por lo cual procedemos a realizar los
            #         calculos como tal
            buckets_seccion = [bucket for bucket in self.buckets_temas if bucket.seccion.id == seccion]
            try:
                seccion_feedback.nombre_seccion = buckets_seccion[0].seccion.nombre
            except:
                print("No se pudo obtener el nombre de la seccion")
            
            for bucket_tema in buckets_seccion:
                print("------------------------------------------------")
                print("CALCULANDO LA FRECUENCIA PARA LOS BUCKETS:")
                print(bucket_tema.temas)

                # Paso 2: Calculamos las fecuencias de cada respuesta elegida
                #         Para las preguntas que contempla el bucket
                datos_frecuencia = self.calcular_frecuencia_literales(bucket_tema.preguntas, self.ids_intentos)

                # Paso 3: Calcular bucket tema feedback
                bucket_tema_feedback = self.crear_bucket_tema_feedback(bucket_tema, datos_frecuencia)
                print("PARA ESTE BUCKET DE TEMAS, LA FRECUENCIA DE EXITOS ES: ")
                print("NUMERO PREGUNTAS = " + str(bucket_tema_feedback.numero_preguntas))
                print("EXITOS TOTALES = " + str(bucket_tema_feedback.aciertos))

                # Paso 4: Iteramos los buckets de deficiencia, y empezamos a realizar el calculo
                #         de frecuencias para las deficiencias
                for bucket_deficiencia in bucket_tema.buckets_deficiencias:
                    bucket_deficiencia_feedback = self.crear_bucket_deficiencia_feedback(bucket_tema_feedback, bucket_deficiencia, datos_frecuencia)
                    bucket_tema_feedback.deficiencias.append(bucket_deficiencia_feedback)
                
                seccion_feedback.fortalezas.append(bucket_tema_feedback)
            self.feedback.secciones.append(seccion_feedback)
        
        # Paso 5: Habiendo calculado fortalezas y debilidades, reordenar en base a
        #         porcentaje de fortaleza (asc = debilidad, desc = fortaleza)
        for seccion in self.feedback.secciones:
            seccion.fortalezas.sort(key=lambda x: x.porcentaje_fortaleza, reverse=True)
            seccion.debilidades = seccion.fortalezas.copy()
            seccion.debilidades.sort(key=lambda x: x.porcentaje_debilidad, reverse=True)

        #self.feedback.fortalezas.sort(key=lambda x: x.porcentaje_fortaleza, reverse=True)
        #self.feedback.debilidades = self.feedback.fortalezas.copy()
        #self.feedback.debilidades.sort(key=lambda x: x.porcentaje_debilidad, reverse=True)
        
        self.jsonData = json.dumps(self.feedback.__dict__, default=lambda o: o.__dict__, indent=4)
        print(self.jsonData)

    
    def crear_bucket_tema_feedback(self, bucket_tema, datos_frecuencia):
        temas = [TemaFeedback(tema.id, tema.nombre) for tema in bucket_tema.temas_obj]
        numero_preguntas = sum(int(dato[2]) for dato in datos_frecuencia)
        aciertos = sum(int(dato[2]) for dato in datos_frecuencia if int(dato[1]) in bucket_tema.literales_correctos)
        
        bucket = BucketFeedback(temas, numero_preguntas, aciertos)
        bucket.calcular_porcentaje_fortaleza_debilidad()
        return bucket
    
    def crear_bucket_deficiencia_feedback(self, bucket_tema, bucket_deficiencia, datos_frecuencia):
        etiqueta = EtiquetaFeedback(bucket_deficiencia.etiqueta_obj.id, bucket_deficiencia.etiqueta_obj.enunciado)
        fallos = sum(int(dato[2]) for dato in datos_frecuencia if int(dato[1]) in bucket_deficiencia.literales)

        bucket = DeficienciaFeedback(etiqueta, fallos)
        bucket.calcular_porcentaje_debilidad(bucket_tema.numero_preguntas)
        return bucket
        
    
    '''
        FUNCIONES DE RETORNO SQL
    '''
    def calcular_id_examenes_prueba(self):
        # Paso 1: Hacer la suposicion que lo que se desea calcular
        #         son las fortalezas y deficiencias de un intento
        sql = 'SELECT examen_id, id FROM intentos WHERE id = :ID_INTENTO'
        params = { 'ID_INTENTO': self.id_intento }
        
        # Paso 2: En caso que el intento sea -1 (indicando que se quiere
        #         Evaluar deficiencias por un rango de tiempo determinado)
        #         Cambiamos la consulta
        if (self.id_intento == -1):        
            sql = """
            SELECT 
                i1.examen_id,
                i1.id
            FROM
                nota_intento_seccion nis1
            INNER JOIN
                intentos i1
                ON nis1.intento_id = i1.id
            WHERE
                i1.tiempo_finalizacion_real > :FECHA_INICIO AND
                i1.tiempo_finalizacion_real < :FECHA_FIN AND
                i1.user_id = :ID_USUARIO AND
                i1.terminado = 1 AND
                nis1.seccion_id = :SECCION_ID;
            """

            params = {
                'FECHA_INICIO': self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                'FECHA_FIN': self.fecha_fin.strftime('%Y-%m-%d %H:%M:%S'),
                'ID_USUARIO': self.id_usuario,
                'SECCION_ID': self.seccion_id
            }

        ids = self.session.execute(sql, params).fetchall()
        self.ids_examenes = [examen[0] for examen in ids]
        self.ids_examenes = list(dict.fromkeys(self.ids_examenes))
        self.ids_intentos = [examen[1] for examen in ids]
    
    def calcular_frecuencia_literales(self, id_preguntas, id_intentos):
        sql = """
        SELECT
            ir.pregunta_id,
            ir.respuesta_id,
            COUNT(*) as FRECUENCIA
        FROM
            intentos_respuestas ir
        WHERE
            ir.intento_id IN :ID_INTENTOS AND
            ir.pregunta_id IN :ID_PREGUNTAS
        GROUP BY 
            ir.pregunta_id, ir.respuesta_id
        """

        # NOTA: Se ocupa el operador ternario con la lista None para evitar
        #       errores de sintaxis por parte de SQLAlchemy en la construccion
        #       de la query cuando se detecta que no hay intentos que evaluar
        params = {
            'ID_INTENTOS': [None] if len(id_intentos) == 0 else id_intentos,
            'ID_PREGUNTAS': id_preguntas
        }

        print("PARAMETROS FRECUENCIA LITERALES")
        print(params)

        return self.session.execute(sql, params).fetchall()