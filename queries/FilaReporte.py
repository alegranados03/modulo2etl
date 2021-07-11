class FilaReporte:
    def __init__(self, bucket_id, temas, nombre):
        self.bucket_id = bucket_id
        self.temas = temas
        self.nombre = nombre
        self.general = {'Npreguntas': 0, 'M': 0, 'F': 0}
        self.fallos = {'Npreguntas': 0, 'M': 0, 'F': 0}
        self.aciertos = {'Npreguntas': 0, 'M': 0, 'F': 0}
        self.deficiencias = {}

    def agregarDatosGeneral(self, bucket): 
        self.general['Npreguntas'] = self.general['Npreguntas'] + bucket.preguntas
        self.general['M'] = self.general['M'] + bucket.preguntas_masculino
        self.general['F'] = self.general['F'] + bucket.preguntas_femenino
        self.fallos['Npreguntas'] = self.fallos['Npreguntas'] + bucket.fallos
        self.fallos['M'] = self.fallos['M'] + bucket.fallos_masculino
        self.fallos['F'] = self.fallos['F'] + bucket.fallos_femenino
        self.aciertos['Npreguntas'] = self.aciertos['Npreguntas'] + bucket.aciertos
        self.aciertos['M'] = self.aciertos['M'] + bucket.aciertos_masculino
        self.aciertos['F'] = self.aciertos['F'] + bucket.aciertos_femenino

    def agregarOModificarDetalle(self, bucket):
        for deficiencia in bucket.deficiencias:
            if deficiencia.etiqueta_id in self.deficiencias.keys():
                anterior = self.deficiencias[deficiencia.etiqueta_id]
                enunciado = anterior['enunciado']
                fallos = anterior['fallos'] + deficiencia.fallos
                fallos_femenino = anterior['fallos_femenino'] + deficiencia.fallos_femenino
                fallos_masculino = anterior['fallos_masculino'] + deficiencia.fallos_masculino
                nuevaDeficiencia = {'etiqueta_id': deficiencia.etiqueta_id,
                                    'enunciado': enunciado, 'fallos': fallos, 'fallos_femenino': fallos_femenino, 'fallos_masculino': fallos_masculino}
                self.deficiencias[deficiencia.etiqueta_id] = nuevaDeficiencia
            else:
                nuevaDeficiencia = {'etiqueta_id': deficiencia.etiqueta_id,
                                    'enunciado': deficiencia.enunciado, 'fallos': deficiencia.fallos, 'fallos_femenino': deficiencia.fallos_femenino, 'fallos_masculino': deficiencia.fallos_masculino}

                self.deficiencias[deficiencia.etiqueta_id] = nuevaDeficiencia
        