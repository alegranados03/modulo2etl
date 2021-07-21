from fpdf import FPDF
from datetime import datetime

"""
    Constantes
"""
TAMANIO_COLUMNA_TEMA = 2/8
TAMANIO_COLUMNA_N_PREG = 1/8
TAMANIO_COLUMNA_M_F = 1/8

T_COL_FORTALEZA_DEFICIENCIA = 1/2
T_COL_DEFICIENCIA_DETALLE = 6/10
T_COL_COMPARACION_TEMA = 3/8
T_COL_COMPARACION_FASE = 1/8
T_COL_COMPARACION_RESULTADO = 2/8

TABLA_DEFICIENCIA_TEMA = "TABLA_DEFICIENCIA_TEMA"
TABLA_RESUMEN_FORTALEZA_DEFICIENCIA = "TBL_RES_FORTALEZA_DEFICIENCIA"
TABLA_RESUMEN_DEFIENCIA_DETALLE = "TABLA_RESUMEN_DEFICIENCIA_DETALLE"
TABLA_RESUMEN_COMPARACION_RONDA = "TABLA_RESUMEN_COMPARACION_RONDA"
TABLA_RESUMEN_COMPARACION_ADMISION_PRUEBA = "TABLA_RESUMEN_COMPARACION_ADMISION_PRUEBA"

FILA_RESUMEN = 'FILA_RESUMEN'
FILA_TEMA = 'FILA_TEMA'
FILA_DEFICIENCIA = 'FILA_DEFICIENCIA'
FILA_RESUMEN_TEMA = 'FILA_RESUMEN_TEMA'
FILA_RESUMEN_DEFICIENCIA = 'FILA_RESUMEN_DEFICIENCIA'
FILA_COMPARACION = 'FILA_COMPRARACION'

"""
    Clases comunes a los reportes
"""

class EstiloCelda:
    def __init__(self, negrita=False, font='helvetica', font_size=10, color='black', align='C'):
        self.negrita = negrita
        self.font = font
        self.font_size = font_size
        self.color = color
        self.align = align

class ColumnaReporte(EstiloCelda):
    def __init__(self, nombre, ancho, negrita=False, font='helvetica', font_size=10, color='black'):
        EstiloCelda.__init__(self, negrita, font, font_size, color)
        self.nombre = nombre
        self.ancho = ancho

class FilaDato():
    def __init__(self, valores):
        self.valores = valores

class CeldaDato(EstiloCelda):
    def __init__(self, valor, negrita=False, font='helvetica', font_size=10, color='black', align='C'):
        EstiloCelda.__init__(self, negrita, font, font_size, color, align)
        self.valor = valor

class TablaReporte:
    def __init__(self, tipo):
        self.columnas = []
        self.tipo = tipo
        self.filas = []
        self.pre_encabezado = []
        self.tamanios_pre_encabezado = []

    def agregar_columna(self, columna):
        self.columnas.append(columna)
    
    def agregar_pre_encabezado(self, pre_encabezado):
        self.pre_encabezado.append(pre_encabezado)
    
    def agregar_fila_datos(self, data, tipo, subtotales = False):
        celdas = []
        negrita = False

        for i in range(0, len(data)):
            celda = data[i]
            flags = self.calcular_flags_celda(tipo, i, subtotales)
            negrita = flags[0]
            align = flags[1]

            celda_dato = CeldaDato(celda, negrita=negrita, align=align)
            celdas.append(celda_dato)

        fila = FilaDato(celdas)
        self.filas.append(fila)
    
    def calcular_flags_celda(self, tipo, i, subtotales):
        negrita = False
        align = 'C'

        if (subtotales):
            negrita = True
            return (negrita, align)

        if tipo == FILA_TEMA or tipo == FILA_COMPARACION:
            if i == 0:
                negrita = True
                align = 'J'
        elif tipo == FILA_RESUMEN_TEMA:
            negrita = True
            align = 'J'
        elif tipo == FILA_RESUMEN_DEFICIENCIA:
            negrita = False
            align = 'J' 
        
        return (negrita, align)


class PDF(FPDF):
    def inicializar_reporte(self, titulo, nivel, font='helvetica'):
        self.titulo = titulo
        self.nivel = nivel
        self.ahora = datetime.now()
        self.reporte_font = font

        # Paso 1: Instruir a FPDF en crear una nueva pagina
        #         Y definir Line break
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def agregar_cabecera(self):
        self.image('logo_ues.png', 10, 8, 28)
        self.set_font(self.reporte_font, 'B', 16)
        self.cell(0, 10, 'Universidad de El Salvador', ln=True, align='C')
        self.set_font(self.reporte_font, 'B', 14)
        self.cell(0, 10, 'Facultad de Ingeniería y Arquitectura', ln=True, align='C')
        self.set_font(self.reporte_font, 'B', 12)
        self.cell(0, 8, self.titulo, ln=True, align='C')
        self.cell(0, 8, 'Nivel ' + self.nivel, ln=True, align='C')
        self.ln(20)
    
    def footer(self):
        self.set_y(-15)
        self.set_font(self.reporte_font, 'I', 8)
        self.cell(1, 8, 'Fecha creacion: ' + self.ahora.strftime("%d/%m/%Y %H:%M:%S"), align='L')
        self.set_font(self.reporte_font, size=12)
        self.cell(0, 8, f'{self.page_no()}', align='C')
    
    def agregar_tabla(self, tabla, titulo=None):
        # Paso 1: Agregar el titulo si existe
        if titulo is not None:
            print('LOGICA A IMPLEMENTAR: TITULO DE TABLA')

        # Paso 1.1: Determinamos si el tamanio de la tabla no ocupa
        #           el espacio efectivo de la pagina, de ser asi centrar
        margen_original = self.l_margin
        margen_nuevo = margen_original
        if (self.epw != sum(col.ancho for col in tabla.columnas)):
            margen_nuevo = margen_original + (self.epw - sum(col.ancho for col in tabla.columnas))/2.0
            self.set_left_margin(margen_nuevo) 
        
        # Paso 1.2: Agregamos los pre encabezados si existen
        line_height = 0.0
        if len(tabla.pre_encabezado) > 0:
            numero_col_pre_encabezado = len(tabla.pre_encabezado)

            for i in range(0, numero_col_pre_encabezado):
                col = tabla.pre_encabezado[i]
                estilo = 'B' if col.negrita else ''
                line_height = col.font_size * 1.02

                self.set_font(col.font, estilo, col.font_size)
                self.multi_cell(col.ancho, line_height, col.nombre, align='C', border=1, max_line_height=line_height, ln=3)
            self.ln(line_height)
        
        # Paso 2: Dibujar cabeceras de la tabla
        numero_columnas = len(tabla.columnas)
        for i in range(0, numero_columnas):
            col = tabla.columnas[i]
            estilo = 'B' if col.negrita else ''
            line_height = col.font_size * 1.02

            self.set_font(col.font, estilo, col.font_size)
            self.multi_cell(col.ancho, line_height, col.nombre, align='C', border=1, max_line_height=line_height, ln=3)
        self.ln(line_height)

        # Paso 3: Dibujar filas normales de la tabla
        for fila in tabla.filas:
            # Variables ocupadas para el calculo de tamanio de celda
            x = self.get_x()
            y = self.get_y()
            max_altura = 0.0
            ultima_pos_x = x
            line_height = 5

            valores_ultima_pos_x = []
            valores_ultima_pos_x.append(ultima_pos_x)

            # Procedemos a dibujar la celda normalmente, dejando que FPDF
            # nos indique el tamanio de la celda mas alta
            for i in range(0, len(fila.valores)):
                print('numero de celdas de fila: ' + str(len(fila.valores)))
                celda = fila.valores[i]

                estilo = 'B' if celda.negrita else ''
                ancho = tabla.columnas[i].ancho
                valor = celda.valor

                self.set_font(celda.font, estilo, celda.font_size)
                self.multi_cell(ancho, line_height, valor, align=celda.align)

                # Despues de haber dibujado la celda, procedemos a calcular
                # su altura para guardarla como referencia
                if (self.get_y() - y > max_altura):
                    max_altura = self.get_y() - y
                
                # Empujar el cursor a la siguiente posicion en X, donde
                # deberia estar la columna
                ultima_pos_x += ancho
                self.set_xy(ultima_pos_x, y)
                valores_ultima_pos_x.append(ultima_pos_x)
            
            # Luego de haber dibujado la tabla normalmente, procedemos a
            # dibujar los bordes tomando de referencia la celda mas alta
            for i in range(0, len(valores_ultima_pos_x)):
                self.line(valores_ultima_pos_x[i], y, valores_ultima_pos_x[i], y + max_altura)
            
            self.line(x, y, valores_ultima_pos_x[len(valores_ultima_pos_x) - 1], y)
            self.line(x, y + max_altura, valores_ultima_pos_x[len(valores_ultima_pos_x) - 1], y + max_altura)
            self.set_xy(x, y + max_altura)
        
        # Paso 4: Volver al margen original
        self.set_left_margin(margen_original)
    
    """
        HELPER FUNCTIONS
    """
    def crear_tabla(self, tipo):
        columnas = []
        tamanios = []
        pre_encabezado = []
        tamanios_pre_encabezado = []

        if (tipo == TABLA_DEFICIENCIA_TEMA):
            columnas = ["Tema", "N° preguntas", "M", "F", "N° fallos", "M", "F"]
            tamanios = [TAMANIO_COLUMNA_TEMA, TAMANIO_COLUMNA_N_PREG, TAMANIO_COLUMNA_M_F,
                        TAMANIO_COLUMNA_M_F, TAMANIO_COLUMNA_N_PREG, TAMANIO_COLUMNA_M_F,
                        TAMANIO_COLUMNA_M_F]
            pre_encabezado = ["", "N° preguntas por género", "N° de fallos por género"]
            tamanios_pre_encabezado = [TAMANIO_COLUMNA_TEMA, TAMANIO_COLUMNA_N_PREG + TAMANIO_COLUMNA_M_F*2.0,
                        TAMANIO_COLUMNA_N_PREG + TAMANIO_COLUMNA_M_F*2.0]
        elif (tipo == TABLA_RESUMEN_FORTALEZA_DEFICIENCIA):
            columnas = ["Debilidades", "Fortalezas"]
            tamanios = [T_COL_FORTALEZA_DEFICIENCIA, T_COL_FORTALEZA_DEFICIENCIA]
        elif (tipo == TABLA_RESUMEN_DEFIENCIA_DETALLE):
            columnas = ["Debilidades (por tema y fallos comunes)"]
            tamanios = [T_COL_DEFICIENCIA_DETALLE]
        elif (tipo == TABLA_RESUMEN_COMPARACION_RONDA):
            columnas = ["Tema", "1ra", "2da", "dif", "Resultado"]
            tamanios = [T_COL_COMPARACION_TEMA, T_COL_COMPARACION_FASE, T_COL_COMPARACION_FASE,
                        T_COL_COMPARACION_FASE, T_COL_COMPARACION_RESULTADO]
        elif (tipo == TABLA_RESUMEN_COMPARACION_ADMISION_PRUEBA):
            columnas = ["Tema", "adm.", "diag.", "dif", "Resultado"]
            tamanios = [T_COL_COMPARACION_TEMA, T_COL_COMPARACION_FASE, T_COL_COMPARACION_FASE,
                        T_COL_COMPARACION_FASE, T_COL_COMPARACION_RESULTADO]
            
        # Paso 2: Creamos la tabla y almacenamos pre encabezados
        tabla = self.crear_tabla_general(tipo, columnas, tamanios, pre_encabezado, tamanios_pre_encabezado) 
        return tabla
    
    def crear_tabla_general(self, tipo, columnas, tamanios, pre_encabezado, tamanios_pre_encabezado):
        tabla = TablaReporte(tipo)

        # epw = available pdf width
        for i in range(0, len(columnas)):
            col = ColumnaReporte(columnas[i], tamanios[i]*self.epw, negrita=True)
            tabla.agregar_columna(col)
        
        for i in range(0, len(pre_encabezado)):
            col = ColumnaReporte(pre_encabezado[i], tamanios_pre_encabezado[i]*self.epw, negrita=True)
            tabla.agregar_pre_encabezado(col)
        
        return tabla


################################################################################################
# Ejemplo de generacion de un PDF para reportes del S.I

################### EJEMPLO REPORTE 1 ##########################################################
# Paso 0: Modelando datos de ejemplo para algunos escenarios
"""DATA_REPORTE_DEBILIDAD_TEMA = (
    ("Tema 1 texto de ejemplo del multi line para ver si funciona y ver cuales son los limites de la libreria para poder combatirlas", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 2", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 3", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 4", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)")
)

DATA_REPORTE_DEBILIDAD_TEMA_SUBTOTALES = (
    ("Subtotal", "435000", "370000", "65000", "360000", "320000", "40000")
)

DATA_REPORTE_RESUMEN_FORTALEZA_DEBILIDAD = (
    ("Casos de factoreo (80%)", "Aritmetica (80%)"),
    ("Casos de factoreo (80%)", "Aritmetica (80%)"),
    ("Casos de factoreo (80%)", ""),
    ("Casos de factoreo (80%)", "")
)


# Paso 1: Crear la instancia PDF y definir el tipo de papel y orientacion
pdf = PDF('P', 'mm', 'Letter')

# Paso 2: Definir el titulo del reporte y agregar la cabecera de pagina
pdf.inicializar_reporte(titulo='Reporte de fortalezas y deficiencias', nivel="departamental")
pdf.agregar_cabecera()

# Paso 3: Crear tabla de resumen de debilidades, llenarla de datos
#         y agregar la tabla al reporte
tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
for row in DATA_REPORTE_DEBILIDAD_TEMA:
    tabla.agregar_fila_datos(row, FILA_TEMA)

tabla.agregar_fila_datos(DATA_REPORTE_DEBILIDAD_TEMA_SUBTOTALES, FILA_TEMA, subtotales = True)
pdf.agregar_tabla(tabla)

# Paso 4: Crear tabla de resumen basico para fortalezas y deficiencias
pdf.ln(20)
tabla = pdf.crear_tabla(TABLA_RESUMEN_FORTALEZA_DEFICIENCIA)
for row in DATA_REPORTE_RESUMEN_FORTALEZA_DEBILIDAD:
    tabla.agregar_fila_datos(row, FILA_RESUMEN)
pdf.agregar_tabla(tabla)

# Paso X: guardar reporte
pdf.output('test_report.pdf')
"""
################## EJEMPLO REPORTE 02 ######################################
# Paso 0: Modelando datos de ejemplo para algunos escenarios
"""DATA_REPORTE_DEBILIDAD_TEMA = (
    ("Tema 1 texto de ejemplo del multi line para ver si funciona y ver cuales son los limites de la libreria para poder combatirlas", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 2", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 3", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 4", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)")
)

DATA_REPORTE_DEBILIDAD_TEMA_SUBTOTALES = (
    ("Subtotal", "435000", "370000", "65000", "360000", "320000", "40000")
)


# Paso 1: Crear la instancia PDF y definir el tipo de papel y orientacion
pdf = PDF('P', 'mm', 'Letter')

# Paso 2: Definir el titulo del reporte y agregar la cabecera de pagina
pdf.inicializar_reporte(titulo='Reporte de debilidades detalle', nivel="departamental")
pdf.agregar_cabecera()

# Paso 3: Crear tabla de resumen de debilidades, llenarla de datos
#         y agregar la tabla al reporte
tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
for row in DATA_REPORTE_DEBILIDAD_TEMA:
    tabla.agregar_fila_datos(row, FILA_TEMA)

tabla.agregar_fila_datos(DATA_REPORTE_DEBILIDAD_TEMA_SUBTOTALES, FILA_TEMA, subtotales = True)
pdf.agregar_tabla(tabla)

# Paso 4: Crear tabla de resumen basico para fortalezas y deficiencias
print('Imprimir tabla de resumen de deficiencias')
pdf.ln(20)
tabla = pdf.crear_tabla(TABLA_RESUMEN_DEFIENCIA_DETALLE)
tabla.agregar_fila_datos(['Nombre Tema 1'], FILA_RESUMEN_TEMA)
tabla.agregar_fila_datos(['        Deficiencia 1'], FILA_RESUMEN_DEFICIENCIA)
tabla.agregar_fila_datos(['        Deficiencia 2'], FILA_RESUMEN_DEFICIENCIA)
tabla.agregar_fila_datos(['        Deficiencia 3'], FILA_RESUMEN_DEFICIENCIA)
pdf.agregar_tabla(tabla)

# Paso X: guardar reporte
pdf.output('test_report.pdf')"""
######################### REPORTE 4 ##########################################
"""DATA_REPORTE_DEBILIDAD_TEMA = (
    ("Tema 1 texto de ejemplo del multi line para ver si funciona y ver cuales son los limites de la libreria para poder combatirlas", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 2", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 3", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)"),
    ("Tema 4", "200000", "170000", "30000", "185000 (80%)", "160000 (90%)", "25000 (10%)")
)

DATA_REPORTE_DEBILIDAD_TEMA_SUBTOTALES = (
    ("Subtotal", "435000", "370000", "65000", "360000", "320000", "40000")
)

DATA_COMPARATIVA = (
    ("Tema 1", "70.8%", "22.8%", "-5.2%", "EMPEORA"),
    ("Tema 2", "70.8%", "22.8%", "-5.2%", "EMPEORA"),
    ("Tema 3", "70.8%", "22.8%", "-5.2%", "EMPEORA"),
)


# Paso 1: Crear la instancia PDF y definir el tipo de papel y orientacion
pdf = PDF('P', 'mm', 'Letter')

# Paso 2: Definir el titulo del reporte y agregar la cabecera de pagina
pdf.inicializar_reporte(titulo='Reporte de debilidades detalle', nivel="departamental")
pdf.agregar_cabecera()

# Paso 3: Crear tabla de resumen de debilidades, llenarla de datos
#         y agregar la tabla al reporte
tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
for row in DATA_REPORTE_DEBILIDAD_TEMA:
    tabla.agregar_fila_datos(row, FILA_TEMA)

tabla.agregar_fila_datos(DATA_REPORTE_DEBILIDAD_TEMA_SUBTOTALES, FILA_TEMA, subtotales = True)
pdf.agregar_tabla(tabla)

# Paso 4: Crear tabla de resumen basico para fortalezas y deficiencias
print("Imprimir comparativa")
pdf.ln(20)
tabla = pdf.crear_tabla(TABLA_RESUMEN_COMPARACION_RONDA)
for row in DATA_COMPARATIVA:
    tabla.agregar_fila_datos(row, FILA_COMPARACION)
pdf.agregar_tabla(tabla)

# Paso X: guardar reporte
pdf.output('test_report.pdf')"""