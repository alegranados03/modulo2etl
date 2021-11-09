from queries import *

class CommonQueryExecutor:
    def __init__(self,db):
        self.db = db

    def getInstituciones(self,instituciones):
        institucionesList = []
        data = dict(instIds=tuple(instituciones))
        institucionesString = """SELECT id,nombre,longitud,latitud,tipo_institucion,departamento_id,municipio_id FROM instituciones
            WHERE id IN :instIds ORDER BY id
            """
        result = self.db.session.execute(institucionesString, data)
        for ins in result:
            inst = Institucion(*ins,self.db)
            institucionesList.append(inst)

        return institucionesList

    def getMunicipios(self,municipios):
        municipiosList = []
        data = dict(municipioIds=tuple(municipios))
        municipiosString = """
            SELECT
                id,
                nombre,
                departamento_id
            FROM
                municipios
            WHERE
                id IN :municipioIds
            ORDER BY
                id
        """
        result = self.db.session.execute(municipiosString, data)

        for mun in result:
            m = Municipio(mun[0], mun[1], mun[2],self.db)
            municipiosList.append(m)

        return municipiosList

    def getDepartamentos(self,departamentos):
        departamentosList = []
        data = dict(deptoIds=tuple(departamentos))
        departamentosString = """
        SELECT
            id,
            nombre
        FROM
            departamentos
        WHERE
            id IN :deptoIds
        ORDER BY
            id
        """
        result = self.db.session.execute(departamentosString, data)
        for dep in result:
            d = Departamento(*dep,self.db)
            departamentosList.append(d)

        return departamentosList


class ExamenAdmisionQueryExecutor:
    def __init__(self,db):
        self.db = db
        self.commonQueryExecutor = CommonQueryExecutor(self.db)
        
    def bucketsAdmisionPorInstitucion(self,examenAdmision, instituciones):
        institucionesList = self.commonQueryExecutor.getInstituciones(instituciones)
        for inst in institucionesList:
            inst.obtenerBucketsAdmision(examenAdmision)
        return institucionesList

    def bucketsAdmisionPorMunicipio(self,examenAdmision, municipios):
        municipiosList = self.commonQueryExecutor.getMunicipios(municipios)
        instituciones = []
        for mun in municipiosList:
            mun.obtenerInstituciones()
            for inst in mun.instituciones:
                inst.obtenerBucketsAdmision(examenAdmision)
                instituciones.append(inst)
        return instituciones

    def bucketsAdmisionPorDepartamento(self,examenAdmision, departamentos):
        departamentosList = self.commonQueryExecutor.getDepartamentos(departamentos)
        instituciones=[]
        for dep in departamentosList:
            dep.obtenerMunicipios()
            for mun in dep.municipios:
                mun.obtenerInstituciones()
                for ins in mun.instituciones:
                    ins.obtenerBucketsAdmision(examenAdmision)
                    instituciones.append(ins)

        return instituciones

    # def bucketsAdmisionPais(self,examenAdmision):
    #     departamentosString = """
    #         SELECT
    #             id
    #         FROM
    #             departamentos
    #         ORDER BY
    #             id
    #         """
    #     result = self.db.session.execute(departamentosString)
    #     departamentos = [r[0] for r in result]
    #     pais = Pais()
    #     pais.departamentos = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(
    #         examenAdmision, departamentos)

    #     return pais


class ExamenPruebaQueryExecutor:
    def __init__(self,db):
        self.db = db
        self.commonQueryExecutor = CommonQueryExecutor(self.db)

    def bucketsPruebaPorInstitucion(self,instituciones, seccion, anio):
        institucionesList = self.commonQueryExecutor.getInstituciones(instituciones)
        for inst in institucionesList:
            inst.obtenerBucketsExamenPrueba(seccion, anio)
        return institucionesList

    def bucketsPruebaPorMunicipio(self,municipios, seccion, anio):
        municipiosList = self.commonQueryExecutor.getMunicipios(municipios)
        instituciones=[]
        for mun in municipiosList:
            mun.obtenerInstituciones()
            for inst in mun.instituciones:
                inst.obtenerBucketsExamenPrueba(seccion, anio)
                instituciones.append(inst)
        return instituciones

    def bucketsPruebaPorDepartamento(self,departamentos, seccion, anio):
        departamentosList = self.commonQueryExecutor.getDepartamentos(departamentos)
        instituciones = []
        for dep in departamentosList:
            dep.obtenerMunicipios()
            for mun in dep.municipios:
                mun.obtenerInstituciones()
                for ins in mun.instituciones:
                    ins.obtenerBucketsExamenPrueba(seccion, anio)
                    instituciones.append(ins)


        return instituciones

    # def bucketsPruebaPais(seccion, anio):
    #     departamentosString = """
    #         SELECT
    #             id
    #         FROM
    #             departamentos
    #         ORDER BY
    #             id
    #         """
    #     result = db.session.execute(departamentosString)
    #     departamentos = [r[0] for r in result]
    #     pais = Pais()
    #     pais.departamentos = ExamenPruebaQueryExecutor.bucketsPruebaPorDepartamento(
    #         departamentos, seccion, anio)

    #     return pais
