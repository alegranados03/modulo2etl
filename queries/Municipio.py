import queries.db as db
import queries.Institucion as Institucion
#import db
#from Institucion import *


class Municipio:
    def __init__(self, id, nombre,departamento_id):
        self.id = id
        self.nombre = nombre
        self.departamento_id = departamento_id
        self.instituciones = []

    def obtenerInstituciones(self):
        data = dict(municipioId=self.id)
        queryString = """
        SELECT
            id,
            nombre,
            longitud,
            latitud,
            tipo_institucion,
            departamento_id,
            municipio_id
        FROM
            instituciones
        WHERE
            municipio_id = :municipioId
         """
        result = db.session.execute(queryString, data)
        self.instituciones = []
        for mun in result:
            inst = Institucion(*mun)
            self.instituciones.append(inst)

