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

    def reporteDebilidadesYFortalezasTema(filtro,ids,examenId):
        if filtro == 'DEPARTAMENTO':
            instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(examenId,ids)
        elif filtro == 'MUNICIPIO':
            instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(examenId,ids)
        elif filtro == 'INSTITUCION':
            instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(examenId,ids)
        
        buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':examenId})
        reporte = Reporte('Reporte de debilidades y fortalezas por tema',instituciones,buckets,'ADMISION')
        reporte.ejecutarProcesamiento()
        return reporte

    def reporteDetalleDebilidades(filtro,ids,examenId):
        if filtro == 'DEPARTAMENTO':
            instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(examenId,ids)
        elif filtro == 'MUNICIPIO':
            instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(examenId,ids)
        elif filtro == 'INSTITUCION':
            instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(examenId,ids)

        buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':examenId})
        reporte = Reporte('Reporte de debilidades',instituciones,buckets,'ADMISION',True)
        reporte.ejecutarProcesamiento()
        return reporte

    def reporteDebilidadesAmbasRondas(filtro,ids,anio,seccion):
        data = dict(seccion=seccion, anio=anio)
        result = db.session.execute('SELECT id,fase FROM examen_admision WHERE anio = :anio AND id_area_conocimiento = :seccion;',data)
        examenes = []
        for examen in result:
            examenes.append([examen[0],examen[1]])
        
        examenes.append([6,2])#remover o comentar esta linea luego
        reportes = []
        bucketsList = []
        #creacion de reportes de ambas rondas
        for examen in examenes:
            id,fase = examen[0],examen[1]
            buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':id})
            bucketsList.append(buckets)

            if filtro == 'DEPARTAMENTO':
                instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(id,ids)
            elif filtro == 'MUNICIPIO':
                instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(id,ids)
            elif filtro == 'INSTITUCION':
                instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(id,ids)

            reporte = Reporte('Reporte examen de admisión del año {0} fase {1}'.format(anio,fase),instituciones,buckets,'ADMISION',True)
            reporte.ejecutarProcesamiento()
            reportes.append(reporte)
        

        buckets1, buckets2 = bucketsList[0], bucketsList[1]
        reporte1, reporte2 = reportes[0],reportes[1]

        reporteComparativo = ReporteComparativo("reporte comparativo")
        reporteComparativo.inicializarComparadores(buckets1,buckets2)
        reporteComparativo.procesarDatos(reporte1,reporte2)
        
        return {
            'reporte_examen_admision_1':reporte1,
            'reporte_examen_admision_2':reporte2,
            'reporte_comparativo': reporteComparativo
        }


    def reporteRendimientoGlobal(filtro,ids,anio,seccion):
        data = dict(seccion=seccion, anio=anio)
        result = db.session.execute('SELECT id,fase FROM examen_admision WHERE anio = :anio AND id_area_conocimiento = :seccion;',data)
        examenes = []
        for examen in result:
            examenes.append([examen[0],examen[1]])
        
        examenes.append([6,2])#remover o comentar esta linea luego
        reportes = []
        bucketsList = []
        #creacion de reportes de ambas rondas
        for examen in examenes:
            id,fase = examen[0],examen[1]
            buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':id})
            bucketsList.append(buckets)
            if filtro == 'DEPARTAMENTO':
                instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(id,ids)
            elif filtro == 'MUNICIPIO':
                instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(id,ids)
            elif filtro == 'INSTITUCION':
                instituciones = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(id,ids)

            reporte = Reporte('Reporte EXAMEN DE ADMISION {0} fase {1}'.format(anio,fase),instituciones,buckets,'ADMISION',True)
            reporte.ejecutarProcesamiento()
            reportes.append(reporte)
        

        buckets1, buckets2 = bucketsList[0], bucketsList[1]
        reporte1, reporte2 = reportes[0],reportes[1]
        
        #reporte examenes de prueba
        bucketsprueba = ReportBuilder.obtenerBuckets('EXAMEN_PRUEBA',{'anio':anio,'seccion':seccion})
        if filtro == 'DEPARTAMENTO':
            instituciones = ExamenPruebaQueryExecutor.bucketsPruebaPorDepartamento(ids,seccion, anio)
        elif filtro == 'MUNICIPIO':
            instituciones = ExamenPruebaQueryExecutor.bucketsPruebaPorMunicipio(ids,seccion, anio)
        elif filtro == 'INSTITUCION':
            instituciones = ExamenPruebaQueryExecutor.bucketsPruebaPorDepartamento(ids,seccion, anio)

        reporteExamenPrueba = Reporte('Reporte examenes de prueba del año {0}'.format(anio),instituciones,bucketsprueba,'EXAMEN_PRUEBA',True)
        reporteExamenPrueba.ejecutarProcesamiento()

        
        #comparacion entre rondas
        reporteComparativoRonda1 = ReporteComparativo("Reporte comparativo entre examen de primera ronda y examenes de prueba")
        reporteComparativoRonda1.inicializarComparadores(buckets1,bucketsprueba)
        reporteComparativoRonda1.procesarDatos(reporte1,reporteExamenPrueba)


        reporteComparativoRonda2 = ReporteComparativo("Reporte comparativo entre examen de segunda ronda y examenes de prueba")
        reporteComparativoRonda2.inicializarComparadores(buckets2,bucketsprueba)
        reporteComparativoRonda2.procesarDatos(reporte2,reporteExamenPrueba)
        
        
        return {
            'reporte_primera_ronda':reporte1,
            'reporte_segunda_ronda':reporte2,
            'reporte_examenes_prueba':reporteExamenPrueba,
            'comparativo_exp_primera_ronda': reporteComparativoRonda1,
            'comparativo_exp_segunda_ronda': reporteComparativoRonda2
        }



#reporte = ReportBuilder.reporteRendimientoGlobal('DEPARTAMENTO',[1,2,3,4,5,6,7,8,9,10,11,12,13,14],2021,1)