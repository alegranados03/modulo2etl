import queries.db as db
import queries.Deficiencia as Deficiencia
#import db
#from Deficiencia import *


class BucketExamenPrueba:
    def __init__(self, bucket_id, anio, seccion_id, nombre, institucion_id, preguntas, preguntas_masculino, preguntas_femenino, aciertos, aciertos_masculino, aciertos_femenino, fallos, fallos_masculino, fallos_femenino):
        self.id = bucket_id
        self.anio = anio
        self.seccion_id = seccion_id
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

    def obtenerDeficiencias(self):
        data = dict(bteId=self.id, instId=self.institucion_id,seccionId=self.seccion_id)
        queryString = """ 
                    SELECT
                    s.nombre,
                    e.id,
                    e.enunciado,
                    bdei.fallos,
                    bdei.fallos_masculino,
                    bdei.fallos_femenino
                    FROM bucket_tema_exp bte 
                    INNER JOIN bucket_tema_exp_detalle bted ON bted.bucket_tema_exp_id = bte.id
                    INNER JOIN temas t ON bted.tema_id = t.id
                    INNER JOIN secciones s ON s.id = bte.seccion_id
                    INNER JOIN bucket_def_exp bde ON bde.bucket_tema_exp_id = bte.id
                    INNER JOIN etiquetas e ON e.id = bde.etiqueta_id
                    INNER JOIN bucket_def_exp_ins bdei ON bdei.bucket_def_exp_id = bde.id
                    INNER JOIN bucket_tema_exp_ins btei ON bdei.bucket_tema_exp_inst_id = btei.id
                    INNER JOIN instituciones ins ON ins.id = btei.institucion_id
                    INNER JOIN municipios mun ON ins.municipio_id = mun.id
                    INNER JOIN departamentos dep ON dep.id = ins.departamento_id

                    WHERE bte.id = :bteId AND btei.institucion_id = :instId AND bte.seccion_id = :seccionId
                    GROUP BY bte.id,bde.id,bdei.id

                    ORDER BY ins.id,e.id
        """
        result = db.session.execute(queryString, data)
        for deficiencia in result:            
            self.deficiencias.append(Deficiencia(*deficiencia[1:len(deficiencia)]))
        
        #print('Bucket: {0}'.format(self.nombre))
        #print('cantidad de deficiencias: {0}'.format(len(self.deficiencias)))