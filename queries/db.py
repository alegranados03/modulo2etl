from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine("mysql+mysqldb://root@localhost/testdata")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
