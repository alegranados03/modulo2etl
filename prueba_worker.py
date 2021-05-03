from analyzer import *
import sys

worker = PruebaAnalyzer(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
worker.start()