from report import *

TIPO_DEBILIDAD_FORTALEZA_TEMA = 'DEBILIDAD_FORTALEZA_TEMA'

TIPO_BUSQUEDA_DEPARTAMENTO = 'DEPARTAMENTO'
TIPO_BUSQUEDA_MUNICIPIO = 'MUNICIPIO'
TIPO_BUSQUEDA_INSTITUCION = 'INSTITUCION'

TABLA_DEFICIENCIA_TEMA = "TABLA_DEFICIENCIA_TEMA"
TABLA_FORTALEZA_TEMA = "TABLA_FORTALEZA_TEMA"
TABLA_RESUMEN_FORTALEZA_DEFICIENCIA = "TBL_RES_FORTALEZA_DEFICIENCIA"
TABLA_RESUMEN_DEFIENCIA_DETALLE = "TABLA_RESUMEN_DEFICIENCIA_DETALLE"
TABLA_RESUMEN_COMPARACION_RONDA = "TABLA_RESUMEN_COMPARACION_RONDA"
TABLA_RESUMEN_COMPARACION_ADMISION_PRUEBA = "TABLA_RESUMEN_COMPARACION_ADMISION_PRUEBA"

class ReportPopulator:
    def __init__(self):
        print('Hola Mundo')
        self.db = ReportBuilderConnection()
        self.report_builder = ReportBuilder(self.db)
    
    def llenar_reporte(self, tipo_reporte, tipo_busqueda, valores_busqueda, id_examen):
        if tipo_reporte == TIPO_DEBILIDAD_FORTALEZA_TEMA:
            return self.reporte_debilidades_fortalezas_tema(tipo_busqueda, valores_busqueda, id_examen)
    
    def reporte_debilidades_fortalezas_tema(self, tipo_busqueda, valores_busqueda, id_examen):
        # Paso 1: Generar PDF basico antes de empezar populate datos
        nivel = self.calcular_nivel(tipo_busqueda)
        seccion_prefix = self.calcular_prefix_seccion(tipo_busqueda)
        pdf = PDF('P', 'mm', 'Letter')
        pdf.inicializar_reporte(titulo='Reporte de debilidades y fortalezas por tema', nivel=nivel)
        pdf.agregar_cabecera()

        # Paso 2: Crear reporte en memoria (resultados) para cada una de los valores de busqueda
        for valor in valores_busqueda:
            query = self.report_builder.reporteDebilidadesYFortalezasTema(tipo_busqueda, [valor], id_examen)
            titulo = 'Test'

            if (tipo_busqueda == TIPO_BUSQUEDA_INSTITUCION):
                titulo = query.instituciones[0].nombre
            else:
                titulo = query.nombreLugar

            pdf.agregar_seccion(seccion_prefix + titulo)

            # Paso 2.1 Crear listas ordenadas en base a aciertos y en base a fallos
            temas_ordenado_acierto = sorted(list(query.filas.values()), key = lambda fila: fila.porcentaje_acierto, reverse=True)
            temas_ordenado_fallos = sorted(list(query.filas.values()), key = lambda fila: fila.porcentaje_fallo, reverse=True)

            # Paso 2.2: Obteniendo el subset de fortalezas y debilidades
            #           La condicion de filtrado es:
            #           Una fortaleza se considera fotaleza si su % acierto > 50
            #           Una debilidad se considera debilidad si su % fallo > 50
            fortalezas = [fortaleza for fortaleza in temas_ordenado_acierto if fortaleza.porcentaje_acierto >= 50.00]
            debilidades = [debilidad for debilidad in temas_ordenado_fallos if debilidad.porcentaje_acierto < 50.00]

            # Paso 2.3 Procedemos a crear la seccion de fortalezas
            tabla = pdf.crear_tabla(TABLA_FORTALEZA_TEMA)
            contador = 1
            for fila in fortalezas:
                datos = (str(contador) + '. ' + fila.nombre, 
                        str(fila.general['Npreguntas']), str(fila.general['M']), str(fila.general['F']),
                        str(fila.aciertos['Npreguntas']), str(fila.aciertos['M']), str(fila.aciertos['F']))
                tabla.agregar_fila_datos(datos, FILA_TEMA)
                contador += 1
            
            # Agregando los totales de la tabla
            n_preg_total = sum(fortaleza.general['Npreguntas'] for fortaleza in fortalezas)
            n_preg_m = sum(fortaleza.general['M'] for fortaleza in fortalezas)
            n_preg_f = sum(fortaleza.general['F'] for fortaleza in fortalezas)
            n_aciertos_total = sum(fortaleza.aciertos['Npreguntas'] for fortaleza in fortalezas)
            n_aciertos_m = sum(fortaleza.aciertos['M'] for fortaleza in fortalezas)
            n_aciertos_f = sum(fortaleza.aciertos['F'] for fortaleza in fortalezas)
            
            totales = ('Total', str(n_preg_total), str(n_preg_m), str(n_preg_f), 
                    str(n_aciertos_total), str(n_aciertos_m), str(n_aciertos_f))
            tabla.agregar_fila_datos(totales, FILA_TEMA, subtotales = True)
            pdf.agregar_tabla(tabla, titulo='Resumen fortalezas')

            # Paso 2.2 Procedemos a crear la seccion de debilidades
            tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
            contador = 1
            for fila in debilidades:
                datos = (str(contador) + '. ' + fila.nombre, 
                        str(fila.general['Npreguntas']), str(fila.general['M']), str(fila.general['F']),
                        str(fila.fallos['Npreguntas']), str(fila.fallos['M']), str(fila.fallos['F']))
                tabla.agregar_fila_datos(datos, FILA_TEMA)
                contador += 1
            
            # Agregando los totales de la tabla
            n_preg_total = sum(debilidad.general['Npreguntas'] for debilidad in debilidades)
            n_preg_m = sum(debilidad.general['M'] for debilidad in debilidades)
            n_preg_f = sum(debilidad.general['F'] for debilidad in debilidades)
            n_fallos_total = sum(debilidad.aciertos['Npreguntas'] for debilidad in debilidades)
            n_fallos_m = sum(debilidad.aciertos['M'] for debilidad in debilidades)
            n_fallos_f = sum(debilidad.aciertos['F'] for debilidad in debilidades)
            
            totales = ('Total', str(n_preg_total), str(n_preg_m), str(n_preg_f), 
                    str(n_fallos_total), str(n_fallos_m), str(n_fallos_f))
            tabla.agregar_fila_datos(totales, FILA_TEMA, subtotales = True)
            pdf.agregar_tabla(tabla, titulo='Resumen debilidades')

            # Paso 2.3: procedemos a crear la tabla resumen
            tabla = pdf.crear_tabla(TABLA_RESUMEN_FORTALEZA_DEFICIENCIA)
            pdf.agregar_tabla(tabla)
            

        return pdf
    
    def calcular_nivel(self, tipo_busqueda):
        if (tipo_busqueda == TIPO_BUSQUEDA_INSTITUCION):
            return 'institucional'
        elif (tipo_busqueda == TIPO_BUSQUEDA_DEPARTAMENTO):
            return 'departamental'
        else:
            return 'municipal'
    
    def calcular_prefix_seccion(self, tipo_busqueda):
        if (tipo_busqueda == TIPO_BUSQUEDA_INSTITUCION):
            return 'Institución: '
        elif (tipo_busqueda == TIPO_BUSQUEDA_DEPARTAMENTO):
            return 'Departamento: '
        else:
            return 'Municipio: '
