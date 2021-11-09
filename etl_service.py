from etl import *
import time
import models.db as db
import subprocess
from sqlalchemy import create_engine


def etl_daemon():
    tracking_list = []
    engine = create_engine(db.connection_string)
    while True:
        print("Buscando ETLs a ejecutar")
        print("Consultando a la base de datos")
    
        with engine.connect() as con:
            rs = con.execute("SELECT * FROM proceso_etls WHERE (tipo_etl = 'PROGRAMADO' AND fecha_hora < NOW() AND estado <> 'EJECUTANDO' AND estado <> 'TERMINADO') OR (tipo_etl = 'INSTANTANEO' AND estado = 'ENPROGRESO' AND estado <> 'TERMINADO')")
        
            for row in rs:
                if (row[0] in tracking_list):
                    continue
                
                print("Se encontro ETL con id=" + str(row[0]))
                print("Determinando el tipo de ETL a realizar")
                
                rs2 = con.execute("SELECT * FROM proceso_etl_paso_generalidades WHERE id_proceso_etl = " + str(row[0]))
                for row2 in rs2:
                    print("Iniciando la ejecucion del proceso ETL")
                    #Para ubuntu si tenes python 3, se pone python3 cuando el subproceso se abre
                    if (row2[5] == "SIMPLE"):
                        print("simple")
                        #p = subprocess.Popen(['python', 'etl_simple_worker.py', str(row[0])])
                        p = EtlSimpleWorker(str(row[0]))
                        p.start()
                        print("if fin")
                    else:
                        print("else")
                        #p = subprocess.Popen(['python', 'etl_complex_worker.py', str(row[0])])
                        p = EtlComplexWorker(str(row[0]))
                        p.start()
                        print("else fin")
                
                tracking_list.append(row[0])
            
            time.sleep(5)
            tracking_list=[]
            print("Llegamos al final de tracking list")

etl_daemon()