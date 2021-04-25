from analyzer import *
import analyzer.constantes as constantes

class BaseBucketCalculation:
    def __init__(self):
        self.buckets_temas = []
    
    def construir_bucket_examen(self, examen, modo):
        # Paso 2: Procedemos a recorrer el examen, en busqueda de temas
        for pregunta in examen.preguntas:
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