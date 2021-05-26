from queries import *


class ExamenAdmisionQueryExecutor:
    def __init__(self):
        pass

    def bucketsAdmisionPorInstitucion(examenesAdmision, instituciones):
        institucionesList = []
        data = dict(instIds=tuple(instituciones))
        institucionesString = """SELECT id,nombre,longitud,latitud,tipo_institucion,departamento_id,municipio_id FROM instituciones
        WHERE id IN :instIds
        """
        result = db.session.execute(institucionesString, data)
        for ins in result:
            inst = Institucion(*ins)
            inst.obtenerBucketsAdmision(examenesAdmision)
            institucionesList.append(inst)

        return institucionesList

    def bucketsAdmisionPorMunicipio(examenesAdmision, municipios):
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
        """
        result = db.session.execute(municipiosString, data)

        for mun in result:
            m = Municipio(mun[0], mun[1], mun[2])
            m.obtenerInstituciones()
            for inst in m.instituciones:
                inst.obtenerBucketsAdmision(examenesAdmision)
            municipiosList.append(m)

        return municipiosList

    def bucketsAdmisionPorDepartamento(examenesAdmision, departamentos):
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
        """
        result = db.session.execute(departamentosString, data)
        for dep in result:
            d = Departamento(*dep)
            d.obtenerMunicipios()
            for mun in d.municipios:
                mun.obtenerInstituciones()
                for ins in mun.instituciones:
                    ins.obtenerBucketsAdmision(examenesAdmision)
            departamentosList.append(d)

        return departamentosList

    def bucketsAdmisionPais(examenesAdmision):
        departamentosString = """
            SELECT
                id
            FROM
                departamentos
            """
        result = db.session.execute(departamentosString)
        departamentos = [r[0] for r in result]
        pais = Pais()
        pais.departamentos = ExamenAdmisionQueryExecutor.bucketsAdmisionPorDepartamento(
            examenesAdmision, departamentos)

        return pais
