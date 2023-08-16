from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from circledata import *
import random
import os

BaseClass = declarative_base()

if os.path.isfile("shapegame.db"):
    os.remove("shapegame.db")

class User(BaseClass):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    username = Column("username", String)

    def __init__(self, id, username):
        self.id = id
        self.username = username.lower()

    def __repr__(self):
        return f"({self.id}) {self.username}"

class Shape(BaseClass):
    __tablename__ = "shapes"

    id = Column("id", Integer, primary_key=True)
    owner_id = Column("owner_id", Integer, ForeignKey("users.id"))
    face_id = Column("face_id", Integer)
    color_id = Column("color_id", Integer)

    density = Column("density", Integer)
    velocity = Column("velocity", Integer)
    radius_min = Column("radius_min", Integer)
    radius_max = Column("radius_max", Integer)
    health = Column("health", Integer)
    dmg_multiplier = Column("dmg_multiplier", Integer)
    luck = Column("luck", Integer)
    team_size = Column("team_size", Integer)

    def __init__(self, id, owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size):
        self.id = id
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


def createShape(id, owner_id):
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

    return Shape(id, owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size)


engine = create_engine("sqlite:///shapegame.db", echo=True)
BaseClass.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

user_1 = User(1, "pat")
user_2 = User(2, "Aiden")
user_3 = User(3, "Camille")

session.add(user_1)
session.add(user_2)
session.add(user_3)

for j in range(1, 4):
    for i in range(10):
        shape = createShape(j * 10 + i, j)
        session.add(shape)

session.commit()