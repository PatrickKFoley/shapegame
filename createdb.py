from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
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


engine = create_engine("sqlite:///shapegame.db", echo=True)
BaseClass.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

user_1 = User(1, "pat")
user_2 = User(2, "Aiden")

shape_1 = Shape(1, 1, 2, 4, 1, 3, 30, 45, 260, 1.7, 8, 15)
shape_2 = Shape(2, 1, 4, 10, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_3 = Shape(3, 1, 1, 7, 1, 4, 69, 71, 750, 1.5, 8, 5)
shape_4 = Shape(4, 1, 2, 2, 1, 4, 33, 44, 750, 1.5, 8, 5)
shape_5 = Shape(5, 1, 4, 1, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_6 = Shape(6, 1, 3, 3, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_7 = Shape(7, 1, 0, 5, 1, 4, 75, 80, 750, 1.5, 8, 5)

shape_8 = Shape(8, 2, 2, 4, 1, 3, 30, 45, 260, 1.7, 8, 15)
shape_9 = Shape(9, 2, 4, 10, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_10 = Shape(10, 2, 1, 7, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_11 = Shape(11, 2, 2, 2, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_12 = Shape(12, 2, 4, 1, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_13 = Shape(13, 2, 3, 3, 1, 4, 75, 80, 750, 1.5, 8, 5)
shape_14 = Shape(14, 2, 0, 5, 1, 4, 75, 80, 750, 1.5, 8, 5)

# user_2 = User(2, "Aiden")
session.add(user_1)
session.add(user_2)
session.add(shape_1)
session.add(shape_2)
session.add(shape_3)
session.add(shape_4)
session.add(shape_5)
session.add(shape_6)
session.add(shape_7)

session.add(shape_8)
session.add(shape_9)
session.add(shape_10)
session.add(shape_11)
session.add(shape_12)
session.add(shape_13)
session.add(shape_14)

session.commit()