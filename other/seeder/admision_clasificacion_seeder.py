from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

class Pregunta:
    def __init__(self, id, temas, etiquetas):
        self.id = id
        self.temas = temas
        self.etiquetas = etiquetas

# Paso 0: Variable de configuracion
id_inicio_pregunta = 1
id_final_pregunta = 26
seccion_id = 1
id_examen_admision = 1


suffix = "$"
temas = [
    "Operaciones algebraicas" + suffix,       #0
    "Definicion de funciones" + suffix,       #1
    "evaluacion de funciones" + suffix,       #2
    "Area y Volumen" + suffix,                #3
    "Permutaciones y combinaciones" + suffix, #4
    "Factorizacion" + suffix,                 #5
    "Valor absoluto" + suffix,                #6
    "Conversion de unidades" + suffix,        #7
    "Desigualdades" + suffix,                 #8
    "Probabilidad" + suffix,                  #9
    "ecuaciones cuadraticas" + suffix,        #10
    "Rectas en el plano" + suffix             #11
]

etiquetas = [
    "Etiqueta 1" + suffix,    #0
    "Etiqueta 2" + suffix,    #1
    "Etiqueta 3" + suffix,    #2
    "Etiqueta 4" + suffix,    #3
    "Etiqueta 5" + suffix,    #4
    "Etiqueta 6" + suffix,    #5
]

ids_preguntas = list(range(id_inicio_pregunta, id_final_pregunta+1))

mapeo_examen = [
    Pregunta(ids_preguntas[0], [0], [0,1,2]),        #1
    Pregunta(ids_preguntas[1], [1,2], [0,1,2]),      #2
    Pregunta(ids_preguntas[2], [2], [0,1,2]),        #3
    Pregunta(ids_preguntas[3], [3], [0,1,2]),        #4
    Pregunta(ids_preguntas[4], [4], [0,1,2]),        #5
    Pregunta(ids_preguntas[5], [5], [0,1,2]),        #6
    Pregunta(ids_preguntas[6], [6], [1,2,3]),        #7
    Pregunta(ids_preguntas[7], [7], [0,1,2]),        #8
    Pregunta(ids_preguntas[8], [3], [1,2,3]),        #9
    Pregunta(ids_preguntas[9], [1,2], [1,2,3]),      #10
    Pregunta(ids_preguntas[10], [8], [0,1,2]),       #11
    Pregunta(ids_preguntas[11], [3], [0,0,4]),        #12
    Pregunta(ids_preguntas[12], [9], [0,1,2]),        #13
    Pregunta(ids_preguntas[13], [1,2], [0,1,3]),      #14
    Pregunta(ids_preguntas[14], [5,10], [0,1,2]),     #15
    Pregunta(ids_preguntas[15], [11], [2,1,0]),       #16
    Pregunta(ids_preguntas[16], [4], [4,2,0]),        #17
    Pregunta(ids_preguntas[17], [9], [3,4,5]),        #18
    Pregunta(ids_preguntas[18], [2], [2,3,4]),        #19
    Pregunta(ids_preguntas[19], [0], [4,3,1]),        #20
    Pregunta(ids_preguntas[20], [8], [5,3,4]),        #21
    Pregunta(ids_preguntas[21], [11], [2,0,5]),       #22
    Pregunta(ids_preguntas[22], [2], [2,0,1]),        #23
    Pregunta(ids_preguntas[23], [1,2], [0,1,4]),      #24
    Pregunta(ids_preguntas[24], [2], [3,4,1]),        #25
    Pregunta(ids_preguntas[25], [8], [0,1,2]),        #26
]

# Paso 1: Configuracion de la db
engine = create_engine("mysql+mysqldb://root@localhost/tesisdata")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

# Paso 1: Eliminar referencias de literal_examen_admision
sql = """
    UPDATE literal_examen_admision SET etiqueta_id = NULL WHERE id_pregunta_examen_admision IN(
        SELECT id FROM pregunta_examen_admision WHERE id_examen_admision = :ID_EXAMEN_ADMISION
    )
"""
params = {
    'ID_EXAMEN_ADMISION': id_examen_admision,
}
session.execute(sql, params)
session.commit()

# Paso 2: Insertando temas a ocupar
sql = "DELETE FROM temas WHERE nombre LIKE '%$'"
session.execute(sql, None)
session.commit()


for tema in temas:
    sql = "INSERT INTO temas(nombre, seccion_id) VALUES(:NOMBRE, :SECCION_ID)"
    params = {
        'NOMBRE': tema,
        'SECCION_ID': seccion_id
    }
    print("TEMA AGREGADO CON EXITO")

    session.execute(sql, params)
session.commit()

# Paso 3: Insertando etiquetas a ocupar
sql = "DELETE FROM etiquetas WHERE enunciado LIKE '%$'"
session.execute(sql, None)
session.commit()

for etiqueta in etiquetas:
    sql = "INSERT INTO etiquetas(enunciado, seccion_id) VALUES(:ENUNCIADO, :SECCION_ID)"
    params = {
        'ENUNCIADO': etiqueta,
        'SECCION_ID': seccion_id
    }
    print("ETIQUETA AGREGADO CON EXITO")

    session.execute(sql, params)
session.commit()

# Paso 4: Agregar los temas a las preguntas
sql = """
    DELETE FROM preguntas_examen_admision_temas WHERE id_pregunta_ex_adm IN(
        SELECT id FROM pregunta_examen_admision WHERE id_examen_admision = :ID_EXAMEN_ADMISION
    )"""
params = {
    'ID_EXAMEN_ADMISION': id_examen_admision
}
session.execute(sql, params)
session.commit()

for pregunta in mapeo_examen:
    for id_tema in pregunta.temas:
        sql = """
            INSERT INTO preguntas_examen_admision_temas(id_pregunta_ex_adm, tema_id) 
            SELECT :ID_PREGUNTA, id FROM temas WHERE nombre = :NOMBRE_TEMA
        """
        params = {
            'ID_PREGUNTA': pregunta.id,
            'NOMBRE_TEMA': temas[id_tema]
        }
        
        session.execute(sql, params)
    session.commit()
    print("UNION TEMA PREGUNTA INSERTADO CON EXITO")

# Agregar las etiquetas de deficiencia
for pregunta in mapeo_examen:
    # Paso 1: Obtener ID de literales
    sql = """
        SELECT id FROM literal_examen_admision WHERE id_pregunta_examen_admision = :ID_PREGUNTA 
        AND literal_correcto = 0
        ORDER BY id ASC
    """
    params = {
        'ID_PREGUNTA': pregunta.id
    }

    literales = session.execute(sql, params).fetchall()
    contador = 0

    for literal in literales:
        sql = """
            UPDATE literal_examen_admision SET etiqueta_id = (
                SELECT id FROM etiquetas WHERE enunciado = :NOMBRE_ETIQUETA
            ) 
            WHERE id = :ID_LITERAL
        """
        
        params = {
            'ID_LITERAL': literal[0],
            'NOMBRE_ETIQUETA': etiquetas[pregunta.etiquetas[contador]]
        }

        session.execute(sql, params)
        contador = contador + 1
        print("UNION LITERAL ETIQUETA INSERTADO CON EXITO")
    session.commit()