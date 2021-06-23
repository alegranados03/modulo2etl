from analyzer import *
from datetime import datetime
import sys

id_usuario = int(sys.argv[1])
id_proceso_feedback = int(sys.argv[2])
id_intento = int(sys.argv[3])
seccion_id = int(sys.argv[4])
fecha_inicio = datetime.strptime(sys.argv[5], '%Y-%m-%d %H:%M:%S')
fecha_fin = datetime.strptime(sys.argv[6], '%Y-%m-%d %H:%M:%S')

worker = FeedbackExamAnalyzer(id_usuario, id_proceso_feedback, id_intento, seccion_id, fecha_inicio, fecha_fin)
worker.start()