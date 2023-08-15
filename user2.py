from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseClass = declarative_base()

class User(BaseClass):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    username = Column("username", String)

    def __init__(self, id, username):
        self.id = int(id)
        self.username = str(username).lower()

    def __repr__(self):
        return f"({self.id}) {self.username}"
    
# engine = create_engine("sqlite:///shapegame.db", echo=True)
# BaseClass.metadata.create_all(bind=engine)