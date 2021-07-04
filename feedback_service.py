from analyzer import *
import time
import models.db as db
import subprocess
from sqlalchemy import create_engine

def feedback_daemon():
    tracking_list = []
    engine = create_engine(db.connection_string)

    while True:
        print("Buscando procesos de analisis a ejecutar")
        print("Consultando a la base de datos")

        with engine.connect() as con:
            sql = """
                SELECT * FROM proceso_feedback 
                WHERE 
                    estado = 'ENPROGRESO'"""
            rs = con.execute(sql)
            
            for row in rs:
                if (row[0] in tracking_list):
                    continue
                
                print("Se encontro Proceso feedback con id=" + str(row[0]))
                print("Determinando el tipo de analisis a realizar")
                p = FeedbackExamAnalyzer(int(row[1]), int(row[0]), int(row[2]), int(row[3]), row[4], row[5])
                p.start()
                tracking_list.append(row[0])
            
            time.sleep(5)
            tracking_list=[]
            print("Llegamos al final de tracking list")

feedback_daemon()