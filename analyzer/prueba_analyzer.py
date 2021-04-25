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
import analyzer.constantes as constantes
from analyzer import *

class BasePruebaAnalyzer(threading.Thread, BaseBucketCalculation):
    def __init__(self, anio, seccion_id):
        threading.Thread.__init__(self)
        self.anio = anio
        self.seccion_id = seccion_id

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
        print("Almacenar buckets")
    
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
        
        # Paso 3: Construir buckets y sus relaciones
        self.construir_buckets()
    
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