from report import *

# Parametros de prueba (a ser reemplazados cuando el servicio se encuentre
# activo)

TIPO_REPORTE = 'DEBILIDAD_DETALLE'
TIPO_BUSQUEDA = 'DEPARTAMENTO'
VALORES_BUSQUEDA = [7]
ID_EXAMEN_ADMISION = 2

# Paso 1: Popular reporte
rp = ReportPopulator()
pdf = rp.llenar_reporte(TIPO_REPORTE, TIPO_BUSQUEDA, VALORES_BUSQUEDA, ID_EXAMEN_ADMISION)
pdf.output('reporte_output.pdf')