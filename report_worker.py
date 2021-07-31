from report import *

# Parametros de prueba (a ser reemplazados cuando el servicio se encuentre
# activo)


TIPO_REPORTE = 'COMPARACION_ADMISION_DIAGNOSTICO'
TIPO_BUSQUEDA = 'INSTITUCION'
VALORES_BUSQUEDA = [1]

# Variables ocuypadas solo para reportes 1 y 2
ID_EXAMEN_ADMISION = 6

# Variables solo ocupadas solo para reportes 3 y 4
ANIO = 2021
SECCION = 1
RONDA = 1

"""
    LLAMADA PARA REPORTE
"""
rp = ReportPopulator()
pdf = rp.llenar_reporte(TIPO_REPORTE, TIPO_BUSQUEDA, VALORES_BUSQUEDA, ID_EXAMEN_ADMISION, ANIO, SECCION, RONDA)
pdf.output('reporte_output.pdf')