from typing import List
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Float, DateTime, Table
from sqlalchemy_utils import database_exists, create_database
from server_files.database_classes import User, Shape
from sqlalchemy.orm import Mapped, sessionmaker, declarative_base, relationship, mapped_column, registry
import random, os, datetime

BaseClass = declarative_base()
Registry = registry()
Registry.configure()

# friends_ass = Table(
#     "friends",
#     BaseClass.metadata,
#     Column("user1_id", ForeignKey("users.id"), primary_key=True),
#     Column("user2_id", ForeignKey("users.id"), primary_key=True)
# )

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
    xp = Column("xp", Integer, default=0)
    num_owners = Column("num_owners", Integer, default=1)

    name = Column("name", String)
    title = Column("title", String)

    

    def __init__(self, owner_id, owner, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, creator_username, name, title):
        self.owner_id = owner_id
        self.owner = owner
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
        self.name = name
        self.title = title
    
    def __repr__(self):
        return f"({self.id}) {self.owner_id} {self.face_id} {self.color_id} {self.density} {self.velocity} {self.radius_min} {self.radius_max} {self.health} {self.dmg_multiplier} {self.luck} {self.team_size}"
        
connection_string = "postgresql://postgres:postgres@localhost/root/shapegame/shapegame/database.db"
engine = create_engine(connection_string, echo=True)
BaseClass.metadata.drop_all(bind=engine)
BaseClass.metadata.create_all(bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)


Session = sessionmaker(bind=engine)
session = Session()


session.query(Shape).delete()
session.query(User).delete()

try:
    user_1 = User("a")
    user_2 = User("b")
    
    session.add(user_1)
    session.add(user_2)
    session.commit()
except Exception as e:
    session.rollback()
    print(e)
