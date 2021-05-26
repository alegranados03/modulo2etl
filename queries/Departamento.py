import queries.db as db
import queries.Municipio as Municipio
#import db
#from Municipio import *

class Departamento:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.municipios = []

    def obtenerMunicipios(self):
        data = dict(deptoId=self.id)
        queryString = """
                    SELECT
                        id,
                        nombre,
                        departamento_id
                    FROM
                        municipios
                    WHERE
                        departamento_id = :deptoId
                    """
        result = db.session.execute(queryString, data)
        self.municipios = []
        for mun in result:
            m = Municipio(mun[0],mun[1],mun[2])
            self.municipios.append(m)

d = Departamento(10,'San Salvador')
d.obtenerMunicipios()
