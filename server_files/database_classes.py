from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float, DateTime
from typing import List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, sessionmaker, declarative_base, relationship, mapped_column, registry
import datetime

BaseClass = declarative_base()

class User(BaseClass):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, unique=True, nullable=False)
    shape_tokens = Column("shape_tokens", Integer, default=5)

    shapes: Mapped[List["Shape"]] = relationship(back_populates="owner", cascade="all, delete")
    # friends: Mapped[List["User"]] = relationship(secondary=friends_ass, back_populates="user")

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return f"({self.id}) {self.username}"
    
class Shape(BaseClass):
    __tablename__ = "shapes"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column("owner_id", Integer, ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="shapes")

    created_on = Column("created_on", DateTime, default=datetime.datetime.utcnow())
    obtained_on = Column("obtained_on", DateTime, default=datetime.datetime.utcnow())
    created_by = Column("created_by", String)

    face_id = Column("face_id", Integer)
    color_id = Column("color_id", Integer)
    density = Column("density", Integer)
    velocity = Column("velocity", Integer)
    radius_min = Column("radius_min", Integer)
    radius_max = Column("radius_max", Integer)
    health = Column("health", Integer)
    dmg_multiplier = Column("dmg_multiplier", Float)
    luck = Column("luck", Float)
    team_size = Column("team_size", Integer)
    num_wins = Column("num_wins", Integer, default=0)
    level = Column("level", Integer, default=1)
    num_owners = Column("num_owners", Integer, default=1)

    

    def __init__(self, owner_id, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, creator_username):
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
        self.created_by = creator_username
    
    def __repr__(self):
        return f"({self.id}) {self.owner_id} {self.face_id} {self.color_id} {self.density} {self.velocity} {self.radius_min} {self.radius_max} {self.health} {self.dmg_multiplier} {self.luck} {self.team_size}"

    
# engine = create_engine("sqlite:///shapegame.db", echo=True)
# BaseClass.metadata.create_all(bind=engine)