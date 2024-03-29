import queries.db as db
import queries.Municipio as Municipio
#import db
#from Municipio import *


class Departamento:
    def __init__(self, id, nombre,db):
        self.id = id
        self.nombre = nombre
        self.municipios = []
        self.db = db

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
        result = self.db.session.execute(queryString, data)
        self.municipios = []
        for mun in result:
            m = Municipio(mun[0], mun[1], mun[2],self.db)
            self.municipios.append(m)
        #print('Departamento: {0}'.format(self.nombre))
        #print('cantidad de municipios: {0}'.format(len(self.municipios)))

