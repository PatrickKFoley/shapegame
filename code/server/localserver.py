import socket, pickle, random
from _thread import *
# from menu_files.network_pregame_files.pregame import Pregame
from playerselections import PlayerSelections
# from game_files.game import Game
from createdb import User, Shape
# from game_files.circledata import *

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseClass = declarative_base()
engine = create_engine("sqlite:///shapegame.db", echo=True)
BaseClass.metadata.create_all(bind=engine)
SessionMaker = sessionmaker(bind=engine)
# session = SessionMaker()

server = "192.168.2.12"
port = 5555
seeds = []
for i in range(1000): seeds.append(random.randint(1, 99999999999))
games_played = 0

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.bind((server, port))
except:
    print("Except")

socket.listen()
print("Waiting for connection...")

connected = set()
pregames = {}
id_count = 0

def threaded_client(conn, player, game_id):
    session = SessionMaker()

    global id_count
    conn.send(str.encode(str(player)))

    winner = 0
    player0_id = None
    player1_id = None
    shape0 = None
    shape1 = None

    reply = None
    game_played = False
    killed = False
    killed_counter = 0
    while True:
        data = conn.recv(4096).decode()

        try:
            if game_id in pregames:
                pregame = pregames[game_id]

                if not data:
                    # pass
                    break
                else:
                    if data[:5] == "USER_":
                        user_id = data[5:]

                        pregame.user_ids[player] = user_id
                    
                    elif data[:9] == "SELECTED_":
                        pregame.users_selected[player] = int(data[9:])

                    elif data[:6] == "SHAPE_":
                        pregame.shape_ids[player] = int(data[6:])

                    elif data[:6] == "KEEPS_":
                        pregame.keeps[player] = int(data[6:])

                    elif data == "READY":
                        pregame.players_ready[player] = True


                    elif data == "KILL":
                        pregame.kill[player] = True

                    if pregame.players_ready[0] and pregame.players_ready[1]:
                        pregame.seed = seeds[game_id]

                    # SECOND HALF TO ABOVE CHECK
                    if data == "READY":
                        reply = pregame
                        conn.sendall(pickle.dumps(reply))

                    if data in ["READY", "GET"]:
                        reply = pregame
                        conn.sendall(pickle.dumps(reply))

                    # One of the threads simulates the game

                    # print("------------ {} {} {} {} ------------".format(player, pregame.players_ready[0], pregame.players_ready[1], game_played))
                    if player == 0 and pregame.players_ready[0] and pregame.players_ready[1] and not game_played:
                        print("-----THANK GOD------")

                        reply = pregame
                        conn.sendall(pickle.dumps(reply))

                        session.commit()

                        print("USER IDS: {}".format(pregame.user_ids))
                        print("SHAPE IDS: {}".format(pregame.shape_ids))

                        player0_id = session.query(User).filter(User.id == int(pregame.user_ids[0])).first().id
                        player1_id = session.query(User).filter(User.id == int(pregame.user_ids[1])).first().id

                        shape0 = session.query(Shape).filter(Shape.id == int(pregame.shape_ids[0])).first()
                        shape1 = session.query(Shape).filter(Shape.id == int(pregame.shape_ids[1])).first()

                        game_shape0 = {}
                        game_shape0["group_id"] = 0
                        game_shape0["circle_id"] = 0
                        game_shape0["face_id"] = shape0.face_id
                        game_shape0["color"] = colors[shape0.color_id]
                        game_shape0["density"] = shape0.density
                        game_shape0["velocity"] = shape0.velocity
                        game_shape0["radius_min"] = shape0.radius_min
                        game_shape0["radius_max"] = shape0.radius_max
                        game_shape0["health"] = shape0.health
                        game_shape0["dmg_multiplier"] = shape0.dmg_multiplier
                        game_shape0["luck"] = shape0.luck
                        game_shape0["team_size"] = shape0.team_size

                        game_shape1 = {}
                        game_shape1["group_id"] = 1
                        game_shape1["circle_id"] = 0
                        game_shape1["face_id"] = shape1.face_id
                        game_shape1["color"] = colors[shape1.color_id]
                        game_shape1["density"] = shape1.density
                        game_shape1["velocity"] = shape1.velocity
                        game_shape1["radius_min"] = shape1.radius_min
                        game_shape1["radius_max"] = shape1.radius_max
                        game_shape1["health"] = shape1.health
                        game_shape1["dmg_multiplier"] = shape1.dmg_multiplier
                        game_shape1["luck"] = shape1.luck
                        game_shape1["team_size"] = shape1.team_size

                        print("ABOUT TO PLAY GAME")

                        winner = Game(game_shape0, game_shape1, "", "", None, pregame.seed, False).playGame()

                        print("GAME FINISHED: {}".format(winner))
                        game_played = True

                    if game_played == True and player == 0:
                        if pregame.keeps[0] == 1 and pregame.keeps[1] == 1:
                            if winner == 0: shape1.owner_id = player0_id
                            else: shape0.owner_id = player1_id

                        if winner == 0: shape0.num_wins += 1
                        else: shape1.num_wins += 1
                        session.commit()

                        # del pregames[game_id]
                        seeds.pop(0)

                        print("player 0 breaking")
                        break

                    if player == 1 and pregame.players_ready[0] and pregame.players_ready[1] and not game_played:
                        reply = pregame
                        conn.sendall(pickle.dumps(reply))
                        game_played = True

                    if game_played == True and player == 1:
                        print("player 1 breaking")
                        break
                    
                    # if not pregames[game_id]:
                    #     id_count -= 1
                    #     conn.close()
                    #     break

                    # if pregame.kill[0] and pregame.kill[1]:
                    #     id_count -= 1
                    #     conn.close()
                    #     break

            else:
                print("HUHHUH")
                break
        except Exception as e:
            print(e)
            break
    
    print("Lost connection! {}".format(player))

    # id_count -= 1
    conn.close()

    # # try to delete game
    # try: 
    #     # del pregames[game_id]
    #     print("Closing game: ", game_id); 
    #     seeds.pop(0)


    # except: pass

while True:
    conn, addr = socket.accept()
    print("Connected to: ", addr)

    id_count += 1
    player = 0
    game_id = (id_count - 1) // 2

    if id_count % 2 == 1:
        pregames[game_id] = PlayerSelections(game_id)
        print("Creating a new game...")
    else:
        pregames[game_id].ready = True
        player = 1

    start_new_thread(threaded_client, (conn, player, game_id))
