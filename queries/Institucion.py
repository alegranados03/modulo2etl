import queries.db as db
import queries.BucketAdmision as BucketAdmision
import queries.BucketExamenPrueba as BucketExamenPrueba
#from BucketAdmision import *
#from BucketExamenPrueba import *
#import db

class Institucion:
    def __init__(self, id, nombre, longitud, latitud, tipo_institucion, departamento_id, municipio_id,db):
        self.id = id
        self.nombre = nombre
        self.longitud = longitud
        self.latitud = latitud
        self.tipo_institucion = tipo_institucion
        self.departamento_id = departamento_id
        self.municipio_id = municipio_id
        self.bucketsAdmision = []
        self.bucketsExamenesPrueba = []
        self.db = db

    def obtenerBucketsAdmision(self, examen):
        data = dict(examenId=examen, institucionId=self.id)
        queryString = """
             SELECT
                bta.id,
                bta.id_examen_admision,
                GROUP_CONCAT(btad.tema_id) as tema_id,
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
                bta.id_examen_admision = :examenId AND btai.institucion_id = :institucionId
            GROUP BY
                bta.id,
                btai.institucion_id
            ORDER BY 
                bta.id
                """
        result = self.db.session.execute(queryString, data)
        self.buckets = []
        
        #print('Institucion: {0} id:{1}'.format(self.nombre,self.id))
        for tup in result:
            b = BucketAdmision(*tup, self.db)
            self.bucketsAdmision.append(b)
        
        for bucket in self.bucketsAdmision:
            bucket.obtenerDeficiencias()    
        
    

    def obtenerBucketsExamenPrueba(self, seccion, anio):
        data = dict(seccionId=seccion,
                    anio=anio, institucionId=self.id)
        queryString = """
                        SELECT
                            bte.id AS bucket_tema_exp_id,
                            bte.anio,
                            bte.seccion_id,
                            GROUP_CONCAT(bted.tema_id) as tema_id,
                            GROUP_CONCAT(t.nombre) AS nombre_tema,
                            btei.institucion_id,
                            btei.preguntas,
                            btei.preguntas_masculino,
                            btei.preguntas_femenino,
                            btei.aciertos,
                            btei.aciertos_masculino,
                            btei.aciertos_femenino,
                            btei.fallos,
                            btei.fallos_masculino,
                            btei.fallos_femenino
                        FROM
                            bucket_tema_exp AS bte
                        INNER JOIN bucket_tema_exp_detalle bted ON
                            bte.id = bted.bucket_tema_exp_id
                        INNER JOIN temas t ON
                            bted.tema_id = t.id
                        INNER JOIN bucket_tema_exp_ins btei ON
                            btei.bucket_tema_exp_id = bte.id
                        INNER JOIN instituciones ins ON
                            ins.id = btei.institucion_id
                        INNER JOIN municipios mun ON
                            mun.id = ins.municipio_id
                        INNER JOIN departamentos dep ON
                            dep.id = ins.departamento_id
                        WHERE
                         bte.seccion_id = :seccionId AND bte.anio = :anio AND btei.institucion_id = :institucionId
                        GROUP BY
                            bte.id,
                            btei.institucion_id
                        ORDER BY
                            bte.id ASC,
                            btei.institucion_id ASC
                """
        result = self.db.session.execute(queryString, data)
        for tup in result:
            b = BucketExamenPrueba(*tup, self.db)
            self.bucketsExamenesPrueba.append(b)
        for bucket in self.bucketsExamenesPrueba:
              b = bucket
              #print('bucket: {0}, institucion:{1}'.format(b.nombre, b.institucion_id))
              bucket.obtenerDeficiencias()

