from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseClass = declarative_base()

class User(BaseClass):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, unique=True, nullable=False)
    shape_tokens = Column("shape_tokens", Integer)

    def __init__(self, username):
        self.username = username.lower()
        self.shape_tokens = 5


    def __repr__(self):
        return f"({self.id}) {self.username}"
    
# engine = create_engine("sqlite:///shapegame.db", echo=True)
# BaseClass.metadata.create_all(bind=engine)