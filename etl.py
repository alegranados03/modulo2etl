from etlworker import *
import time
import models.db as db
import subprocess

tracking_list = []

def etl_daemon():
    while True:
        print("Buscando ETLs a ejecutar")
        print("Consultando a la base de datos")
    
        with db.engine.connect() as con:
            rs = con.execute("SELECT * FROM proceso_etls WHERE (tipo_etl = 'PROGRAMADO' AND fecha_hora < NOW() AND estado <> 'EJECUTANDO') OR (tipo_etl = 'INSTANTANEO' AND estado = 'ENPROGRESO')")
        
            for row in rs:
                if (row[0] in tracking_list):
                    continue
                
                print("Se encontro ETL con id=" + str(row[0]))
                print("Determinando el tipo de ETL a realizar")
                
                rs2 = con.execute("SELECT * FROM proceso_etl_paso_generalidades WHERE id_proceso_etl = " + str(row[0]))
                for row2 in rs2:
                    print("Iniciando la ejecucion del proceso ETL")
                    if (row2[5] == "SIMPLE"):
                        p = subprocess.Popen(['python', 'etl_simple_worker.py', str(row[0])])
                    else:
                        p = subprocess.Popen(['python', 'etl_complex_worker.py', str(row[0])])
                
                tracking_list.append(row[0])
            
            time.sleep(5)


etl_daemon()