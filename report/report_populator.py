from report import *

TIPO_DEBILIDAD_FORTALEZA_TEMA = 'DEBILIDAD_FORTALEZA_TEMA'
TIPO_DEBILIDAD_DETALLE = 'DEBILIDAD_DETALLE'
TIPO_COMPARACION_RONDA_1_2 = 'COMPARACION_RONDA_1_2'
TIPO_COMPARACION_ADMISION_DIAGNOSTICO = 'COMPARACION_ADMISION_DIAGNOSTICO'

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
    
    def llenar_reporte(self, tipo_reporte, tipo_busqueda, valores_busqueda, id_examen, anio, seccion):
        if tipo_reporte == TIPO_DEBILIDAD_FORTALEZA_TEMA:
            return self.reporte_debilidades_fortalezas_tema(tipo_busqueda, valores_busqueda, id_examen)
        elif tipo_reporte == TIPO_DEBILIDAD_DETALLE:
            return self.reporte_debilidades_detalle(tipo_busqueda, valores_busqueda, id_examen)
        elif tipo_reporte == TIPO_COMPARACION_RONDA_1_2:
            return self.reporte_comparativo_ronda_1_2(tipo_busqueda, valores_busqueda, anio, seccion)
    
    """
        FUNCIONES GENERADORAS DE REPORTE
    """

    """
        REPORTE 1: Reporte de debilidades y fortalezas por tema
    """
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
            fortaleza_debilidad = self.calcular_lista_fortaleza_debilidad(query.filas.values())
            fortalezas = fortaleza_debilidad[0]
            debilidades = fortaleza_debilidad[1]

            # Paso 2.2 Procesar vlores y agregarlos a la tabla, tanto para debilidad
            #          como fortaleza
            tabla = pdf.crear_tabla(TABLA_FORTALEZA_TEMA)
            tabla = self.procesar_tabla_fortaleza_deficiencia(tabla, fortalezas, is_fortaleza = True)
            pdf.agregar_tabla(tabla, titulo='Resumen fortalezas')

            tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
            tabla = self.procesar_tabla_fortaleza_deficiencia(tabla, debilidades, is_fortaleza = False)
            pdf.agregar_tabla(tabla, titulo='Resumen debilidades')

            # Paso 2.3: procedemos a crear la tabla resumen
            tabla = pdf.crear_tabla(TABLA_RESUMEN_FORTALEZA_DEFICIENCIA)
            pdf.agregar_tabla(tabla)
            

        return pdf
    
    """
        REPORTE 2: Reporte de debilidades
    """
    def reporte_debilidades_detalle(self, tipo_busqueda, valores_busqueda, id_examen):
        # Paso 1: Generar PDF basico antes de empezar populate datos
        nivel = self.calcular_nivel(tipo_busqueda)
        seccion_prefix = self.calcular_prefix_seccion(tipo_busqueda)
        pdf = PDF('P', 'mm', 'Letter')
        pdf.inicializar_reporte(titulo='Reporte de debilidades detallado', nivel=nivel)
        pdf.agregar_cabecera()

        # Paso 2: Crear reporte en memoria (resultados) para cada una de los valores de busqueda
        for valor in valores_busqueda:
            query = self.report_builder.reporteDetalleDebilidades(tipo_busqueda, [valor], id_examen)
            titulo = 'Test'

            if (tipo_busqueda == TIPO_BUSQUEDA_INSTITUCION):
                titulo = query.instituciones[0].nombre
            else:
                titulo = query.nombreLugar

            pdf.agregar_seccion(seccion_prefix + titulo)
            
            tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
            temas_ordenado_fallos = sorted(list(query.filas.values()), key = lambda fila: fila.porcentaje_fallo, reverse=True)
            contador = 1
            for fila in temas_ordenado_fallos:
                datos = (str(contador) + '. ' + fila.nombre, 
                        str(fila.general['Npreguntas']), str(fila.general['M']), str(fila.general['F']),
                        str(fila.fallos['Npreguntas']), str(fila.fallos['M']), str(fila.fallos['F']))
                tabla.agregar_fila_datos(datos, FILA_TEMA)

                # Por cada tema, imprimimos las deficiencias
                for deficiencia in fila.deficiencias.values():
                    datos = (deficiencia['enunciado'], '-', '-', '-',
                            str(deficiencia['fallos']), str(deficiencia['fallos_femenino']), str(deficiencia['fallos_masculino']))
                    tabla.agregar_fila_datos(datos, FILA_DEFICIENCIA)
                contador += 1
            
            # Agregando los totales de la tabla
            totales = ('Total', str(query.totales['total_preguntas']), str(query.totales['total_preguntas_masculino']), str(query.totales['total_preguntas_femenino']),
                      str(query.totales['total_fallos']), str(query.totales['total_fallos_masculino']), str(query.totales['total_fallos_femenino']))
            tabla.agregar_fila_datos(totales, FILA_TEMA, subtotales = True)
            pdf.agregar_tabla(tabla, titulo = 'Detalle debilidades')

            # Agregando el resumen de debilidades
            tabla = pdf.crear_tabla(TABLA_RESUMEN_DEFIENCIA_DETALLE)
            contador = 1
            for fila in temas_ordenado_fallos:
                datos = [str(contador) + '. ' + fila.nombre + ' (' + str(fila.porcentaje_fallo) + '%)']
                tabla.agregar_fila_datos(datos, FILA_RESUMEN_TEMA)

                for deficiencia in fila.deficiencias.values():
                    pcj_fallo = 0.0

                    if (fila.fallos['Npreguntas'] > 0):  
                        pcj_fallo = (deficiencia['fallos'] / fila.fallos['Npreguntas'])*100.0
                        pcj_fallo = round(pcj_fallo, 2)
                    
                    datos = ['      ' + deficiencia['enunciado'] + ' (' + str(pcj_fallo) + '%)']
                    tabla.agregar_fila_datos(datos, FILA_RESUMEN_DEFICIENCIA)
                contador += 1
            
            pdf.agregar_tabla(tabla)
        return pdf
    
    """
        REPORTE 3: Comparacion primera ronda vs segunda ronda
    """
    def reporte_comparativo_ronda_1_2(self, tipo_busqueda, valores_busqueda, anio, seccion):
        # Paso 1: Generar PDF basico antes de empezar populate datos
        nivel = self.calcular_nivel(tipo_busqueda)
        seccion_prefix = self.calcular_prefix_seccion(tipo_busqueda)
        pdf = PDF('P', 'mm', 'Letter')
        pdf.inicializar_reporte(titulo='Reporte comparativo primera ronda vs segunda ronda', nivel=nivel)
        pdf.agregar_cabecera()

        for valor in valores_busqueda:
            # Paso 1: Obtener el reporte en memoria, y agregar el titulo de seccion
            #         respectivo
            query = self.report_builder.reporteDebilidadesAmbasRondas(tipo_busqueda, [valor], anio, seccion)
            titulo = 'Test'

            if (tipo_busqueda == TIPO_BUSQUEDA_INSTITUCION):
                titulo = query['reporte_examen_admision_1'].instituciones[0].nombre
            else:
                titulo = query['reporte_examen_admision_1'].nombreLugar
            pdf.agregar_seccion(seccion_prefix + titulo)

            # Paso 2: Desplegar la info del reporte 1
            fortaleza_debilidad = self.calcular_lista_fortaleza_debilidad(query['reporte_examen_admision_1'].filas.values())
            fortalezas = fortaleza_debilidad[0]
            debilidades = fortaleza_debilidad[1]

            tabla = pdf.crear_tabla(TABLA_FORTALEZA_TEMA)
            tabla = self.procesar_tabla_fortaleza_deficiencia(tabla, fortalezas, is_fortaleza = True)
            pdf.agregar_tabla(tabla, titulo='Resumen fortalezas primera fase')

            tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
            tabla = self.procesar_tabla_fortaleza_deficiencia(tabla, debilidades, is_fortaleza = False)
            pdf.agregar_tabla(tabla, titulo='Resumen debilidades primera fase')

            # Paso 3: Desplegar la info de reporte 2
            fortaleza_debilidad_2 = self.calcular_lista_fortaleza_debilidad(query['reporte_examen_admision_2'].filas.values())
            fortalezas_2 = fortaleza_debilidad_2[0]
            debilidades_2 = fortaleza_debilidad_2[1]

            tabla = pdf.crear_tabla(TABLA_FORTALEZA_TEMA)
            tabla = self.procesar_tabla_fortaleza_deficiencia(tabla, fortalezas, is_fortaleza = True)
            pdf.agregar_tabla(tabla, titulo='Resumen fortalezas segunda fase')

            tabla = pdf.crear_tabla(TABLA_DEFICIENCIA_TEMA)
            tabla = self.procesar_tabla_fortaleza_deficiencia(tabla, debilidades, is_fortaleza = False)
            pdf.agregar_tabla(tabla, titulo='Resumen debilidades segunda fase')

            # Paso 4: Calcular tablas de resumen respectivas
            tabla = pdf.crear_tabla(TABLA_RESUMEN_COMPARACION_RONDA)
            tabla = self.procesar_tabla_comparacion_ronda_1_2(tabla, query['reporte_comparativo'].filasResultado, calcular_fortaleza = True)
            pdf.agregar_tabla(tabla, titulo='Resumen (fortalezas)')

            tabla = pdf.crear_tabla(TABLA_RESUMEN_COMPARACION_RONDA)
            tabla = self.procesar_tabla_comparacion_ronda_1_2(tabla, query['reporte_comparativo'].filasResultado, calcular_fortaleza = False)
            pdf.agregar_tabla(tabla, titulo='Resumen (debilidades)')

        return pdf
    
    """
        REPORTE 4
    """
    
    
    """
        HELPER FUNCTIONS
    """
    def procesar_tabla_fortaleza_deficiencia(self, tabla, fortaleza_deficiencia, is_fortaleza=False):
        contador = 1
        for fila in fortaleza_deficiencia:
            datos = None

            if is_fortaleza:
                datos = (str(contador) + '. ' + fila.nombre, 
                        str(fila.general['Npreguntas']), str(fila.general['M']), str(fila.general['F']),
                        str(fila.aciertos['Npreguntas']), str(fila.aciertos['M']), str(fila.aciertos['F']))
            else:
                datos = (str(contador) + '. ' + fila.nombre, 
                        str(fila.general['Npreguntas']), str(fila.general['M']), str(fila.general['F']),
                        str(fila.fallos['Npreguntas']), str(fila.fallos['M']), str(fila.fallos['F']))

            tabla.agregar_fila_datos(datos, FILA_TEMA)
            contador += 1
        
        # Agregando los totales de la tabla
        n_preg_total = sum(fortaleza.general['Npreguntas'] for fortaleza in fortaleza_deficiencia)
        n_preg_m = sum(fortaleza.general['M'] for fortaleza in fortaleza_deficiencia)
        n_preg_f = sum(fortaleza.general['F'] for fortaleza in fortaleza_deficiencia)

        n_aciertos_total = 0
        n_aciertos_m = 0
        n_aciertos_f = 0

        if is_fortaleza:
            n_aciertos_total = sum(fortaleza.aciertos['Npreguntas'] for fortaleza in fortaleza_deficiencia)
            n_aciertos_m = sum(fortaleza.aciertos['M'] for fortaleza in fortaleza_deficiencia)
            n_aciertos_f = sum(fortaleza.aciertos['F'] for fortaleza in fortaleza_deficiencia)
        else:
            n_aciertos_total = sum(debilidad.fallos['Npreguntas'] for debilidad in fortaleza_deficiencia)
            n_aciertos_m = sum(debilidad.fallos['M'] for debilidad in fortaleza_deficiencia)
            n_aciertos_f = sum(debilidad.fallos['F'] for debilidad in fortaleza_deficiencia)
        
        totales = ('Total', str(n_preg_total), str(n_preg_m), str(n_preg_f), 
                str(n_aciertos_total), str(n_aciertos_m), str(n_aciertos_f))
        tabla.agregar_fila_datos(totales, FILA_TEMA, subtotales = True)

        return tabla
    
    def procesar_tabla_comparacion_ronda_1_2(self, tabla, resultados, calcular_fortaleza = False):
        # Paso 1: Extraer de la tabla comparativa todas las filas que se consideren fortaleza
        #         o debilidad
        match_inicial = None
        match_inicial_2 = None
        if calcular_fortaleza:
            match_inicial = [fila for fila in resultados 
                if (isinstance(fila['aciertos']['examen1'], float) and fila['aciertos']['examen1'] >= 0.5) or
                   (isinstance(fila['aciertos']['examen2'], float) and fila['aciertos']['examen2'] >= 0.5)]
        else:
            match_inicial = [fila for fila in resultados 
                if (isinstance(fila['aciertos']['examen1'], float) and fila['aciertos']['examen1'] < 0.5) or
                   (isinstance(fila['aciertos']['examen2'], float) and fila['aciertos']['examen2'] < 0.5)]
        
        # En base a los matches iniciales, calcular pcj de mejora o empeora
        for match in match_inicial:
            pcj_ronda_1 = 0.0
            pcj_ronda_2 = 0.0

            if calcular_fortaleza:
                pcj_ronda_1 = match['aciertos']['examen1']
                pcj_ronda_2 = match['aciertos']['examen2']
            else:
                pcj_ronda_1 = match['fallos']['examen1']
                pcj_ronda_2 = match['fallos']['examen2']


            calculo = self.calcular_fila_comparativa_ronda_1_2(pcj_ronda_1, pcj_ronda_2, calcular_fortaleza)
            datos = (match['nombre'], calculo[0], calculo[1], calculo[2], calculo[3])
            tabla.agregar_fila_datos(datos, FILA_COMPARACION)           

        return tabla
    
    def calcular_fila_comparativa_ronda_1_2(self, pcj_ronda_1, pcj_ronda_2, calcular_fortaleza = False):
        datos = ()

        # En este escenario no hay nada que comparar, simplemente se despliega
        if isinstance(pcj_ronda_1, str) or isinstance(pcj_ronda_2, str):
            datos = (str(round(pcj_ronda_1*100, 2)) + '%' if isinstance(pcj_ronda_1, int) else pcj_ronda_1,
                     str(round(pcj_ronda_2*100, 2)) + '%' if isinstance(pcj_ronda_2, int) else pcj_ronda_2,
                     '-', '-')
        else:
            pcj_ronda_1 = round(pcj_ronda_1*100.0, 2)
            pcj_ronda_2 = round(pcj_ronda_2*100.0, 2)

            pcj_diferencia =  pcj_ronda_2 - pcj_ronda_1
            resultado = ''

            if pcj_diferencia < 0.0:
                resultado = 'EMPEORA' if calcular_fortaleza else 'MEJORA'
            elif pcj_diferencia > 0.0:
                resultado = 'MEJORA' if calcular_fortaleza else 'EMPEORA'
            else:
                resultado = 'MANTUVO'
            
            datos = (str(pcj_ronda_1) + '%', str(pcj_ronda_2) + '%',
                    str(pcj_diferencia) + '%', resultado)
        
        return datos
    
    def calcular_lista_fortaleza_debilidad(self, filas):
        # Paso 2.1 Crear listas ordenadas en base a aciertos y en base a fallos
        temas_ordenado_acierto = sorted(list(filas), key = lambda fila: fila.porcentaje_acierto, reverse=True)
        temas_ordenado_fallos = sorted(list(filas), key = lambda fila: fila.porcentaje_fallo, reverse=True)

        # Paso 2.2: Obteniendo el subset de fortalezas y debilidades
        #           La condicion de filtrado es:
        #           Una fortaleza se considera fotaleza si su % acierto > 50
        #           Una debilidad se considera debilidad si su % fallo > 50
        fortalezas = [fortaleza for fortaleza in temas_ordenado_acierto if fortaleza.porcentaje_acierto >= 50.00]
        debilidades = [debilidad for debilidad in temas_ordenado_fallos if debilidad.porcentaje_acierto < 50.00]

        return [fortalezas, debilidades]
    
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
