import queries.db as db
import queries.BucketAdmision as Bucket
#from Bucket import *
#import db

class Institucion:
    def __init__(self, id, nombre, longitud, latitud, tipo_institucion,departamento_id,municipio_id):
        self.id = id
        self.nombre = nombre
        self.longitud = longitud
        self.latitud = latitud
        self.tipo_institucion = tipo_institucion
        self.departamento_id = departamento_id
        self.municipio_id = municipio_id
        self.bucketsAdmision = []
        self.bucketsExamenesPrueba = []

    def obtenerBucketsAdmision(self, examenes):
        data = dict(examenIds=tuple(examenes),institucionId = self.id)
        queryString = """
             SELECT
                bta.id,
                bta.id_examen_admision,
                GROUP_CONCAT(t.nombre) AS nombre_bucket,
                btai.institucion_id,
                btai.preguntas,
                btai.preguntas_masculino,
                btai.preguntas_femenino,
                btai.aciertos,
                btai.aciertos_masculino,
                btai.aciertos_femenino,
                btai.fallos,
                btai.fallos_masculino,
                btai.fallos_femenino
            FROM
                bucket_tema_adm bta
            INNER JOIN bucket_tema_adm_detalle btad ON
                bta.id = btad.bucket_tema_adm_id
            INNER JOIN bucket_tema_adm_instituto btai ON
                btai.bucket_tema_adm_id = bta.id
            INNER JOIN temas t ON
                t.id = btad.tema_id
            WHERE
                bta.id_examen_admision IN :examenIds AND btai.institucion_id = :institucionId
            GROUP BY
                bta.id
            ORDER BY 
                bta.id
                """
        result = db.session.execute(queryString, data)
        self.buckets=[]
        for tup in result:
            b = Bucket(*tup)
            self.bucketsAdmision.append(b)

        for bucket in self.bucketsAdmision:
            bucket.obtenerDeficiencias()



