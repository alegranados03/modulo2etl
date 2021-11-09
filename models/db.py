from sqlalchemy import create_engine, Table, Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

#Para Ubuntu(Testeado en la version 20.04)
#engine = create_engine("mysql+mysqldb://root@localhost:81/tesis?unix_socket=/opt/lampp/var/mysql/mysql.sock")

# Ejemplo Windows
connection_string = "mysql+mysqldb://root@localhost/tesis2020"

# Ejemplo Linux
# connection_string = "mysql+mysqldb://phpmyadmin:tesis2020$@localhost:3306/tesis2020"

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
TBL_TEMA_FK = "temas.id"
TBL_ETIQUETA_FK = 'etiquetas.id'
TBL_INSTITUCION_FK = 'instituciones.id'

TBL_EXAMEN_FK = "examenes.id"
TBL_PREGUNTA_FK = "preguntas.id"
TBL_SECCION_FK = "secciones.id"

TBL_BUCKET_TEMA_ADMISION_FK = "bucket_tema_adm.id"
TBL_BUCKET_TEMA_ADMISION_INSTITUTO_FK = "bucket_tema_adm_instituto.id"
TBL_BUCKET_DEFICIENCIA_ADMISION_FK = "bucket_deficiencia_adm.id"

TBL_BUCKET_TEMA_EXAMEN_PRUEBA_FK = "bucket_tema_exp.id"
TBL_BUCKET_TEMA_EXAMEN_PRUEBA_INSTITUTO_FK = "bucket_tema_exp_ins.id"
TBL_BUCKET_DEFICIENCIA_EXAMEN_PRUEBA_FK = "bucket_def_exp.id"

# Ejemplo Windows
RUTA_ARCHIVOS = "C:\\xampp\\htdocs\\Tesis-2020\\public\\csv\\"

# Ejemplo Linux
# RUTA_ARCHIVOS = "/var/www/Tesis-2020/public/csv/"


# Tablas intermedias para examenes de prueba
examen_preguntas = Table("examenes_preguntas", Database.metadata,
    Column("examen_id", Integer, ForeignKey(TBL_EXAMEN_FK)),
    Column("pregunta_id", Integer, ForeignKey(TBL_PREGUNTA_FK))
)

preguntas_temas = Table("preguntas_temas", Database.metadata,
    Column("pregunta_id", Integer, ForeignKey(TBL_PREGUNTA_FK)),
    Column("tema_id", Integer, ForeignKey(TBL_TEMA_FK))
)

# Declaracion de tablas intermedias de detalle para buckets de examen de admision
preguntas_examen_admision_temas = Table("preguntas_examen_admision_temas", Database.metadata,
    Column("id_pregunta_ex_adm", Integer, ForeignKey(TBL_PREGUNTA_EXAMEN_ADMISION_FK)),
    Column("tema_id", Integer, ForeignKey(TBL_TEMA_FK))
)

bucket_tema_adm_detalle = Table("bucket_tema_adm_detalle", Database.metadata,
    Column("bucket_tema_adm_id", Integer, ForeignKey(TBL_BUCKET_TEMA_ADMISION_FK)),
    Column("tema_id", Integer, ForeignKey(TBL_TEMA_FK))
)

# Declaracion de tablas intermedias de detalle para buckets de examenes de prueba
bucket_tema_exp_detalle = Table("bucket_tema_exp_detalle", Database.metadata,
    Column("bucket_tema_exp_id", Integer, ForeignKey(TBL_BUCKET_TEMA_EXAMEN_PRUEBA_FK)),
    Column("tema_id", Integer, ForeignKey(TBL_TEMA_FK))
)