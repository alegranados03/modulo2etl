from etlworker import *
import sys

worker = EtlComplexWorker(sys.argv[1])
worker.start()