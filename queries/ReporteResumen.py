class ReporteResumen:
    def __init__(self, filasReporte, detalles=False):
        self.filas = filasReporte
        self.detalles = detalles
        self.filasResumen = {}

    def construirResumen(self):
        for filaReporte in self.filas.values():
            general = filaReporte.general['Npreguntas']
            fallos = filaReporte.fallos['Npreguntas']
            aciertos = filaReporte.aciertos['Npreguntas']

            self.filasResumen[filaReporte.bucket_id] = {
                'bucket_id':filaReporte.bucket_id,
                'temas':filaReporte.temas,
                'nombre':filaReporte.nombre,
                'porcentaje_aciertos':round(aciertos/general,2),
                'porcentaje_fallos':round(fallos/general,2)
            }

            if self.detalles==True:
                resumenDeficiencia={}
                for deficiencia in filaReporte.deficiencias.values():
                    resumenDeficiencia[deficiencia['etiqueta_id']]={
                        'etiqueta_id':deficiencia['etiqueta_id'],
                        'enunciado':deficiencia['enunciado'],
                        'porcentaje_deficiencia':round(deficiencia['fallos']/fallos,2)
                    }
                self.filasResumen[filaReporte.bucket_id]['resumen_deficiencias'] = resumenDeficiencia
