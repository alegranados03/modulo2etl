from etlworker import *
import sys

worker = EtlSimpleWorker(sys.argv[1])
worker.start()