from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_sesion
from sqlalchemy.ext.declarative import declarative_base



#(UserMixin,Base) for flask.login
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String) 
    role = Column(String)

    def __init__(name:str,email:str,password:str,role:str):
        self.name,self.email,self.password,self.role  = name,email,password,role

class Database:
    ENGINE = create_engine("sqlite:///example.db",connect_args={"check_same_thread": False},)
    SESSION = sessionmaker(bind = ENGINE)
    BASE = declarative_base()
    #thread-local session
    CURRENT_SESSION = scoped_sesion(SESSION)

    @staticmethod
    def createsuperuser(name:str = "admin",email:str = "admin@mail.com", password = "admin"):
        CURRENT_SESSION.add(User(name,email,password,role = "Admin")) 
        CURRENT_SESSION.commit()