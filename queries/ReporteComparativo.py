class ReporteComparativo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.bucketsComparadores = {}
        self.filasResultado = []

    def inicializarComparadores(self, buckets1, buckets2):
        for bucket in buckets1:
            self.bucketsComparadores[bucket.temas] = {'nombre': bucket.nombre}

        for bucket in buckets2:
            if bucket.temas not in self.bucketsComparadores.keys():
                self.bucketsComparadores[bucket.temas] = {
                    'nombre': bucket.nombre}

    def procesarDatos(self, reporte1, reporte2):
        filasResumen1 = reporte1.resumen.filasResumen
        filasResumen2 = reporte2.resumen.filasResumen

        for fila in filasResumen1.values():
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
        
        self.realizarComparacion()

    def realizarComparacion(self):
        for comparador in self.bucketsComparadores.values():
            comparacion = {'nombre': comparador['nombre'], 'aciertos': {}, 'fallos': {}, 'deficiencias': {}}

            if 'examen1' in comparador.keys() and 'examen2' in comparador.keys():
                acierto1 = comparador['examen1']['porcentaje_aciertos']
                acierto2 = comparador['examen2']['porcentaje_aciertos']
                fallo1 = comparador['examen1']['porcentaje_fallos']
                fallo2 = comparador['examen2']['porcentaje_fallos']
                if len(comparador['examen1']['deficiencias'].keys()) > 0 and len(comparador['examen2']['deficiencias'].keys()) > 0:
                    comparacion['deficiencias'] = {}

                if 'deficiencias' in comparacion.keys():
                    for key in comparador['examen1']['deficiencias'].keys():
                        if key in comparador['examen2']['deficiencias'].keys():
                            comparacion['deficiencias'][key] = {
                                "enunciado": comparador['examen1']['deficiencias'][key]['enunciado'],
                                "examen1_porcentaje_deficiencia": comparador['examen1']['deficiencias'][key]['porcentaje_deficiencia'],
                                "examen2_porcentaje_deficiencia": comparador['examen2']['deficiencias'][key]['porcentaje_deficiencia']
                            }
                        else:
                            comparacion['deficiencias'][key] = {
                                "enunciado": comparador['examen1']['deficiencias'][key]['enunciado'],
                                "examen1_porcentaje_deficiencia": comparador['examen1']['deficiencias'][key]['porcentaje_deficiencia'],
                                "examen2_porcentaje_deficiencia": '-'
                            }

                    for key in comparador['examen2']['deficiencias'].keys():
                        if key not in comparador['examen1']['deficiencias'].keys():
                            comparacion['deficiencias'][key] = {
                                "enunciado": comparador['examen2']['deficiencias'][key]['enunciado'],
                                "examen1_porcentaje_deficiencia": '-',
                                "examen2_porcentaje_deficiencia": comparador['examen2']['deficiencias'][key]['porcentaje_deficiencia']
                            }

            else:
                if 'examen1' not in comparador.keys() and 'examen2' in comparador.keys():
                    acierto1 = '-'
                    acierto2 = comparador['examen2']['porcentaje_aciertos']
                    fallo1 = '-'
                    fallo2 = comparador['examen2']['porcentaje_fallos']
                    if len(comparador['examen2']['deficiencias'].keys()) > 0:
                        comparacion['deficiencias'] = {}

                    if 'deficiencias' in comparacion.keys():
                        for key in comparador['examen2']['deficiencias'].keys():
                            comparacion['deficiencias'][key] = {
                                "enunciado": comparador['examen2']['deficiencias'][key]['enunciado'],
                                "examen1_porcentaje_deficiencia": '-',
                                "examen2_porcentaje_deficiencia": comparador['examen2']['deficiencias'][key]['porcentaje_deficiencia']
                            }

                elif 'examen1' in comparador.keys() and 'examen2' not in comparador.keys():
                    acierto1 = comparador['examen1']['porcentaje_aciertos']
                    acierto2 = '-'
                    fallo1 = comparador['examen1']['porcentaje_fallos']
                    fallo2 = '-'
                    if len(comparador['examen1']['deficiencias'].keys()) > 0:
                        comparacion['deficiencias'] = {}

                    if 'deficiencias' in comparacion.keys():
                        for key in comparador['examen1']['deficiencias'].keys():
                            comparacion['deficiencias'][key] = {
                                "enunciado": comparador['examen1']['deficiencias'][key]['enunciado'],
                                "examen1_porcentaje_deficiencia": comparador['examen1']['deficiencias'][key]['porcentaje_deficiencia'],
                                "examen2_porcentaje_deficiencia": '-'
                            }
                else:
                    return 0

            comparacion['aciertos'] = {'examen1': acierto1, 'examen2': acierto2}
            comparacion['fallos'] = {'examen1': fallo1, 'examen2': fallo2}
            self.filasResultado.append(comparacion)