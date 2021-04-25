from prueba_analyzer import *
import sys

worker = PruebaAnalyzer(sys.argv[1], sys.argv[2])
worker.start()