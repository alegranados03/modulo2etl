from analyzer import *
import analyzer.constantes as constantes

class BaseBucketCalculation:
    def __init__(self):
        self.buckets_temas = []
    
    def construir_bucket_examen(self, examen, modo, seccion_id=-1):
        # Paso 2: Procedemos a recorrer el examen, en busqueda de temas
        for pregunta in examen.preguntas:
            # Paso 2.1: Para los calculos de examenes de prueba, nada mas
            #           tomar en cuenta las preguntas cuyo seccion_id sea el que
            #           se esta analizando, como tambien que el tipo de pregunta
            #           sea con respuesta unica (este algoritmo no soporta respuestas multiples)
            if modo == constantes.MODO_EXAMENES_PRUEBA:
                if pregunta.seccion_id != seccion_id and seccion_id != -1:
                    print("Saltandose la pregunta con ID=" + str(pregunta.id))
                    print("Seccion a buscar=" + str(seccion_id))
                    print("Seccion encontrada=" + str(pregunta.seccion_id))
                    continue
                
                if pregunta.tipo_pregunta != constantes.RESPUESTA_PREGUNTA_UNICA:
                    print("Saltandose la pregunta con ID=" + str(pregunta.id))
                    print("pregunta no es de respuesta unica")
                    continue

            bucket = self.obtener_bucket_tema(pregunta)

            # Paso 3: Si no encontramos un bucket, lo creamos, y anexamos
            #         la info de la pregunta
            if bucket is None:
                bucket = self.crear_bucket_tema(pregunta)
            else:
                self.anexar_pregunta_bucket(bucket, pregunta)
            
            
            for literal in list(filter(lambda x: x.etiqueta is not None, pregunta.respuestas)):
                # Paso 4: Procedemos a buscar el bucket de deficiencia, si no lo
                #         encontramos, y anexamos la info del literal
                bucket_deficiencia = self.obtener_bucket_deficiencia(bucket, literal)

                if bucket_deficiencia is None:
                    bucket_deficiencia = self.crear_bucket_deficiencia(bucket, literal)
                else:
                    self.anexar_literal_bucket(bucket_deficiencia, literal)
            
            for literal in list(filter(lambda x: x.etiqueta is None, pregunta.respuestas)):
                # Paso 5: Ya calculamos todos los literales de la pregunta que eran deficiencia
                #         ahora procedemos a guardar el literal de pregunta que era el correcto
                if (literal.id not in bucket.literales_correctos):
                    bucket.literales_correctos.append(literal.id)
        
        #self.imprimir_buckets_temas()
    
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
        bucket.temas_obj = pregunta.temas
        bucket.preguntas.append(pregunta.id)

        try:
            bucket.seccion = pregunta.seccion
        except:
            print("Seccion no encontrada, saltandose validacion")

        self.buckets_temas.append(bucket)
        return bucket
    
    def anexar_pregunta_bucket(self, bucket, pregunta):
        if (pregunta.id not in bucket.preguntas):
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
        bucket_deficiencia.etiqueta_obj = literal.etiqueta
        bucket_deficiencia.literales.append(literal.id)
        bucket_tema.buckets_deficiencias.append(bucket_deficiencia)
    
    def anexar_literal_bucket(self, bucket_deficiencia, literal):
        if (literal.id not in bucket_deficiencia.literales):
            bucket_deficiencia.literales.append(literal.id)
    
    '''
        DEBUGGER FUNCTIONS
    '''
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