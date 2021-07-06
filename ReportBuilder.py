from queries import *
from queries import QueryExecutor
from queries.QueryExecutor import ExamenAdmisionQueryExecutor, ExamenPruebaQueryExecutor
import json
class ReportBuilder:
    def obtenerBuckets(tipo, condiciones):
        buckets = []
        if tipo == 'ADMISION':
            data = dict(examenId=condiciones['examenId'])
            bucketString = """
            SELECT
                bta.id,
                GROUP_CONCAT(btad.tema_id) AS tema_id,
                GROUP_CONCAT(t.nombre) AS nombre
            FROM
                bucket_tema_adm AS bta
            INNER JOIN bucket_tema_adm_detalle AS btad
            ON
                bta.id = btad.bucket_tema_adm_id
            INNER JOIN temas AS t
            ON
                t.id = btad.tema_id
            WHERE
                bta.id_examen_admision = :examenId
            GROUP BY
                bta.id
            ORDER BY
                bta.id;
            """
            result = db.session.execute(bucketString, data)
            for tup in result:
                b = Bucket(*tup)
                buckets.append(b)
        elif tipo == 'EXAMEN_PRUEBA':
            data = dict(
                seccionId=condiciones['seccion'], anio=condiciones['anio'])
            bucketString = """
            SELECT
                bte.id,
                GROUP_CONCAT(bted.tema_id) AS tema_id,
                GROUP_CONCAT(t.nombre) AS nombre
            FROM
                bucket_tema_exp AS bte
            INNER JOIN bucket_tema_exp_detalle AS bted
            ON
                bte.id = bted.bucket_tema_exp_id
            INNER JOIN temas AS t
            ON
                t.id = bted.tema_id
            WHERE
                bte.seccion_id = :seccionId AND bte.anio = :anio
            GROUP BY
                bte.id
            ORDER BY
                bte.id;
            """
            result = db.session.execute(bucketString, data)
            for tup in result:
                b = Bucket(*tup)
                buckets.append(b)
        else:
            pass

        return buckets

    def reporteDebilidadesYFortalezasTema(instituciones):
        buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':6})
        reporte = Reporte('reporte 1',instituciones,buckets,'ADMISION')
        reporte.prepararFilas()
        reporte.procesarDatos()
        reporte.generarResumen()
        reporte.calcularTotales()
        return reporte

    def reporteDetalleDebilidades(instituciones):
        buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':6})
        reporte = Reporte('reporte 2',instituciones,buckets,'ADMISION',True)
        reporte.prepararFilas()
        reporte.procesarDatos()
        reporte.generarResumen()
        reporte.calcularTotales()
        return reporte

    def reporteDebilidadesAmbasRondas(instituciones):
        pass

    def reporteRendimientoGlobal(instituciones):
        pass

instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(6,[1,2,3,4,5,6,7,8,9,10,11,12,13,14])
#reporte = ReportBuilder.reporteDebilidadesYFortalezasTema(instituciones)
reporte = ReportBuilder.reporteDetalleDebilidades(instituciones)
print("total: {0}, total_fallos:{1}, total_aciertos: {2}".format(reporte.totales['total_preguntas'],reporte.totales['total_fallos'],reporte.totales['total_aciertos']))
for fila in reporte.filas.values():
    print(fila.deficiencias)
#ReportBuilder.reporteDetalleDebilidades(instituciones)
