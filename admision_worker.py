from analyzer import *
import sys

worker = AdmisionAnalyzer(sys.argv[1], sys.argv[2])
worker.start()