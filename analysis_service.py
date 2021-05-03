from analyzer import *
import time
import models.db as db
import subprocess
from sqlalchemy import create_engine

def analysis_daemon():
    tracking_list = []
    engine = create_engine(db.connection_string)

    while True:
        print("Buscando procesos de analisis a ejecutar")
        print("Consultando a la base de datos")

        with engine.connect() as con:
            sql = "SELECT * FROM proceso_analisis WHERE (ejecutar_ahora = 0 AND fecha_hora < NOW() AND estado <> 'EJECUTANDO' AND estado <> 'TERMINADO' AND estado <> 'ERROR') OR (ejecutar_ahora = 1 AND estado = 'ENPROGRESO' AND estado <> 'TERMINADO')"
            rs = con.execute(sql)
            
            for row in rs:
                if (row[0] in tracking_list):
                    continue
                
                print("Se encontro ETL con id=" + str(row[0]))
                print("Determinando el tipo de analisis a realizar")
                
                if (row[2] == "ADMISION"):
                    p = AdmisionAnalyzer(row[7], row[0])
                    p.start()
                    print("INICIADO ANALISIS EXAMEN ADMISION")
                elif(row[2] == "PRUEBA"):
                    p = PruebaAnalyzer(row[4], row[8], row[0])
                    p.start()
                    print("INICIADO ANALISIS EXAMEN ADMISION")
                
                tracking_list.append(row[0])
            
            time.sleep(5)
            tracking_list=[]
            print("Llegamos al final de tracking list")

analysis_daemon()