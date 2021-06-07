from queries import *
from queries.QueryExecutor import ExamenAdmisionQueryExecutor, ExamenPruebaQueryExecutor

class Reporte:
    def __init__(self,nombre):
        self.nombre = nombre
        self.diccionario_filas = dict()

    def registrarOActualizarFilaReporte(bucket):
        pass
    
    def actualizarSubFila(filaReporte,deficiencia):
        pass


class FilaReporte:
    def __init__(self,bucket_id,nombre,preguntas, preguntas_masculino, preguntas_femenino, aciertos,aciertos_masculino, aciertos_femenino, fallos, fallos_masculino, fallos_femenino):
        self.bucket_id = bucket_id
        self.nombre = nombre
        self.preguntas = preguntas
        self.preguntas_masculino = preguntas_masculino
        self.preguntas_femenino = preguntas_femenino
        self.aciertos = aciertos
        self.aciertos_masculino = aciertos_masculino
        self.aciertos_femenino = aciertos_femenino
        self.fallos = fallos
        self.fallos_masculino = fallos_masculino
        self.fallos_femenino = fallos_femenino
        self.subFilas = []

    

class ReportBuilder:
    def reporteDebilidadesYFortalezasTema(instituciones):
        # los buckets considerados en este reporte solo son de examen de admisión
        pass

    def reporteDetalleDebilidades(instituciones):
        pass

    def reporteDebilidadesAmbasRondas(instituciones):
        pass

    def reporteRendimientoGlobal(instituciones):
        pass
