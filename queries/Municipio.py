import queries.db as db
import queries.Institucion as Institucion
#import db
#from Institucion import *


class Municipio:
    def __init__(self, id, nombre, departamento_id,db):
        self.id = id
        self.nombre = nombre
        self.departamento_id = departamento_id
        self.instituciones = []
        self.db = db

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
        
        ORDER BY id
         """
        result = self.db.session.execute(queryString, data)
        self.instituciones = []
        for mun in result:
            inst = Institucion(*mun,self.db)
            self.instituciones.append(inst)
        #print('Municipio: {0}'.format(self.nombre))
        #print('cantidad de instituciones: {0}'.format(len(self.instituciones)))
