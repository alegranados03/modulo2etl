import queries.FilaReporte as FilaReporte
import queries.ReporteResumen as ReporteResumen


class Reporte:
    def __init__(self, titulo, instituciones, buckets, tipo, detalles=False):
        self.titulo = titulo
        self.instituciones = instituciones
        self.tipo = tipo
        self.detalles = detalles
        self.buckets = buckets
        self.resumen = None
        self.filas = {}
        self.totales = {'total_preguntas': 0,
                        'total_preguntas_masculino': 0,
                        'total_preguntas_femenino': 0,
                        'total_fallos': 0,
                        'total_fallos_masculino': 0,
                        'total_fallos_femenino': 0,
                        'total_aciertos': 0,
                        'total_aciertos_masculino': 0,
                        'total_aciertos_femenino': 0}

    def prepararFilas(self):
        for bucket in self.buckets:
            temas = [int(x) for x in bucket.temas.split(",")]
            if(len(temas) > 1):
                self.filas[bucket.bucket_id] = FilaReporte(bucket.bucket_id, temas, bucket.nombre)
            else:
                self.filas[bucket.bucket_id] = FilaReporte(bucket.bucket_id, temas[0], bucket.nombre)

    def procesarDatos(self):
        for institucion in self.instituciones:
            if self.tipo == 'ADMISION':
                bucketsInstitucion = institucion.bucketsAdmision
            elif self.tipo == 'EXAMEN_PRUEBA':
                bucketsInstitucion = institucion.bucketsExamenesPrueba

            for bucket in bucketsInstitucion:
                fila = self.filas[bucket.id]
                fila.agregarDatosGeneral(bucket)
                # agregar datos a fila, falta funcion en la clase
                if self.detalles == True:
                    fila.agregarOModificarDetalle(bucket)

    def calcularTotales(self):
        for fila in self.filas.values():
            print("total: {0}, fallos: {1}, aciertos: {2}".format(fila.general['Npreguntas'],fila.fallos['Npreguntas'],fila.aciertos['Npreguntas']))
            self.totales['total_preguntas'] = self.totales['total_preguntas'] + fila.general['Npreguntas']
            self.totales['total_preguntas_masculino'] = self.totales['total_preguntas_masculino'] + fila.general['M']
            self.totales['total_preguntas_femenino'] = self.totales['total_preguntas_femenino'] + fila.general['F']
            self.totales['total_fallos'] = self.totales['total_fallos'] + fila.fallos['Npreguntas']
            self.totales['total_fallos_masculino'] = self.totales['total_fallos_masculino'] + fila.fallos['M']
            self.totales['total_fallos_femenino'] = self.totales['total_fallos_femenino'] + fila.fallos['F']
            self.totales['total_aciertos'] = self.totales['total_aciertos'] + fila.aciertos['Npreguntas']
            self.totales['total_aciertos_masculino'] = self.totales['total_aciertos_masculino'] + fila.aciertos['M']
            self.totales['total_aciertos_femenino'] = self.totales['total_aciertos_femenino'] + fila.aciertos['F']

    def generarResumen(self):
        self.resumen = ReporteResumen(self.filas, self.detalles)
        self.resumen.construirResumen()

    def ejecutarProcesamiento(self):
        self.procesarDatos()

    def removerDataEnBruto(self):
        self.instituciones = None
        self.buckets = None
