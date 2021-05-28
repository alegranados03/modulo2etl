from queries import *

class CommonQueryExecutor:
    def getInstituciones(instituciones):
        institucionesList = []
        data = dict(instIds=tuple(instituciones))
        institucionesString = """SELECT id,nombre,longitud,latitud,tipo_institucion,departamento_id,municipio_id FROM instituciones
            WHERE id IN :instIds ORDER BY id
            """
        result = db.session.execute(institucionesString, data)
        for ins in result:
            inst = Institucion(*ins)
            institucionesList.append(inst)

        return institucionesList

    def getMunicipios(municipios):
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
        result = db.session.execute(municipiosString, data)

        for mun in result:
            m = Municipio(mun[0], mun[1], mun[2])
            municipiosList.append(m)

        return municipiosList

    def getDepartamentos(departamentos):
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
        result = db.session.execute(departamentosString, data)
        for dep in result:
            d = Departamento(*dep)
            departamentosList.append(d)

        return departamentosList


class ExamenAdmisionQueryExecutor:

    def bucketsAdmisionPorInstitucion(examenesAdmision, instituciones):
        institucionesList = CommonQueryExecutor.getInstituciones(instituciones)
        for inst in institucionesList:
            inst.obtenerBucketsAdmision(examenesAdmision)
        return institucionesList

    def bucketsAdmisionPorMunicipio(examenesAdmision, municipios):
        municipiosList = CommonQueryExecutor.getMunicipios(municipios)
        for mun in municipiosList:
            mun.obtenerInstituciones()
            for inst in mun.instituciones:
                inst.obtenerBucketsAdmision(examenesAdmision)
        return municipiosList

    def bucketsAdmisionPorDepartamento(examenesAdmision, departamentos):
        departamentosList = CommonQueryExecutor.getDepartamentos(departamentos)
        for dep in departamentosList:
            dep.obtenerMunicipios()
            for mun in dep.municipios:
                mun.obtenerInstituciones()
                for ins in mun.instituciones:
                    ins.obtenerBucketsAdmision(examenesAdmision)

        return departamentosList

    def bucketsAdmisionPais(examenesAdmision):
        departamentosString = """
            SELECT
                id
            FROM
                departamentos
            ORDER BY
                id
            """
        result = db.session.execute(departamentosString)
        departamentos = [r[0] for r in result]
        pais = Pais()
        pais.departamentos = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(
            examenesAdmision, departamentos)

        return pais


class ExamenPruebaQueryExecutor:

    def bucketsPruebaPorInstitucion(instituciones, secciones, anios):
        institucionesList = CommonQueryExecutor.getInstituciones(instituciones)
        for inst in institucionesList:
            inst.obtenerBucketsExamenPrueba(secciones, anios)
        return institucionesList

    def bucketsPruebaPorMunicipio(municipios, secciones, anios):
        municipiosList = CommonQueryExecutor.getMunicipios(municipios)
        for mun in municipiosList:
            mun.obtenerInstituciones()
            for inst in mun.instituciones:
                inst.obtenerBucketsExamenPrueba(secciones, anios)
        return municipiosList

    def bucketsPruebaPorDepartamento(departamentos, secciones, anios):
        departamentosList = CommonQueryExecutor.getDepartamentos(departamentos)
        for dep in departamentosList:
            dep.obtenerMunicipios()
            for mun in dep.municipios:
                mun.obtenerInstituciones()
                for ins in mun.instituciones:
                    ins.obtenerBucketsExamenPrueba(secciones, anios)

        return departamentosList

    def bucketsPruebaPais(secciones, anios):
        departamentosString = """
            SELECT
                id
            FROM
                departamentos
            ORDER BY
                id
            """
        result = db.session.execute(departamentosString)
        departamentos = [r[0] for r in result]
        pais = Pais()
        pais.departamentos = ExamenPruebaQueryExecutor.bucketsPruebaPorDepartamento(
            departamentos, secciones, anios)

        return pais
