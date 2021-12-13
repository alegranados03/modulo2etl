import random


# Seeder basico para crear respuesta de examenes
class Examen:
    def __init__(self):
        self.preguntas = []

class Pregunta:
    def __init__(self):
        self.id_pregunta = -1
        self.texto_pregunta = ""
        self.literales = []

class Literal:
    def __init__(self):
        self.id_literal = -1
        self.texto_literal = ""
        self.correcto = ""

# Parametros del seeder
nombre_archivo_pregunta = "DataSetPreguntas.csv"
nombre_archivo_literal = "DataSetLiterales.csv"
numero_estudiantes = 1000

columna_id_pregunta = 0
columna_texto_pregunta = 1

columna_id_literal = 0
columna_referencia_pregunta = 1
columna_literal_correcto = 2
columna_texto_literal = 3


# --------------- PROCESAMIENTO DE DATOS ---------------------------

# Paso 0: Creando objetos basicos
examen = Examen()

# Paso 1: Abriendo los archivos
f_pregunta = open(nombre_archivo_pregunta, encoding="utf-8")
f_literal = open(nombre_archivo_literal, encoding="utf-8")

# Paso 2: Leyendo y procesando preguntas
print("Procesando preguntas")
line = f_pregunta.readline()
line = f_pregunta.readline()
while (line):
    datos = line.strip().split(";")
    print(datos)

    pregunta = Pregunta()
    pregunta.id_pregunta = int(datos[columna_id_pregunta])
    pregunta.texto_pregunta = datos[columna_texto_pregunta]
    examen.preguntas.append(pregunta)

    line = f_pregunta.readline()

print("")
print("Procesando respuestas")
line = f_literal.readline()
line = f_literal.readline()
while (line):
    datos = line.strip().split(";")
    print(datos)

    literal = Literal()
    literal.id_literal = datos[columna_id_literal]
    literal.texto_literal = datos[columna_texto_literal]
    literal.correcto = datos[columna_literal_correcto]

    pregunta = list(filter(lambda x: x.id_pregunta == int(datos[columna_referencia_pregunta]), examen.preguntas))[0]
    pregunta.literales.append(literal)

    line = f_literal.readline()


# Paso 3: Imprimiendo prueba de preguntas
print("")
print("Iniciando la creacion de respuestas aspirante")
f = open("DataSetRespuestas.csv", "w")
f2 = open("DataSetGlobalSimple.csv", "w")

f.write("NUM_ASPIRANTE;ID_PREGUNTA;ID_LITERAL\n")
f2.write("NUM_ASPIRANTE;PREG_MATEMATICAS;RESP_MATEMATICAS\n")

estudiante = 1
for i in range(10000, (numero_estudiantes+10000+1)):
    contador_preguntas = 0
    contador_correctas = 0

    for pregunta in examen.preguntas:
        contador_preguntas = contador_preguntas + 1

        id_pregunta = pregunta.id_pregunta
        literal = pregunta.literales[random.randrange(0, len(pregunta.literales), 1)]
        id_literal = literal.id_literal

        if (literal.correcto == "SI"):
            contador_correctas = contador_correctas + 1

        fila = "{};{};{}\n".format(i, id_pregunta, id_literal)
        print(fila)
        f.write(fila)
    
    fila2 = "{};{};{}\n".format(i, contador_preguntas, contador_correctas)
    f2.write(fila2)

f.close()
f2.close()