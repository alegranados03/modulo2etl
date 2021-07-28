from queries import *
from queries import QueryExecutor
from queries.QueryExecutor import ExamenAdmisionQueryExecutor, ExamenPruebaQueryExecutor, CommonQueryExecutor

class ReportBuilder:
    def __init__(self,db):
        self.db = db
        self.examenAdmisionQueryExecutor = ExamenAdmisionQueryExecutor(db)
        self.examenPruebaQueryExecutor = ExamenPruebaQueryExecutor(db)
        self.commonQueryExecutor = CommonQueryExecutor(db)

    def obtenerBuckets(self,tipo, condiciones):
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
            result = self.db.session.execute(bucketString, data)
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
            result = self.db.session.execute(bucketString, data)
            for tup in result:
                b = Bucket(*tup)
                buckets.append(b)
        else:
            pass

        return buckets

    def reporteDebilidadesYFortalezasTema(self,filtro,ids,examenId):
        if filtro == 'DEPARTAMENTO':
            instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(examenId,ids)
            departamentos = self.commonQueryExecutor.getDepartamentos(ids)
            nombre = departamentos[0].nombre
        elif filtro == 'MUNICIPIO':
            instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(examenId,ids)
            municipios = self.commonQueryExecutor.getMunicipios(ids)
            nombre = municipios[0].nombre
        elif filtro == 'INSTITUCION':
            instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorInstitucion(examenId,ids)

        
        buckets = self.obtenerBuckets('ADMISION',{'examenId':examenId})
        reporte = Reporte('Reporte de debilidades y fortalezas por tema',instituciones,buckets,'ADMISION')
        try:
            reporte.nombreLugar = nombre
        except:
            pass
        reporte.ejecutarProcesamiento()
        return reporte

    def reporteDetalleDebilidades(self,filtro,ids,examenId):
        if filtro == 'DEPARTAMENTO':
            instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(examenId,ids)
            departamentos = self.commonQueryExecutor.getDepartamentos(ids)
            nombre = departamentos[0].nombre
        elif filtro == 'MUNICIPIO':
            instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(examenId,ids)
            municipios = self.commonQueryExecutor.getMunicipios(ids)
            nombre = municipios[0].nombre
        elif filtro == 'INSTITUCION':
            instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorInstitucion(examenId,ids)


        buckets = self.obtenerBuckets('ADMISION',{'examenId':examenId})
        reporte = Reporte('Reporte de debilidades',instituciones,buckets,'ADMISION',True)
        try:
            reporte.nombreLugar = nombre
        except:
            pass
        reporte.ejecutarProcesamiento()
        return reporte

    def reporteDebilidadesAmbasRondas(self,filtro,ids,anio,seccion):
        data = dict(seccion=seccion, anio=anio)
        result = self.db.session.execute('SELECT id,fase FROM examen_admision WHERE anio = :anio AND id_area_conocimiento = :seccion;',data)
        examenes = []
        for examen in result:
            examenes.append([examen[0],examen[1]])
        
        #examenes.append([6,2])#remover o comentar esta linea luego
        reportes = []
        bucketsList = []
        #creacion de reportes de ambas rondas
        for examen in examenes:
            id,fase = examen[0],examen[1]
            buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':id})
            bucketsList.append(buckets)

            if filtro == 'DEPARTAMENTO':
                instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(id,ids)
                departamentos = self.commonQueryExecutor.getDepartamentos(ids)
                nombre = departamentos[0].nombre
            elif filtro == 'MUNICIPIO':
                instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(id,ids)
                municipios = self.commonQueryExecutor.getMunicipios(ids)
                nombre = municipios[0].nombre
            elif filtro == 'INSTITUCION':
                instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorInstitucion(id,ids)

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


    def reporteRendimientoGlobal(self,filtro,ids,anio,seccion,fase):
        data = dict(seccion=seccion, anio=anio,fase=fase)
        result = self.db.session.execute('SELECT id,fase FROM examen_admision WHERE anio = :anio AND id_area_conocimiento = :seccion AND fase=:fase;',data)
        examenes = []
        for examen in result:
            examenes.append([examen[0],examen[1]])
        
        reportes = []
        bucketsList = []
        #creacion de reportes de ronda de examen de admision
        for examen in examenes:
            id,fase = examen[0],examen[1]
            buckets = ReportBuilder.obtenerBuckets('ADMISION',{'examenId':id})
            bucketsList.append(buckets)
            if filtro == 'DEPARTAMENTO':
                instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(id,ids)
                departamentos = self.commonQueryExecutor.getDepartamentos(ids)
                nombre = departamentos[0].nombre
            elif filtro == 'MUNICIPIO':
                instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorMunicipio(id,ids)
                municipios = self.commonQueryExecutor.getMunicipios(ids)
                nombre = municipios[0].nombre
            elif filtro == 'INSTITUCION':
                instituciones = self.examenAdmisionQueryExecutor.bucketsAdmisionPorInstitucion(id,ids)

            reporte = Reporte('Reporte Examen de Admisión {0} fase {1}'.format(anio,fase),instituciones,buckets,'ADMISION',True)
            try:
                reporte.nombreLugar = nombre
            except:
                pass
            reporte.ejecutarProcesamiento()
            reportes.append(reporte)
        

        buckets1 = bucketsList[0]
        reporte1 = reportes[0]
        
        #reporte examenes de prueba
        bucketsprueba = self.obtenerBuckets('EXAMEN_PRUEBA',{'anio':anio,'seccion':seccion})
        if filtro == 'DEPARTAMENTO':
            instituciones = ExamenPruebaQueryExecutor.bucketsPruebaPorDepartamento(ids,seccion, anio)
            departamentos = self.commonQueryExecutor.getDepartamentos(ids)
            nombre = departamentos[0].nombre
        elif filtro == 'MUNICIPIO':
            instituciones = ExamenPruebaQueryExecutor.bucketsPruebaPorMunicipio(ids,seccion, anio)
            municipios = self.commonQueryExecutor.getMunicipios(ids)
            nombre = municipios[0].nombre
        elif filtro == 'INSTITUCION':
            instituciones = ExamenPruebaQueryExecutor.bucketsAdmisionPorInstitucion(ids,seccion, anio)

        reporteExamenPrueba = Reporte('Reporte examenes de prueba del año {0}'.format(anio),instituciones,bucketsprueba,'EXAMEN_PRUEBA',True)
        try:
            reporteExamenPrueba.nombreLugar = nombre
        except:
            pass

        reporteExamenPrueba.ejecutarProcesamiento()

        
        #comparacion entre ronda y examen de admisin
        reporteComparativoRonda = ReporteComparativo("Reporte comparativo entre examen de primera ronda y examenes de prueba")
        reporteComparativoRonda.inicializarComparadores(buckets1,bucketsprueba)
        reporteComparativoRonda.procesarDatos(reporte1,reporteExamenPrueba)

                
        return {
            'reporte_ronda':reporte1,
            'reporte_examenes_prueba':reporteExamenPrueba,
            'comparativo_exp_ronda': reporteComparativoRonda,
        }