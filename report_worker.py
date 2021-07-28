from report import *

# Parametros de prueba (a ser reemplazados cuando el servicio se encuentre
# activo)

TIPO_REPORTE = 'DEBILIDAD_FORTALEZA_TEMA'
TIPO_BUSQUEDA = 'MUNICIPIO'
VALORES_BUSQUEDA = [85, 124]
ID_EXAMEN_ADMISION = 2

# Paso 1: Popular reporte
rp = ReportPopulator()
pdf = rp.llenar_reporte(TIPO_REPORTE, TIPO_BUSQUEDA, VALORES_BUSQUEDA, ID_EXAMEN_ADMISION)
pdf.output('reporte_output.pdf')