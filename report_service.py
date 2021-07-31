from report import *
import time
import models.db as db
import subprocess
from sqlalchemy import create_engine


def report_daemon():
    tracking_list = []
    engine = create_engine(db.connection_string)

    #while True:
    print("Buscando procesos de reporte a ejecutar")
    print("Consultando a la base de datos")

    with engine.connect() as con:
        sql = """
            SELECT * FROM parametros_analisis 
            WHERE estado = 'ENPROGRESO' """
        rs = con.execute(sql)
        
        for row in rs:
            if (row[0] in tracking_list):
                continue
            
            print("Se encontro proceso de reporte con id=" + str(row[0]))
            #print(row[1])

            p = ReportPopulator(row[0], row[1])
            p.start()
            
            tracking_list.append(row[0])
        
        #time.sleep(5)
        tracking_list=[]
        print("Llegamos al final de tracking list")

report_daemon()