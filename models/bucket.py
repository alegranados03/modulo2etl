class BucketTema():
    def __init__(self):
        self.preguntas = []
        self.temas = []
        self.buckets_deficiencias = []
        self.literales_correctos = []
        self.referencia_bucket_tema = None

class BucketDeficiencia():
    def __init__(self):
        self.deficiencia = -1
        self.literales = []