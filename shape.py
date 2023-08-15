from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseClass = declarative_base()

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