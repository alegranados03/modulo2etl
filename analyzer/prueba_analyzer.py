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

class BasePruebaAnalyzer(threading.Thread, BaseBucketCalculation, AnalysisProcess):
    def __init__(self, anio, seccion_id, id_proceso_analisis):
        threading.Thread.__init__(self)
        BaseBucketCalculation.__init__(self)
        AnalysisProcess.__init__(self, id_proceso_analisis)

        self.anio = anio
        self.seccion_id = seccion_id
        self.examenes = None
        self.ids_examenes = None
    
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
        for bucket_tema in self.buckets_temas:
            # Paso 2: Agregando informacion basica del tema
            bucket = BucketTemaExamenPrueba(self.anio, self.seccion_id)
            bucket.temas = self.session.query(Tema).filter(Tema.id.in_(bucket_tema.temas)).all()

            # Paso 3: Agregando buckets de deficiencia
            bucket.deficiencias = []
            for bucket_deficiencia in bucket_tema.buckets_deficiencias:
                bucket2 = BucketDeficienciaExamenPrueba(None, bucket_deficiencia.deficiencia)
                bucket.deficiencias.append(bucket2)
            
            bucket_tema.referencia_bucket_tema = bucket
            self.session.add(bucket)
        
        self.session.commit()
    
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
    def __init__(self, anio, id_area_conocimiento, id_proceso_analisis):
        BasePruebaAnalyzer.__init__(self, anio, id_area_conocimiento, id_proceso_analisis)
    
    def run(self):
        # Paso 0: TODO: crear validaciones previas antes de ejecutar analyzer

        # Paso 1: Inicializar el proceso de analisis y cambiar su estado
        self.inicializar_proceso_analisis()

        # Paso 1.2: Eliminar rastros de cualquier calculo realizado previamente
        self.eliminar_analisis_previo()

        # Paso 2: Obtener los examenes que aplican para este analisis
        self.calcular_id_examenes_prueba()
        self.obtener_examenes_prueba()
        
        # Paso 3: Construir buckets y sus relaciones
        self.construir_buckets()

        # Paso 4: Construir los modelos ORM del calculo de tuplas de temas
        #         y las etiquetas de deficiencia asociadas a dichas tuplas
        self.almacenar_buckets()

        # Paso 5: Procedemos a calcular las frecuencias a nivel de institucion
        #         en base a genero
        self.calcular_frecuencias_institucion_genero()

        # Paso 6: Terminando correctamente el analisis, reflejar que el proceso
        #         ha sido terminado exitosamente
        self.cambiar_estado("FINALIZADO")
        self.actualizar_progreso(1.0)
    
    def eliminar_analisis_previo(self):
        sql = """
            DELETE FROM bucket_tema_exp WHERE ANIO = :ANIO AND seccion_id = :SECCION_ID
        """
        params = {
            'ANIO': self.anio,
            'SECCION_ID': self.seccion_id
        }
        self.session.execute(sql, params)

    
    def calcular_frecuencias_institucion_genero(self):
        print("EMPEZAMOS EL CALCULO DE FRECUENCIAS")
        # Paso 1: Obtenemos todas las instituciones que vamos a ocupar para calcular
        instituciones = self.session.query(Institucion)

        # Paso 2: Iteramos cada una de las instituciones y empezamos el calculo
        for institucion in instituciones:
            print("PROCEDEMOS A CALCULAR EL INSTITUTO CON ID=" + str(institucion.id))

            # Paso 2.1: Calculamos los intentos de los estudiantes de este instituto, a tomar
            #           en cuenta
            self.ids_intentos = self.calcular_ids_itentos(institucion.id, self.ids_examenes)

            # Paso 3: Por cada institucion, tenemos que calcular todos los buckets de temas
            #         y sus respectivas deficiencias
            for bucket_tema in self.buckets_temas:
                print("------------------------------------------------")
                print("CALCULANDO LA FRECUENCIA PARA LOS BUCKETS:")
                print(bucket_tema.temas)

                # Paso 4: Creamos el bucket de tema para la institucion, y lo llenamos con la
                #         data inicial (numero de preguntas por genero), como tambien calculamos
                #         los intentos por estudiante a tomar en cuenta en el calculo
                bucket_tema_instituto = self.crear_bucket_tema_instituto(institucion, bucket_tema)

                # Paso 5: Procedemos a calcular las frecuencias (por genero) de cada uno de lo literales
                #         de las preguntas involugradas en este bucket
                datos_frecuencia = self.calcular_frecuencia_literales_genero(institucion.id, bucket_tema.preguntas, self.ids_intentos)

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

            self.instituciones_procesadas = self.instituciones_procesadas + 1
            self.actualizar_progreso()
            self.session.commit()
    
    def crear_bucket_tema_instituto(self, institucion, bucket_tema):
        # Paso 1: Creamos el bucket de instituto, con datos por defecto a 0
        bucket_tema_instituto = BucketTemaPruebaInstituto(
            bucket_tema.referencia_bucket_tema.id,
            institucion.id,
            0, 0, 0, 0, 0, 0, 0, 0, 0
        )

        # Paso 2: Obtenemos los datos generales de numero de preguntas, y lo anexamos al bucket
        #         de instituto, los fallos y aciertos los iremos calculando mientras vayamos
        #         iterando las etiquetas de deficiencia
        datos_generales = self.calcular_pregunta_genero(institucion.id, bucket_tema.preguntas, self.ids_intentos)
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
        bucket_deficiencia_instituto = BucketDeficienciaPruebaInstituto(
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
    
    '''
        FUNCIONES DE RETORNO SQL
    '''
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
    
    def calcular_ids_itentos(self, institucion_id, id_examenes):
        sql = """
        SELECT 
            i1.examen_id,
            i1.user_id,
            nis1.seccion_id,
            nis1.nota,
            i1.id AS intento_id
        FROM 
            nota_intento_seccion nis1
        INNER JOIN
            intentos i1
            ON nis1.intento_id = i1.id
        INNER JOIN
            (
                SELECT 
                    i.examen_id, 
                    i.user_id, 
                    nis.seccion_id,
                    MAX(nis.nota) as nota_maxima
                FROM 
                    nota_intento_seccion nis
                INNER JOIN 
                    intentos i
                    ON nis.intento_id = i.id
                INNER JOIN
                    estudiantes e
                    ON i.user_id = e.user_id
                WHERE
                    YEAR(i.tiempo_finalizacion_real) = :ANIO_EXAMEN AND
                    nis.seccion_id = :ID_SECCION AND
                    e.institucion_id = :ID_INSTITUCION AND
                    i.examen_id IN :ID_EXAMENES
                GROUP BY
                    i.examen_id, i.user_id, nis.seccion_id
            ) resultado
            ON
            i1.examen_id = resultado.examen_id AND
            i1.user_id = resultado.user_id AND
            nis1.seccion_id = resultado.seccion_id AND
            nis1.nota = resultado.nota_maxima
        """
    
        params = {
            'ANIO_EXAMEN': self.anio,
            'ID_SECCION': self.seccion_id,
            'ID_INSTITUCION': institucion_id,
            'ID_EXAMENES': id_examenes
        }

        resultados = self.session.execute(sql, params).fetchall()
        return [intento[4] for intento in resultados]
    
    def calcular_pregunta_genero(self, institucion_id, id_preguntas, id_intentos):
        sql = """
        SELECT 
            e.genero, 
            COUNT(*) as NUMERO_PREGUNTAS
        FROM 
            intentos_respuestas ir
        INNER JOIN 
            intentos i
            ON i.id = ir.intento_id
        INNER JOIN
            estudiantes e
            ON e.user_id = i.user_id
        WHERE
            ir.intento_id IN :ID_INTENTOS AND
            ir.pregunta_id IN :ID_PREGUNTAS AND
            e.institucion_id = :ID_INSTITUCION
        GROUP BY
            e.genero; 
        """

        # NOTA: Se ocupa el operador ternario con la lista None para evitar
        #       errores de sintaxis por parte de SQLAlchemy en la construccion
        #       de la query cuando se detecta que no hay intentos que evaluar
        params = {
            'ID_INTENTOS': [None] if len(id_intentos) == 0 else id_intentos,
            'ID_INSTITUCION': institucion_id,
            'ID_PREGUNTAS': id_preguntas
        }

        print("PARAMETROS FRECUENCIA PREGUNTAS")
        print(params)

        return self.session.execute(sql, params).fetchall()
    
    def calcular_frecuencia_literales_genero(self, institucion_id, id_preguntas, id_intentos):
        sql = """
        SELECT 
            ir.pregunta_id,
            ir.respuesta_id,
            e.genero, 
            COUNT(*) as FRECUENCIA
        FROM 
            intentos_respuestas ir
        INNER JOIN 
            intentos i
            ON i.id = ir.intento_id
        INNER JOIN
            estudiantes e
            ON e.user_id = i.user_id
        WHERE
            ir.intento_id IN :ID_INTENTOS AND
            ir.pregunta_id IN :ID_PREGUNTAS AND
            e.institucion_id = :ID_INSTITUCION
        GROUP BY
            ir.pregunta_id,
            ir.respuesta_id,
            e.genero;
        """

        # NOTA: Se ocupa el operador ternario con la lista None para evitar
        #       errores de sintaxis por parte de SQLAlchemy en la construccion
        #       de la query cuando se detecta que no hay intentos que evaluar
        params = {
            'ID_INTENTOS': [None] if len(id_intentos) == 0 else id_intentos,
            'ID_INSTITUCION': institucion_id,
            'ID_PREGUNTAS': id_preguntas
        }

        print("PARAMETROS FRECUENCIA LITERALES")
        print(params)

        return self.session.execute(sql, params).fetchall()