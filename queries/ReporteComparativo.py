class ReporteComparativo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.bucketsComparadores = {}

    def inicializarComparadores(self, buckets1, buckets2):
        for bucket in buckets1:
            self.bucketsComparadores[bucket.temas] = {}

        for bucket in buckets2:
            if bucket.temas not in self.bucketsComparadores.keys():
                self.bucketsComparadores[bucket.temas] = {}

    def procesarDatos(self, reporte1, reporte2):
        filasResumen1 = reporte1.resumen.filasResumen
        filasResumen2 = reporte2.resumen.filasResumen

        for fila in filasResumen1.values():
            if(isinstance(fila['temas'], int)):
                indiceDiccionario = str(fila['temas'])
            elif(isinstance(fila['temas'], list)):
                indiceDiccionario = ",".join([str(x) for x in fila['temas']])

            estructura =  {
                'porcentaje_aciertos': fila['porcentaje_aciertos'],
                'porcentaje_fallos': fila['porcentaje_fallos']
            }
            

            estructuraDeficiencia = {}
            if 'resumen_deficiencias' in fila.keys():
                for deficiencia in fila['resumen_deficiencias'].values():
                    estructuraDeficiencia[deficiencia['etiqueta_id']] = {
                        'etiqueta_id': deficiencia['etiqueta_id'],
                        'enunciado': deficiencia['enunciado'],
                        'porcentaje_deficiencia': deficiencia['porcentaje_deficiencia']
                    }

            estructura['deficiencias'] = estructuraDeficiencia
            self.bucketsComparadores[indiceDiccionario]['examen1'] = estructura
        
        for fila in filasResumen2.values():
            if(isinstance(fila['temas'], int)):
                indiceDiccionario = str(fila['temas'])
            elif(isinstance(fila['temas'], list)):
                indiceDiccionario = ",".join([str(x) for x in fila['temas']])

            estructura = {
                'porcentaje_aciertos': fila['porcentaje_aciertos'],
                'porcentaje_fallos': fila['porcentaje_fallos']
            }
            

            estructuraDeficiencia = {}
            if 'resumen_deficiencias' in fila.keys():
                for deficiencia in fila['resumen_deficiencias'].values():
                    estructuraDeficiencia[deficiencia['etiqueta_id']] = {
                        'etiqueta_id': deficiencia['etiqueta_id'],
                        'enunciado': deficiencia['enunciado'],
                        'porcentaje_deficiencia': deficiencia['porcentaje_deficiencia']
                    }

            estructura['deficiencias'] = estructuraDeficiencia
            self.bucketsComparadores[indiceDiccionario]['examen2'] = estructura


    def realizarComparacion(self):
        pass