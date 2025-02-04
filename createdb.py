from typing import List
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Float, DateTime, Table, Boolean
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Mapped, sessionmaker, declarative_base, relationship, mapped_column, registry, Session
import random, os, datetime
import bcrypt

from code.game.gamedata import color_data, shape_data as shape_model_data, names, titles


FRIEND_ADD = 'FRIEND'
FRIEND_CONFIRM = 'FRIEND_CONFIRM'
CHALLENGE = 'CHALLENGE'


BaseClass = declarative_base()

# Games Played Table
class GamePlayed(BaseClass):
    __tablename__ = "games_played"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Players involved
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Shapes used by each player
    shape1_id = Column(Integer, ForeignKey("shapes.id"), nullable=False)
    shape2_id = Column(Integer, ForeignKey("shapes.id"), nullable=False)
    
    # Winner of the game
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamp for when the entry was created
    time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])
    shape1 = relationship("Shape", foreign_keys=[shape1_id])
    shape2 = relationship("Shape", foreign_keys=[shape2_id])
    winner = relationship("User", foreign_keys=[winner_id])

    def __init__(self, player1_id, player2_id, shape1_id, shape2_id, winner_id):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.shape1_id = shape1_id
        self.shape2_id = shape2_id
        self.winner_id = winner_id

    def __repr__(self):
        return (f"<GamePlayed(player1_id={self.player1_id}, player2_id={self.player2_id}, "
                f"shape1_id={self.shape1_id}, shape2_id={self.shape2_id}, "
                f"winner_id={self.winner_id}, time={self.time})>")

friends = Table(
    "friends", BaseClass.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("friend_id", Integer, ForeignKey("users.id"), primary_key=True)
)
    
class Notification(BaseClass):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column("owner_id", Integer, ForeignKey("users.id"))
    sender_id: Mapped[int] = mapped_column("sender_id", Integer, ForeignKey("users.id"))

    # Relationships
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], back_populates="notifications_owned")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="notifications_sent")

    new = Column("new", Boolean, default=True)
    type = Column("type", String, nullable=False)

    def __init__(self, owner, sender, type):
        self.owner = owner
        self.sender = sender
        self.owner_id = self.owner.id
        self.sender_id = self.sender.id
        self.type = type

    def __repr__(self):
        return f'Notification(id={self.id}, type="{self.type}", owner_id={self.owner_id}, sender_id={self.sender_id})'

class User(BaseClass):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    favorite_id = Column("favorite_id", Integer, nullable=True, default=None)
    username = Column("username", String, unique=True, nullable=False)
    _password = Column("password", String, nullable=False)
    shape_tokens = Column("shape_tokens", Integer, default=5)
    shape_essence = Column("shape_essence", Float, default=0.0)
    num_shapes = Column("num_shapes", Integer, default=0)
    num_wins = Column("num_wins", Integer, default=0)
    date_joined = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # notifications: Mapped[List["Notification"]] = relationship(back_populates="owner", cascade="all, delete")
    notifications_owned = relationship("Notification", foreign_keys="Notification.owner_id", back_populates="owner", cascade="all, delete")
    notifications_sent = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender", cascade="all, delete")
    shapes: Mapped[List["Shape"]] = relationship(back_populates="owner", cascade="all, delete")
    friends: Mapped[List["User"]] = relationship("User", secondary=friends,
                                                 primaryjoin=id==friends.c.user_id,
                                                 secondaryjoin=id==friends.c.friend_id,
                                                 backref="friend_of")

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password: str):
        """Hash and set the password"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self._password = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify the provided password matches the stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))

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

    type = Column("type", String)
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
    num_losses = Column("num_losses", Integer, default=0)
    level = Column("level", Integer, default=10)
    xp = Column("xp", Integer, default=0)
    num_owners = Column("num_owners", Integer, default=1)

    name = Column("name", String)
    title = Column("title", String)

    

    def __init__(self, owner_id, owner, type, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_multiplier, luck, team_size, creator_username, name, title):
        self.type = type
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

def generateRandomShape(user: User, session):
    '''returns randomly generated ShapeData'''

    type = random.choices(['circle', 'triangle', 'square'], weights=[40, 40, 20], k=1)[0]
    face_id = 0
    color_id = random.randint(0, len(color_data)-1)
    density = 1
    velocity = shape_model_data[type].velocity + random.randint(-3, 3)
    radius_min = shape_model_data[type].radius_min + random.randint(-10, 10)
    radius_max = shape_model_data[type].radius_max + random.randint(-10, 10)
    health = shape_model_data[type].health + random.randint(-50, 50)
    dmg_x = round(shape_model_data[type].dmg_multiplier + (random.random() * random.choice([-1, 1])), 1)
    luck = shape_model_data[type].luck + random.randint(-5, 5)
    team_size = shape_model_data[type].team_size + random.randint(-3, 3)
    name = random.choice(names)
    title = titles[0]

    while radius_max <= radius_min: radius_max += 1

    shape_data = Shape(user.id, user, type, face_id, color_id, density, velocity, radius_min, radius_max, health, dmg_x, luck, team_size, user.username, name, title)

    user.shape_tokens -= 1
    user.num_shapes += 1

    session.add(shape_data)
    session.commit()

    return shape_data

if __name__ == "__main__":
    # string for server database connection
    # connection_string = "postgresql://postgres:postgres@localhost/root/shapegame/shapegame/database.db"
    
    # string for local database connection
    connection_string = "sqlite:///database.db"
    engine = create_engine(connection_string, echo=True)
    BaseClass.metadata.drop_all(bind=engine)
    BaseClass.metadata.create_all(bind=engine)

    if not database_exists(engine.url):
        create_database(engine.url)

    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Shape).delete()
    session.query(Notification).delete()
    session.query(User).delete()

    try:
        user_1 = User("pat", "1")
        user_2 = User("camille", "1")
        user_3 = User("aiden", "password123")
        user_4 = User("kyra", "password123")
        user_5 = User("zack", "password123")
        user_6 = User("deborah", "password123")

        session.add(user_1)
        session.add(user_2)
        session.add(user_3)
        session.add(user_4)
        session.add(user_5)
        session.add(user_6)

        for i in range(10):
            session.add(User(f'{i}', f'password{i}'))

        user_1.friends.append(user_2)
        user_1.friends.append(user_3)
        user_1.friends.append(user_4)
        user_1.friends.append(user_5)
        # user_1.friends.append(user_6)

        session.commit()
        
        
        session.add(Notification(user_1, user_2, "FRIEND"))
        session.add(Notification(user_1, user_3, "FRIEND_CONFIRM"))
        session.add(Notification(user_1, user_4, "CHALLENGE"))
        session.add(Notification(user_1, user_2, "CHALLENGE"))
        
        session.add(Notification(user_3, user_1, "FRIEND"))
        session.add(Notification(user_3, user_1, "CHALLENGE"))
        session.add(Notification(user_3, user_1, "CHALLENGE"))
        session.add(Notification(user_3, user_1, "CHALLENGE"))
        session.add(Notification(user_3, user_1, "CHALLENGE"))


        shape_1 = generateRandomShape(user_1, session)
        shape_2 = generateRandomShape(user_2, session)
        shape_3 = generateRandomShape(user_3, session)
        shape_4 = generateRandomShape(user_4, session)
        shape_5 = generateRandomShape(user_5, session)
        
        session.query(User).filter(User.id == user_1.id).update({User.favorite_id: shape_1.id})
        session.query(User).filter(User.id == user_2.id).update({User.favorite_id: shape_2.id})
        session.query(User).filter(User.id == user_3.id).update({User.favorite_id: shape_3.id})
        session.query(User).filter(User.id == user_4.id).update({User.favorite_id: shape_4.id})
        session.query(User).filter(User.id == user_5.id).update({User.favorite_id: shape_5.id})
        session.commit()

        session.add(GamePlayed(user_1.id, user_2.id, shape_1.id, shape_2.id, user_1.id))
        session.commit()

    except Exception as e:
        session.rollback()
        print(e)
