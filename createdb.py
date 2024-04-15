from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Float
from sqlalchemy_utils import database_exists, create_database
import urllib.parse
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from circledata import *
from user import User
from shape import Shape
import random
import os

BaseClass = declarative_base()

# if os.path.isfile("shapegame.db"):
#     os.remove("shapegame.db")

class User(BaseClass):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, unique=True, nullable=False)
    shape_tokens = Column("shape_tokens", Integer)

    def __init__(self, username):
        self.username = username
        self.shape_tokens = 5


    def __repr__(self):
        return f"({self.id}) {self.username}"

class Shape(BaseClass):
    __tablename__ = "shapes"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    owner_id = Column("owner_id", Integer, ForeignKey("users.id"))
    face_id = Column("face_id", Integer)
    color_id = Column("color_id", Integer)
    num_wins = Column("num_wins", Integer, default=0)
    level = Column("level", Integer, default=1)

    density = Column("density", Integer)
    velocity = Column("velocity", Integer)
    radius_min = Column("radius_min", Integer)
    radius_max = Column("radius_max", Integer)
    health = Column("health", Integer)
    dmg_multiplier = Column("dmg_multiplier", Float)
    luck = Column("luck", Float)
    team_size = Column("team_size", Integer)

    def __init__(self, owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size):
        self.owner_id = owner_id
        self.face_id = face_id
        self.color_id = color_id
        self.density = density
        self.velocity = velocity
        self.radius_min = radius_min
        self.radius_max = radius_max
        self.health = health
        self.dmg_multiplier = dmg_multiplier
        self.luck = luck
        self.team_size = team_size

    def __repr__(self):
        return f"({self.id}) {self.owner_id} {self.face_id} {self.color_id} {self.density} {self.velocity} {self.radius_min} {self.radius_max} {self.health} {self.dmg_multiplier} {self.luck} {self.team_size}"

def createShape(owner_id):
    face_id = random.randint(0, 4)
    color_id = random.randint(0, len(colors)-1)

    base = circles_unchanged[face_id]

    density = base["density"]
    velocity = base["velocity"] + random.randint(-3, 3)
    radius_min = base["radius_min"] + random.randint(-3, 3)
    radius_max = base["radius_max"] + random.randint(-3, 3)
    health = base["health"] + random.randint(-100, 100)
    dmg_multiplier = base["dmg_multiplier"] + round((random.randint(-10, 10) / 10), 2)
    luck = base["luck"] + round((random.randint(-10, 10) / 10), 2)
    team_size = base["team_size"] + random.randint(-3, 3)

    return Shape(owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size)

connection_string = "postgresql://postgres:postgres@localhost/root/shapegame-server-2024/shapegame.db"

engine = create_engine(connection_string, echo=True)
if not database_exists(engine.url):
    create_database(engine.url)
BaseClass.metadata.drop_all(bind=engine)
BaseClass.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


session.query(Shape).delete()
session.query(User).delete()

try:
    user_1 = User("pat")
    shape_1 = createShape(1)

    user_2 = User("camille")
    shape_2 = createShape(2)
    
    session.add(user_1)
    session.add(user_2)
    session.commit()

    # session.add(shape_2)
    # session.add(shape_1)
    # session.commit()
except Exception as e:
    session.rollback()
    print(e)
