import math
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine("mysql+mysqldb://root@localhost/tesis2020_2")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

############################ Clases Model ##########################################
class Literal:
    def __init__(self):
        self.id = -1
        self.id_referencia = -1
        self.literal_correcto= -1

class Pregunta:
    def __init__(self):
        self.id = -1
        self.id_referencia = -1
        self.literales = []

class Examen:
    def __init__(self):
        self.id = -1
        self.preguntas = []

class Estudiante:
    def __init__(self):
        self.nie = -1
        self.genero = "Test"

class Institucion:
    def __init__(self):
        self.id = -1
        self.nombre = "Test"
        self.estudiantes = []

class Respuesta:
    def __init__(self):
        self.id_pregunta = -1
        self.id_referencia_pregunta = -1
        self.id_literal = -1
        self.id_referencia_literal = -1
        self.correcta = -1

class Intento:
    def __init__(self):
        self.nie = -1
        self.respuestas = []
        self.n_preguntas = -1
        self.n_correctas = -1
        self.id_examen_admision = -1


########################## Logica de construccion de objetos ##################################
def construir_examen_admision(id_examen_admision):
    e = Examen()
    e.id = id_examen_admision

    # Paso 1: obteniendo las preguntas
    with engine.connect() as con:
        rs_preguntas = con.execute("SELECT id, id_referencia FROM pregunta_examen_admision WHERE id_examen_admision = " + str(id_examen_admision))

        for pregunta in rs_preguntas:
            p = Pregunta()
            e.preguntas.append(p)
            p.id = pregunta[0]
            p.id_referencia = pregunta[1]

            # Paso 2: Obtenemos los literales de dicha pregunta
            rs_literales = con.execute("SELECT id, id_referencia, literal_correcto FROM literal_examen_admision WHERE id_pregunta_examen_admision = " + str(p.id))

            for literal in rs_literales:
                l = Literal()
                p.literales.append(l)
                l.id = literal[0]
                l.id_referencia = literal[1]
                l.literal_correcto = literal[2]
    
    return e

def construir_instituciones_estudiantes():
    instituciones = []

    # Paso 1: obteniendo las instituciones
    with engine.connect() as con:
        rs_instituciones = con.execute("SELECT id, nombre FROM instituciones")

        for institucion in rs_instituciones:
            i = Institucion()
            instituciones.append(i)
            i.id = institucion[0]
            i.nombre = institucion[1]

            # Paso 2: Obtener estudiantes de dicha institucion
            rs_estudiantes = con.execute("SELECT NIE, genero FROM estudiantes WHERE institucion_id = " + str(i.id))

            for estudiante in rs_estudiantes:
                e = Estudiante()
                i.estudiantes.append(e)
                e.nie = estudiante[0]
                e.genero = estudiante[1]
            
    return instituciones

############################ Funciones basicas de simulacion #######################
def pdf_gamma(x, rate, shape):
    return ((rate**shape)/math.gamma(shape))*(x**(shape - 1))*math.exp(-rate*x)

def rand_dist_gamma(c, a, b, rate, shape):
    not_computed = True
    val = -1
	
    while (not_computed):
        r1 = np.random.uniform()
        r2 = np.random.uniform()
        x = a + (b - a)*r1
		
        if (r2 <= (1.0/c)*pdf_gamma(x, rate, shape)):
            val = x
            not_computed = False
	
    return round(val)

def rand_dist_empirical():
    recta_x_opciones = ["MALO", "MEDIO", "BUENO"]
    p_x_opciones = [0.25, 0.50, 0.25]
    cdf_x_opciones = [0.25, 0.75, 1.00]
	
    r1 = np.random.uniform()
    
    for i in reversed(range(0, len(recta_x_opciones))):
        if (i == 0):
            return recta_x_opciones[i]
        elif (r1 >= cdf_x_opciones[i - 1] and r1 <= cdf_x_opciones[i]):
            return  recta_x_opciones[i]

def rand_generator_by_type(tipo, n_preguntas):
    opciones = ["MALO", "MEDIO", "BUENO"]
	
	# MALO, MEDIO, BUENO
    c_values = [0.095390970631294, 0.07018694790714, 0.055834612780239]
	
	# MALO, MEDIO, BUENO
    rates = [0.24, 0.4, 0.4]
	
	# MALO, MEDIO, BUENO
    shapes = [2.4, 6.0, 9.0]
	
    i = opciones.index(tipo)
    
    return rand_dist_gamma(c_values[i], 0, n_preguntas, rates[i], shapes[i])

def contestar_examen(estudiante, examen, correctas):
    # Paso 1: Obtener lista de ids de cada una de las preguntas del examen
    # supocicion: todo lo que quede en la lista sera considerado malo
    preguntas_malas = [x.id for x in examen.preguntas]
    preguntas_buenas = []

    # Paso 2: En base a la lista de preguntas malas, empiezo a sacar todas las preguntas
    # que aleatoriamente considerare como "buenas"
    for i in range(0, correctas):
        #print("Intentamos hacer pop")
        r1 = np.random.randint(0, len(preguntas_malas))
        #print("Indice de elemento a remover: " + str(r1))
        el = preguntas_malas.pop(r1)
        #print("Elemento removido: " + str(el))
        preguntas_buenas.append(el)
    
    # Paso 3: ahora con ambas listas establecidas, empiezo a crear el intento
    # y llenarlo con las preguntas
    i = Intento()
    i.nie = estudiante.nie
    i.n_preguntas = len(examen.preguntas)
    i.n_correctas = correctas
    i.id_examen_admision = examen.id

    for pregunta in examen.preguntas:
        r = Respuesta()
        i.respuestas.append(r)

        r.id_pregunta = pregunta.id
        r.id_referencia_pregunta = pregunta.id_referencia

        if pregunta.id in preguntas_buenas:
            #print("Encontramos respuesta correcta")
            literal = list(filter(lambda x: x.literal_correcto == 1, pregunta.literales))[0]
            r.id_literal = literal.id
            r.id_referencia_literal = literal.id_referencia
            r.correcta = 1
        else:
            literales = list(filter(lambda x: x.literal_correcto == 0, pregunta.literales))
            r1 = np.random.randint(0, len(literales))
            literal = literales[r1]
            r.id_literal = literal.id
            r.id_referencia_literal = literal.id_referencia
            r.correcta = 0
    
    return i
############################ Logica almacenamiento simulacion #####################
def escribir_intento(intento, archivo):
    for respuesta in intento.respuestas:
        archivo.write("{0};{1};{2}\n".format(intento.nie, respuesta.id_referencia_pregunta, respuesta.id_referencia_literal))

def escribir_puntuacion(nie, preguntas, respuestas, archivo):
    archivo.write("{0};{1};{2}\n".format(nie, preguntas, respuestas))

############################ Logica de almacenamiento en DB #######################
def generar_sql_intento(intento):
    sql = ""

    for respuesta in intento.respuestas:
        sql += "INSERT INTO respuesta_examen_admision(id_examen_admision, numero_aspirante, id_pregunta_examen_admision, id_literal_pregunta, created_at, updated_at) VALUES({0}, {1}, {2}, {3}, NOW(), NOW());".format(
            intento.id_examen_admision,
            intento.nie,
            respuesta.id_pregunta,
            respuesta.id_literal
        )
    
    return sql

def generar_sql_nota(intento):
    sql = "INSERT INTO resumen_examen_admision(numero_aspirante, numero_preguntas, preguntas_correctas, materia, id_examen_admision, created_at, updated_at) VALUES({0}, {1}, {2}, '{3}', {4}, NOW(), NOW())".format(
        intento.nie,
        intento.n_preguntas,
        intento.n_correctas,
        "MATEMATICA",
        intento.id_examen_admision
    )

    return sql

def almacenar_intento_admision(intento):
    sql = generar_sql_intento(intento)

    with engine.connect() as con:
        rs_instituciones = con.execute(sql)

    return True

def almacenar_puntaje_ronda(intento):
    sql = generar_sql_nota(intento)

    with engine.connect() as con:
        rs_instituciones = con.execute(sql)

    return True

############################ Logica de simulacion de examen #######################

# Paso 1: Construir los objetos que representan los examenes de admision de primera y segunda ronda
print("----- CONSTRUYENDO EXAMENES DE ADMISION DESDE DB -----")
examenes = [construir_examen_admision(1), construir_examen_admision(2)]
print("Cargado exitosamente")
print("----- CONSTRUYENDO INSTITUCIONES Y ESTUDIANTES DESDE DB -----")
instituciones = construir_instituciones_estudiantes()
print("Cargado exitosamente")
print("----- CREANDO ARCHIVOS DE ALAMACENAMIENTO DE SIMULACION -----")
intentos_ronda_1 = []
intentos_ronda_2 = []

f_ronda_1 = open("respuestas_ronda_1.csv", "w")
f_ronda_2 = open("respuestas_ronda_2.csv", "w")
f_ronda_1_simple = open("respuestas_ronda_1_simple.csv", "w")
f_ronda_2_simple = open("respuestas_ronda_2_simple.csv", "w")

f_ronda_1.write("NIE;ID_PREGUNTA;ID_LITERAL\n")
f_ronda_2.write("NIE;ID_PREGUNTA;ID_LITERAL\n")
f_ronda_1_simple.write("NIE;PREG;RESP\n")
f_ronda_2_simple.write("NIE;PREG;RESP\n")

print("----- INICIANDO SIMULACION -----")
for instituto in instituciones:
    tipo = rand_dist_empirical()
    print("########## ID_INSTITUCION = " + str(instituto.id) + " TIPO = " + tipo + " NOMBRE = " + instituto.nombre + "##########")

    # Reglas:
    #     - Cada estudiante se le generara resultado para ronda 1
    #     - si el estudiante reprueba, se le generara resultado para ronda 2
    for estudiante in instituto.estudiantes:
        correctas_ronda_1 = rand_generator_by_type(tipo, len(examenes[0].preguntas))
        correctas_ronda_2 = rand_generator_by_type(tipo, len(examenes[1].preguntas))
        
        print("Estudiante NIE =" + str(estudiante.nie) + " RONDA 1 = " + str(correctas_ronda_1))
        if (correctas_ronda_1 < len(examenes[0].preguntas)/2):
            print("Estudiante NIE =" + str(estudiante.nie) + " RONDA 2 = " + str(correctas_ronda_2))

        intento_1 = contestar_examen(estudiante, examenes[0], correctas_ronda_1)
        escribir_intento(intento_1, f_ronda_1)
        escribir_puntuacion(estudiante.nie, len(examenes[0].preguntas), correctas_ronda_1, f_ronda_1_simple)
        intentos_ronda_1.append(intento_1)

        if (correctas_ronda_1 < len(examenes[0].preguntas)/2):
            intento_2 = contestar_examen(estudiante, examenes[1], correctas_ronda_2)
            escribir_intento(intento_2, f_ronda_2)
            escribir_puntuacion(estudiante.nie, len(examenes[1].preguntas), correctas_ronda_2, f_ronda_2_simple)
            intentos_ronda_2.append(intento_2)

print("----- SIMULACION TERMINADA CON EXITO -----")
print("Almacenando datos recolectados en CSV")
f_ronda_1.close()
f_ronda_2.close()
f_ronda_1_simple.close()
f_ronda_2_simple.close()
print("Terminado...")
print("Almacenando datos recolectados en DB")

print("Almacenando resultados primera ronda")
for intento in intentos_ronda_1:
    print("Almacenando ronda 1, NIE={0}".format(intento.nie))
    almacenar_intento_admision(intento)
    almacenar_puntaje_ronda(intento)

print("Almacenando resultados segunda ronda")
for intento in intentos_ronda_2:
    print("Almacenando ronda 2, NIE={0}".format(intento.nie))
    almacenar_intento_admision(intento)
    almacenar_puntaje_ronda(intento)

print("Terminado")