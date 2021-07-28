from report import *

# Parametros de prueba (a ser reemplazados cuando el servicio se encuentre
# activo)


TIPO_REPORTE = 'COMPARACION_RONDA_1_2'
TIPO_BUSQUEDA = 'INSTITUCION'
VALORES_BUSQUEDA = [5]

# Variables ocuypadas solo para reportes 1 y 2
ID_EXAMEN_ADMISION = 2

# Variables solo ocupadas solo para reportes 3 y 4
ANIO = 2021
SECCION = 1

"""
    LLAMADA PARA REPORTE
"""
rp = ReportPopulator()
pdf = rp.llenar_reporte(TIPO_REPORTE, TIPO_BUSQUEDA, VALORES_BUSQUEDA, ID_EXAMEN_ADMISION, ANIO, SECCION)
pdf.output('reporte_output.pdf')