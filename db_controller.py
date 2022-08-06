from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData,Table, Column,Integer, String

class Database:
    engine = create_engine("sqlite:///example.db",connect_args={"check_same_thread": False},)
    base = declarative_base()
    metadata = MetaData
    session = sessionmaker(bind = engine)
    #thread-local session
    current_session = scoped_session(session)

    @classmethod
    def createall(self):
        self.base.metadata.create_all(self.engine)

    @classmethod
    def createsuperuser(self,name:str = "admin",email:str = "admin@mail.com", password = "admin"):
        role = "Admin"
        user = User(name,email,password,role)
        self.current_session.add(user) 
        self.current_session.commit()
        
DB = Database()
 #(UserMixin,DB.base) for flask.login
class User(DB.base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String) 
    role = Column(String)

    def __init__(self,name:str,email:str,password:str,role:str):
        self.name,self.email,self.password,self.role  = name,email,password,role

DB.createall()
DB.createsuperuser()
