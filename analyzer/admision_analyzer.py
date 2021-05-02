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

class BaseAdmisionAnalyzer(threading.Thread, BaseBucketCalculation, AnalysisProcess):
    def __init__(self, id_examen_admision, id_proceso_analisis):
        threading.Thread.__init__(self)
        BaseBucketCalculation.__init__(self)
        AnalysisProcess.__init__(self, id_proceso_analisis)

        self.id_examen_admision = id_examen_admision
        self.examen = None
    
    '''
        FUNCIONES RELACIONADAS AL CALCULO DE BUCKETS
    '''
    def construir_buckets(self):
        # Paso 1: Imprimir un trace del estado original del examen
        self.imprimir_estado_examen()

        # Paso 2: Por cada uno de los examenes involucrados, calculamos
        #         los buckets de temas y deficiencias involucrados
        self.construir_bucket_examen(self.examen, constantes.MODO_ADMISION)
        self.imprimir_buckets_temas()
    
    '''
        FUNCIONES RELACIONADAS A LA CREACION DE LOS BUCKETS Y PERSISTENCIA
        EN BASE DE DATOS
    '''
    def almacenar_buckets(self):
        for bucket_tema in self.buckets_temas:
            # Paso 2: Agregando informacion basica del tema
            bucket = BucketTemaAdmision(self.examen.id)
            bucket.temas = self.session.query(Tema).filter(Tema.id.in_(bucket_tema.temas)).all()

            # Paso 3: Agregando buckets de deficiencia
            bucket.deficiencias = []
            for bucket_deficiencia in bucket_tema.buckets_deficiencias:
                bucket2 = BucketDeficienciaAdmision(None, bucket_deficiencia.deficiencia)
                bucket.deficiencias.append(bucket2)
            
            bucket_tema.referencia_bucket_tema = bucket
            self.session.add(bucket)
        
        self.session.commit()
    
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

            for literal in list(filter(lambda x: x.etiqueta is not None, pregunta.respuestas)):
                print("ID=" + str(literal.etiqueta.id) + " " + literal.etiqueta.enunciado + " LITERAL=" + str(literal.id))
            
            print("")


class AdmisionAnalyzer(BaseAdmisionAnalyzer):
    def __init__(self, id_examen_admision, id_proceso_analisis):
        BaseAdmisionAnalyzer.__init__(self, id_examen_admision, id_proceso_analisis)
    
    def run(self):
        # Paso 0: TODO: crear validaciones previas antes de ejecutar analyzer

        # Paso 1: Inicializar el proceso de analisis y cambiar su estado
        self.inicializar_proceso_analisis()

        # Paso 1.2: Eliminar rastros de cualquier calculo realizado previamente
        self.eliminar_analisis_previo()

        # Paso 2: Obtener el examen de admision 
        self.obtener_examen()

        # Paso 3: Construir buckets y sus relaciones
        self.construir_buckets()

        # Paso 4: Construir los modelos ORM del calculo de tuplas de temas
        #         y las etiquetas de deficiencia asociadas a dichas tuplas
        self.almacenar_buckets()

        # Paso 5: Procedemos a calcular las frecuencias a nivel de institucion
        #         en base a genero
        self.calcular_frecuencias_institucion_genero()
    
    def eliminar_analisis_previo(self):
        print("POR HACER ELIMINACION")
    
    def calcular_frecuencias_institucion_genero(self):
        print("EMPEZAMOS EL CALCULO DE FRECUENCIAS")
        # Paso 1: Obtenemos todas las instituciones que vamos a ocupar para calcular
        instituciones = self.session.query(Institucion)

        # Paso 2: Iteramos cada una de las instituciones y empezamos el calculo
        for institucion in instituciones:
            print("PROCEDEMOS A CALCULAR EL INSTITUTO CON ID=" + str(institucion.id))

            # Paso 3: Por cada institucion, tenemos que calcular todos los buckets de temas
            #         y sus respectivas deficiencias
            for bucket_tema in self.buckets_temas:
                print("------------------------------------------------")
                print("CALCULANDO LA FRECUENCIA PARA LOS BUCKETS:")
                print(bucket_tema.temas)

                # Paso 4: Creamos el bucket de tema para la institucion, y lo llenamos con la
                #         data inicial (numero de preguntas por genero)
                bucket_tema_instituto = self.crear_bucket_tema_instituto(institucion, bucket_tema)

                # Paso 5: Procedemos a calcular las frecuencias (por genero) de cada uno de lo literales
                #         de las preguntas involugradas en este bucket
                datos_frecuencia = self.calcular_frecuencia_literales_genero(institucion.id, bucket_tema.preguntas)

                # Paso 6: En base a las frecuencias procedemos a obtener y calcular la frecuencia de aciertos
                #         respecto a las preguntas que cubre este bucket
                self.calcular_aciertos_genero(bucket_tema, bucket_tema_instituto, datos_frecuencia)

                print("PARA ESTE BUCKET DE TEMAS, LA FRECUENCIA DE EXITOS ES: ")
                print("EXITOS TOTALES = " + str(bucket_tema_instituto.aciertos))
                print("EXITOS M=" + str(bucket_tema_instituto.aciertos_masculino))
                print("EXITOS F=" + str(bucket_tema_instituto.aciertos_femenino))
                
                # Paso 7: Iteramos los buckets de deficiencia, y empezamos a realizar el calculo
                #         de frecuencias para las deficiencias
                for bucket_deficiencia in bucket_tema.buckets_deficiencias:
                    # Paso 8: Obtenemos la referencia correspondiente en DB
                    referencia_bucket_deficiencia = list(filter(lambda x: x.etiqueta_id == bucket_deficiencia.deficiencia, 
                        bucket_tema.referencia_bucket_tema.deficiencias))
                    
                    if (len(referencia_bucket_deficiencia) == 0):
                        raise Exception("No se encontro referencia a bucket de deficiencia")
                    else:
                        referencia_bucket_deficiencia = referencia_bucket_deficiencia[0]
                    
                    # Paso 9: Nos limitamos a la data involucrada para este bucket de deficiencia
                    datos_frec_deficiencia = list(filter(lambda x: x[0] in bucket_tema.preguntas 
                        and (x[1] in bucket_deficiencia.literales),
                        datos_frecuencia))
                    
                    # Paso 10: Con la data filtrada procedemos a crear buckets de deficiencia
                    bucket_deficiencia_instituto = self.crear_bucket_deficiencia_instituto(referencia_bucket_deficiencia)
                    for frecuencia_deficiencia in datos_frec_deficiencia:
                        if (frecuencia_deficiencia[2] == "M"):
                            bucket_deficiencia_instituto.fallos_masculino = bucket_deficiencia_instituto.fallos_masculino + frecuencia_deficiencia[3]
                        else:
                            bucket_deficiencia_instituto.fallos_femenino = bucket_deficiencia_instituto.fallos_femenino + frecuencia_deficiencia[3]
                    
                    # Paso 11: Calculamos fallos totales a nivel de bucket de deficiencia, como a nivel de
                    #          bucket de tema que contiene dicha deficiencia, ademas de esto lo agregamos
                    #          al bucket de tema, para persistirlo
                    bucket_deficiencia_instituto.fallos = bucket_deficiencia_instituto.fallos_masculino + bucket_deficiencia_instituto.fallos_femenino
                    bucket_tema_instituto.fallos = bucket_tema_instituto.fallos + bucket_deficiencia_instituto.fallos
                    bucket_tema_instituto.fallos_masculino = bucket_tema_instituto.fallos_masculino + bucket_deficiencia_instituto.fallos_masculino
                    bucket_tema_instituto.fallos_femenino = bucket_tema_instituto.fallos_femenino + bucket_deficiencia_instituto.fallos_femenino

                    bucket_tema_instituto.deficiencias.append(bucket_deficiencia_instituto)
                    
                    print("PARA ESTE BUCKET DE DEFICIENCIA, LA FRECUENCIA DE FALLOS ES: ")
                    print(bucket_deficiencia.deficiencia)
                    print("FALLOS TOTALES: " + str(bucket_deficiencia_instituto.fallos))
                    print("FALLOS M=" + str(bucket_deficiencia_instituto.fallos_masculino))
                    print("FALLOS F=" + str(bucket_deficiencia_instituto.fallos_femenino))
                
                self.session.add(bucket_tema_instituto)
            self.session.commit()

    
    
    def crear_bucket_tema_instituto(self, institucion, bucket_tema):
        # Paso 1: Creamos el bucket de instituto, con datos por defecto a 0
        bucket_tema_instituto = BucketTemaAdmisionInstituto(
            bucket_tema.referencia_bucket_tema.id,
            institucion.id,
            0, 0, 0, 0, 0, 0, 0, 0, 0
        )

        # Paso 2: Obtenemos los datos generales de numero de preguntas, y lo anexamos al bucket
        #         de instituto, los fallos y aciertos los iremos calculando mientras vayamos
        #         iterando las etiquetas de deficiencia
        datos_generales = self.calcular_pregunta_genero(institucion.id, bucket_tema.preguntas)
        cuenta_M = list(filter(lambda x: x[0] == "M", datos_generales))
        cuenta_F = list(filter(lambda x: x[0] == "F", datos_generales))

        bucket_tema_instituto.preguntas_masculino = 0
        bucket_tema_instituto.preguntas_femenino = 0

        if len(cuenta_M) > 0:
            bucket_tema_instituto.preguntas_masculino = cuenta_M[0][1]
        
        if len(cuenta_F) > 0:
            bucket_tema_instituto.preguntas_femenino = cuenta_F[0][1]
        
        bucket_tema_instituto.preguntas = bucket_tema_instituto.preguntas_masculino + bucket_tema_instituto.preguntas_femenino
        
        print("M=" + str(bucket_tema_instituto.preguntas_masculino))
        print("F=" + str(bucket_tema_instituto.preguntas_femenino))

        return bucket_tema_instituto
    
    def crear_bucket_deficiencia_instituto(self, referencia_bucket_deficiencia):
        bucket_deficiencia_instituto = BucketDeficienciaAdmisionInstituto(
            None, referencia_bucket_deficiencia.id, 0, 0, 0
        );

        return bucket_deficiencia_instituto;
    
    def calcular_aciertos_genero(self, bucket_tema, bucket_tema_instituto, datos_frecuencia):
        # Paso 1: seteamos todo a 0 otra vez, para asegurarnos que en caso el for no encuentre
        #         resultados (lo que sorprendentemente significaria que nadie acerto a la pregunta)
        #         automaticamente determine que hubo 0 aciertos
        bucket_tema_instituto.aciertos = 0
        bucket_tema_instituto.aciertos_masculino = 0
        bucket_tema_instituto.aciertos_femenino = 0

        # Paso 2: Buscamos los literales de respuesta
        frecuencia_aciertos = list(filter(lambda x: x[0] in bucket_tema.preguntas 
            and (x[1] in bucket_tema.literales_correctos), datos_frecuencia))
        
        for frecuencia_acierto in frecuencia_aciertos:
            if frecuencia_acierto[2] == "M":
                bucket_tema_instituto.aciertos_masculino = bucket_tema_instituto.aciertos_masculino + frecuencia_acierto[3]
            else:
                bucket_tema_instituto.aciertos_femenino = bucket_tema_instituto.aciertos_femenino + frecuencia_acierto[3]
        
        bucket_tema_instituto.aciertos = bucket_tema_instituto.aciertos_masculino + bucket_tema_instituto.aciertos_femenino

    def calcular_pregunta_genero(self, institucion_id, id_preguntas):
        sql = """
        SELECT 
            e.genero, 
            COUNT(*) as NUMERO_PREGUNTAS 
        FROM 
            respuesta_examen_admision re
        INNER JOIN 
            estudiantes e
            ON e.NIE = re.numero_aspirante
        WHERE
            re.numero_aspirante IN(
                SELECT 
                    estudiantes.NIE 
                FROM 
                    users
                INNER JOIN 
                    estudiantes
                    ON users.id = estudiantes.user_id
                WHERE 
                    YEAR(users.created_at) = :ANIO_EXAMEN_ADM AND
                    estudiantes.institucion_id = :ID_INSTITUCION
            ) AND
            re.id_pregunta_examen_admision IN :ID_PREGUNTAS
        GROUP BY
            e.genero; 
        """

        params = {
            'ANIO_EXAMEN_ADM': self.examen.anio,
            'ID_INSTITUCION': institucion_id,
            'ID_PREGUNTAS': id_preguntas
        }

        print("PARAMETROS FRECUENCIA PREGUNTAS")
        print(params)

        return self.session.execute(sql, params).fetchall()
    
    def calcular_frecuencia_literales_genero(self, institucion_id, id_preguntas):
        sql = """
        SELECT 
            re.id_pregunta_examen_admision,
            re.id_literal_pregunta, 
            e.genero,    
            COUNT(*) as FRECUENCIA 
        FROM 
            respuesta_examen_admision re
        INNER JOIN 
            estudiantes e
            ON e.NIE = re.numero_aspirante
        WHERE
            re.numero_aspirante IN(
                SELECT 
                    estudiantes.NIE 
                FROM 
                    users
                INNER JOIN 
                    estudiantes
                    ON users.id = estudiantes.user_id
                WHERE 
                    YEAR(users.created_at) = :ANIO_EXAMEN_ADM AND
                    estudiantes.institucion_id = :ID_INSTITUCION
            ) AND
            re.id_pregunta_examen_admision IN :ID_PREGUNTAS
        GROUP BY
            re.id_pregunta_examen_admision,
            re.id_literal_pregunta,
            e.genero
        ORDER BY
            re.id_pregunta_examen_admision ASC,
            re.id_literal_pregunta ASC,
            e.genero ASC;
        """

        params = {
            'ANIO_EXAMEN_ADM': self.examen.anio,
            'ID_INSTITUCION': institucion_id,
            'ID_PREGUNTAS': id_preguntas
        }

        print("PARAMETROS FRECUENCIAS LITERALES")
        print(params)

        return self.session.execute(sql, params).fetchall()