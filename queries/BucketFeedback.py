class BucketFeedback:
    def __init__(self, temas, numero_preguntas, aciertos):
        self.temas = temas
        self.numero_preguntas = numero_preguntas
        self.aciertos = aciertos
        self.deficiencias = []
        self.porcentaje_fortaleza = 0.0
        self.porcentaje_debilidad = 0.0
    
    def calcular_porcentaje_fortaleza_debilidad(self):
        self.porcentaje_fortaleza = round((self.aciertos / self.numero_preguntas) * 100.0, 2)
        self.porcentaje_debilidad = 100.0 - self.porcentaje_fortaleza