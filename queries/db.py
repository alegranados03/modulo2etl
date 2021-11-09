from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

# Ejemplo Windows
engine = create_engine("mysql+mysqldb://root@localhost/tesis2020")

# Ejemplo Linux
# engine = create_engine("mysql+mysqldb://phpmyadmin:tesis2020$@localhost:3306/tesis2020")

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()


class ReportBuilderConnection():
    def __init__(self):
        # Crear objetos iniciales
        # Ejemplo Windows
        self.engine = create_engine("mysql+mysqldb://root@localhost/tesis2020")
        
        # Ejemplo Linux
        # self.engine = create_engine("mysql+mysqldb://phpmyadmin:tesis2020$@localhost:3306/tesis2020")
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()