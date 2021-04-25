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

class BasePruebaAnalyzer(threading.Thread):
    def __init__(self, anio, id_area_conocimiento):
        threading.Thread.__init__(self)
        self.anio = anio
        self.id_area_conocimiento = id_area_conocimiento

        self.engine = create_engine(db.connection_string)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()
        self.examenes = None
        self.ids_examenes = None

        self.buckets_temas = []
    
    '''
        FUNCIONES RELACIONADAS AL CALCULO DE BUCKETS
    '''
    def construir_buckets(self):
        print("Construir buckets")
            
    def obtener_bucket_tema(self, pregunta):
        print("Obtener bucket de tema")
    
    def crear_bucket_tema(self, pregunta):
        print("Crear bucket")
    
    def anexar_pregunta_bucket(self, bucket, pregunta):
        print("Anexar bucket")
    
    def obtener_bucket_deficiencia(self, bucket_tema, literal):
        print("Obtener bucket de deficiencia")

    def crear_bucket_deficiencia(self, bucket_tema, literal):
        print("Crear bucket de deficiencia")
    
    def anexar_literal_bucket(self, bucket_deficiencia, literal):
        print("Anexar literal bucket")
    
    '''
        FUNCIONES RELACIONADAS A LA CREACION DE LOS BUCKETS Y PERSISTENCIA
        EN BASE DE DATOS
    '''
    def almacenar_buckets(self):
        print("Almacenar buckets")
    
    '''
        HELPER FUNCTIONS
    '''
    def obtener_examenes_prueba(self):
        # Paso 2: Ya habiendo obtenido los ids de los examenes involucrados en el calculo
        #         procedemos a obtenerlos como objetos con todas sus relaciones
        self.examenes = self.session.query(Examen).filter(Examen.id.in_(self.ids_examenes)).all()

        """for examen in self.examenes:
            for pregunta in examen.preguntas:
                print(pregunta.enunciado)

                for tema in pregunta.temas:
                    print(tema.nombre)
                
                for respuesta in pregunta.respuestas:
                    print(respuesta.enunciado)
                    print(respuesta.etiqueta)"""

        print(self.examenes)
    

    '''
        DEBUGGER FUNCTIONS
    '''
    def imprimir_estado_examen(self):
        print("estado examen")
    
    def imprimir_buckets_temas(self):
        for bucket in self.buckets_temas:
            print("Temas: ")
            print(bucket.temas)
            print("Preguntas: ")
            print(bucket.preguntas)
            print("Literales correctos: ")
            print(bucket.literales_correctos)

            print("Deficiencias:")
            for bucket_deficiencia in bucket.buckets_deficiencias:
                print(bucket_deficiencia.deficiencia)
                print(bucket_deficiencia.literales)
            
            print("###################")









class PruebaAnalyzer(BasePruebaAnalyzer):
    def __init__(self, anio, id_area_conocimiento):
        BasePruebaAnalyzer.__init__(self, anio, id_area_conocimiento)
    
    def run(self):
        # Paso 0: TODO: crear validaciones previas antes de ejecutar analyzer

        # Paso 1: Cambiar el estado del proceso de analisis que ha invocado
        #         a esta instancia

        # Paso 2: Obtener los examenes que aplican para este analisis
        self.calcular_id_examenes_prueba()
        self.obtener_examenes_prueba()
        print("Hola mundo")
    
    def calcular_id_examenes_prueba(self):
        # Paso 1: Obtener los examenes que, para el año a calcular, se encuentran
        #         vigentes aun
        sql = """
        SELECT 
            id 
        FROM 
            examenes
        WHERE
            ((YEAR(examenes.disponible_desde) = :ANIO_EXAMEN) OR 
             (YEAR(examenes.disponible_hasta) = :ANIO_EXAMEN))
            OR
            (YEAR(examenes.disponible_desde) < :ANIO_EXAMEN AND YEAR(examenes.disponible_hasta) > :ANIO_EXAMEN)
        """

        params = {
            'ANIO_EXAMEN': self.anio
        }

        ids = self.session.execute(sql, params).fetchall()
        self.ids_examenes = [examen[0] for examen in ids]