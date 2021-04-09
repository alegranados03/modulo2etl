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

class BucketTema():
    def __init__(self):
        self.preguntas = []
        self.temas = []
        self.buckets_deficiencias = []

class BucketDeficiencia():
    def __init__(self):
        self.deficiencia = -1
        self.literales = []

class BaseAdmisionAnalyzer(threading.Thread):
    def __init__(self, id_examen_admision):
        threading.Thread.__init__(self)
        self.id_examen_admision = id_examen_admision

        self.engine = create_engine(db.connection_string)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()
        self.examen = None

        self.buckets_temas = []
    
    '''
        FUNCIONES RELACIONADAS AL CALCULO DE BUCKETS
    '''
    def construir_buckets(self):
        # Paso 1: Imprimir un trace del estado original del examen
        self.imprimir_estado_examen()

        # Paso 2: Procedemos a recorrer el examen, en busqueda de temas
        for pregunta in self.examen.preguntas:
            bucket = self.obtener_bucket_tema(pregunta)

            # Paso 3: Si no encontramos un bucket, lo creamos, y anexamos
            #         la info de la pregunta
            if bucket is None:
                bucket = self.crear_bucket_tema(pregunta)
            else:
                self.anexar_pregunta_bucket(bucket, pregunta)
            
            for literal in list(filter(lambda x: x.etiqueta is not None, pregunta.literales)):
                # Paso 4: Procedemos a buscar el bucket de deficiencia, si no lo
                #         encontramos, y anexamos la info del literal
                bucket_deficiencia = self.obtener_bucket_deficiencia(bucket, literal)

                if bucket_deficiencia is None:
                    bucket_deficiencia = self.crear_bucket_deficiencia(bucket, literal)
                else:
                    self.anexar_literal_bucket(bucket_deficiencia, literal)
        
        self.imprimir_buckets_temas()
            
    def obtener_bucket_tema(self, pregunta):
        # Paso 1: recorremos la lista para determinar si existe un bucket ya con esos temas
        bucket = None

        for bucket_tema in self.buckets_temas:
            #  paso 2: Si el bucket no tiene la misma cantidad de temas, ni nos molestemos 
            #          en comprobar nada
            if (len(bucket_tema.temas) != len(pregunta.temas)):
                continue
            
            # Paso 3: En caso que el bucket tenga el mismo numero de temas que la pregunta
            #         Comprobamos que todos los ID de temas de la pregunta, se encuentren en el bucket
            temas_pregunta = [tema.id for tema in pregunta.temas]
            if (set(bucket_tema.temas) == set(temas_pregunta)):
                bucket = bucket_tema
                break

        return bucket
    
    def crear_bucket_tema(self, pregunta):
        bucket = BucketTema()
        bucket.temas = [tema.id for tema in pregunta.temas]
        bucket.preguntas.append(pregunta.id)

        self.buckets_temas.append(bucket)
        return bucket
    
    def anexar_pregunta_bucket(self, bucket, pregunta):
        bucket.preguntas.append(pregunta.id)
    
    def obtener_bucket_deficiencia(self, bucket_tema, literal):
        # Paso 1: recorremos la lista para determinar si alguno de los bucket
        #         de deficiencia representa la deficiencia del literal
        bucket = None

        for bucket_deficiencia in bucket_tema.buckets_deficiencias:
            if (literal.etiqueta.id != bucket_deficiencia.deficiencia):
                continue
            
            bucket = bucket_deficiencia
            break
        
        return bucket

    def crear_bucket_deficiencia(self, bucket_tema, literal):
        bucket_deficiencia = BucketDeficiencia()
        bucket_deficiencia.deficiencia = literal.etiqueta.id
        bucket_deficiencia.literales.append(literal.id)
        bucket_tema.buckets_deficiencias.append(bucket_deficiencia)
    
    def anexar_literal_bucket(self, bucket_deficiencia, literal):
        bucket_deficiencia.literales.append(literal.id)
    
    '''
        HELPER FUNCTIONS
    '''
    def obtener_examen(self):
        self.examen = self.session.query(ExamenAdmision).get(self.id_examen_admision)

        if (self.examen is not None):
            return self.examen
        else:
            raise Exception("No se pudo obtener el examen de admision con ID: " + str(self.id_examen_admision))
    

    '''
        DEBUGGER FUNCTIONS
    '''
    def imprimir_estado_examen(self):
        for pregunta in self.examen.preguntas:
            print("ID Referencia: " + str(pregunta.id_referencia) + " ORIGINAL: " + str(pregunta.id))
            print("Temas: " + str(len(pregunta.temas)))

            for tema in pregunta.temas:
                print("ID=" + str(tema.id) + " " + tema.nombre)
            
            print("Etiquetas involucradas: ")

            for literal in list(filter(lambda x: x.etiqueta is not None, pregunta.literales)):
                print("ID=" + str(literal.etiqueta.id) + " " + literal.etiqueta.enunciado + " LITERAL=" + str(literal.id))
            
            print("")
    
    def imprimir_buckets_temas(self):
        for bucket in self.buckets_temas:
            print("Temas: ")
            print(bucket.temas)
            print("Preguntas: ")
            print(bucket.preguntas)

            print("Deficiencias:")
            for bucket_deficiencia in bucket.buckets_deficiencias:
                print(bucket_deficiencia.deficiencia)
                print(bucket_deficiencia.literales)
            
            print("###################")




class AdmisionAnalyzer(BaseAdmisionAnalyzer):
    def __init__(self, id_examen_admision):
        BaseAdmisionAnalyzer.__init__(self, id_examen_admision)
    
    def run(self):
        # Paso 0: TODO: crear validaciones previas antes de ejecutar analyzer

        # Paso 1: Cambiar el estado del proceso de analisis que ha invocado
        #         a esta instancia

        # Paso 2: Obtener el examen de admision 
        examen = self.obtener_examen()

        # Paso 3: Construir buckets y sus relaciones
        self.construir_buckets()