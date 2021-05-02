from analyzer import *
import sys

worker = PruebaAnalyzer(sys.argv[1], int(sys.argv[2]))
worker.start()