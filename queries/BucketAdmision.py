import queries.db as db
#import db
class BucketAdmision:
    def __init__(self, bucket_id,id_examen_admision,nombre, institucion_id, preguntas, preguntas_masculino, preguntas_femenino, aciertos,aciertos_masculino, aciertos_femenino, fallos, fallos_masculino, fallos_femenino):
        self.id = bucket_id
        self.id_examen_admision = id_examen_admision
        self.nombre = nombre
        self.institucion_id = institucion_id
        self.preguntas = preguntas
        self.preguntas_masculino = preguntas_masculino
        self.preguntas_femenino = preguntas_femenino
        self.aciertos = aciertos
        self.aciertos_masculino = aciertos_masculino
        self.aciertos_femenino = aciertos_femenino
        self.fallos = fallos
        self.fallos_masculino = fallos_masculino
        self.fallos_femenino = fallos_femenino
        self.deficiencias = []
        self.obtenerDeficiencias()

    def obtenerDeficiencias(self):
        data=dict(btaId=self.id,instId=self.institucion_id)
        queryString = """
        SELECT 
            bta.id as bucket_id,
            e.id,
            e.enunciado,
            bdai.fallos,
            bdai.fallos_masculino,
            bdai.fallos_femenino
            FROM bucket_tema_adm bta 
            INNER JOIN bucket_tema_adm_detalle btad ON btad.bucket_tema_adm_id=bta.id
            INNER JOIN temas t ON t.id = btad.tema_id
            INNER JOIN examen_admision ea ON bta.id_examen_admision = ea.id
            INNER JOIN bucket_deficiencia_adm bda ON bda.bucket_tema_adm_id = bta.id
            INNER JOIN etiquetas e ON bda.etiqueta_id=e.id
            INNER JOIN bucket_deficiencia_adm_instituto bdai ON bdai.bucket_def_adm_id = bda.id
            INNER JOIN bucket_tema_adm_instituto btai ON bdai.bucket_tema_adm_inst_id = btai.id
            INNER JOIN instituciones ins ON btai.institucion_id = ins.id
            INNER JOIN municipios mun ON mun.id = ins.municipio_id
            INNER JOIN departamentos dep ON dep.id = ins.departamento_id
            WHERE bta.id = :btaId AND btai.institucion_id = :instId
            GROUP BY bta.id,bda.id,bdai.id
            ORDER BY ins.id
        """
        result = db.session.execute(queryString, data)
        for deficiencia in result:
            self.deficiencias.append(deficiencia[1:len(deficiencia)])