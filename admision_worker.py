from analyzer import *
import sys

worker = AdmisionAnalyzer(sys.argv[1])
worker.start()