class DeficienciaFeedback:
    def __init__(self, etiqueta, fallos):
        self.etiqueta = etiqueta
        self.fallos = fallos
        self.porcentaje_debilidad = 0.0
    
    def calcular_porcentaje_debilidad(self, numero_preguntas):
        self.porcentaje_debilidad = round((self.fallos / numero_preguntas) * 100.0, 2)