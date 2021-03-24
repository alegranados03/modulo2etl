from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine("mysql+mysqldb://root@localhost/laravel")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
#Session = sessionmaker(bind = engine)
session = Session()
Database = declarative_base()

TBL_PROCESO_ETL_FK = "proceso_etls.id_proceso_etl"
TBL_PROCESO_ETL_CARGA_PREGUNTAS = "proceso_etl_carga_preguntas.id_proceso_carga_preguntas"
TBL_PROCESO_ETL_CARGA_RESUMENES = "proceso_etl_carga_resumenes.id_proceso_carga_resumen"
TBL_PROCESO_ETL_CARGA_LITERALES_FK = "proceso_etl_carga_literales.id_proceso_carga_literales"
TBL_PROCESO_ETL_CARGA_RESPUESTAS_FK = "proceso_etl_carga_respuestas.id_proceso_carga_respuesta"
TBL_AREA_CONOCIMIENTO_FK = "secciones.id"
TBL_EXAMEN_ADMISION_FK = "examen_admision.id"
TBL_PREGUNTA_EXAMEN_ADMISION_FK = "pregunta_examen_admision.id"
TBL_LITERAL_EXAMEN_ADMISION_FK = "literal_examen_admision.id"

RUTA_ARCHIVOS = "C:\\xampp7\\htdocs\\Tesis-2020\\public\\csv\\"
