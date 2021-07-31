from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine("mysql+mysqldb://root@localhost/testdata")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()


class ReportBuilderConnection():
    def __init__(self):
        # Crear objetos iniciales
        self.engine = create_engine("mysql+mysqldb://root@localhost/datatesis")
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.session = self.Session()