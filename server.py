import socket, pickle, random, datetime
from _thread import *
from menu_files.network_pregame_files.pregame import Pregame
from game_files.game import Game
from createdb import User, Shape
from game_files.circledata import *


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

connection_string = "postgresql://postgres:postgres@localhost/root/shapegame/shapegame/database.db"

BaseClass = declarative_base()
engine = create_engine(connection_string, echo=False)
BaseClass.metadata.create_all(bind=engine)
SessionMaker = sessionmaker(bind=engine)

server = ""
port = 5555
seeds = []
for i in range(1000): seeds.append(random.randint(1, 99999999999))

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.bind(("", 5555))
except Exception as e:
    print(f'Error binding socket {e}')
    raise SystemExit

socket.listen()
print("Waiting for connection...")

pool_pregames = {}
p2p_pregames = {}
pool_id_count = 0
p2p_id_count = 0

def processData(data):
    parts = data.split('.')

    user = None
    selected = None
    shape = None
    keeps = None
    ready = None
    kill = None
    get = None

    for part in parts:
        if part[:5] == "USER_":
            user = int(part[5:])

        elif part[:9] == "SELECTED_":
            selected = int(part[9:])

        elif part[:6] == "SHAPE_":
            shape = int(part[6:])

        elif part[:6] == "KEEPS_":
            keeps = int(part[6:])

        elif part[:6] == "READY_":
            ready = int(part[6:])

            ready = ready == 1

        elif part == "KILL":
            kill = True

        elif part == "GET":
            get = True
    
    return user, selected, shape, keeps, ready, kill, get

def handleClient(conn, player, pregames, game_id):
    session = SessionMaker()

    global pool_id_count
    global p2p_id_count

    conn.send(str.encode(str(player)))

    player0_id = None
    player1_id = None
    shape0 = None
    shape1 = None

    game_played = False

    while True:
        try:
            data = conn.recv(4096).decode()
        except Exception as err:
            print("----- ERROR RECIEVING DATA -----\n{}".format(err))
            break

        try:
            if game_id in pregames:
                pregame = pregames[game_id]

                if not data:
                    break
                else:
                    user, selected, shape, keeps, ready, kill, get = processData(data)

                    if user != None:
                        pregame.user_ids[player] = user
                    
                    if selected != None:
                        pregame.users_selected[player] = selected

                    if shape != None:
                        pregame.shape_ids[player] = shape

                    if keeps != None:
                        pregame.keeps[player] = keeps

                    if ready != None:
                        pregame.players_ready[player] = ready

                    if kill != None:
                        pregame.kill[player] = kill
                        break

                    if pregame.players_ready[0] and pregame.players_ready[1]:
                        pregame.seed = seeds[game_id]

                    # SECOND HALF TO ABOVE CHECK
                    if ready != None or get:
                        conn.sendall(pickle.dumps(pregame))

                    # One of the threads simulates the game
                    if player == 0 and pregame.players_ready[0] and pregame.players_ready[1] and not game_played:
                        # conn.sendall(pickle.dumps(pregame))

                        session.commit()

                        # print("USER IDS: {}".format(pregame.user_ids))
                        # print("SHAPE IDS: {}".format(pregame.shape_ids))

                        player0 = session.query(User).filter(User.id == int(pregame.user_ids[0])).first()
                        player1 = session.query(User).filter(User.id == int(pregame.user_ids[1])).first()

                        player0_id = player0.id
                        player0_username = player0.username

                        player1_id = player1.id
                        player1_username = player1.username

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

                        # PLACEHOLDER
                        pregame.xp_earned = random.randint(5, 20)

                        print(f'About to simulate game with id: {game_id}')

                        pregame.winner = Game(game_shape0, game_shape1, "", "", None, pregame.seed, False).play_game()

                        winner_username = player0_username
                        if pregame.winner == 1:
                            winner_username = player1_username

                        print(f'Game finished, winner: {winner_username}')
                        game_played = True

                        conn.sendall(pickle.dumps(pregame))

                    if game_played == True and player == 0:
                        if pregame.keeps[0] == 1 and pregame.keeps[1] == 1:
                            if pregame.winner == 0: 
                                shape1.owner_id = player0_id
                                shape1.owner = player0
                                shape1.num_owners += 1
                                shape1.obtained_on = datetime.datetime.utcnow()

                                if len(player1.shapes) == 0 and player1.shape_tokens == 0:
                                    player1.shape_tokens += 1
                            
                            else: 
                                shape0.owner_id = player1_id
                                shape0.owner = player1
                                shape0.num_owners += 1
                                shape0.obtained_on = datetime.datetime.utcnow()

                                if len(player0.shapes) == 0 and player0.shape_tokens == 0:
                                    player0.shape_tokens += 1

                        

                        if pregame.winner == 0: 
                            shape0.num_wins += 1
                            shape0.xp += pregame.xp_earned
                            shape1.num_losses += 1

                            for i, amount in enumerate(xp_amounts):
                                if shape0.xp >= amount:
                                    shape0.level = i + 1
                        
                        else: 
                            shape1.num_wins += 1
                            shape1.xp += pregame.xp_earned
                            shape0.num_losses += 1

                            for i, amount in enumerate(xp_amounts):
                                if shape1.xp >= amount:
                                    shape1.level = i + 1

                        session.commit()

                        del pregames[game_id]
                        seeds.pop(0)

                        break

                    if player == 1 and pregame.players_ready[0] and pregame.players_ready[1] and not game_played:
                        # conn.sendall(pickle.dumps(pregame))
                        game_played = True

                        while pregame.winner == None:
                            pass

                        conn.sendall(pickle.dumps(pregame))

                    if game_played == True and player == 1:
                        break

            else:
                print("----- GAME ID NOT IN PREGAMES -----")
                
                pregame = Pregame(-1)
                pregame.kill = [True, True]
                conn.sendall(pickle.dumps(pregame))

                break
        except Exception as err:
            print("----- ISSUE IN MAIN LOOP -----\n{}".format(err))
            break
    
    print("Lost connection! {}".format(player))

    if pregames == pool_pregames:
        pool_id_count -= 1
    else:
        p2p_id_count -= 1
    conn.close()

    if player == 0:
        try:
            del pregames[game_id]
            seeds.pop(0)

        except: pass

while True:
    conn, addr = socket.accept()
    print("Connected to: ", addr)

    # server has to send first communication before client can send their method
    conn.send(str.encode(str("Server is ready")))

    try:
        client_method = conn.recv(4096).decode()
    except Exception:
        print(f'Error getting initial client communication')
        break


    if client_method == "STANDARD.":
        pool_id_count += 1
        player = 0
        game_id = (pool_id_count - 1) // 2

        if pool_id_count % 2 == 1:
            pool_pregames[game_id] = Pregame(game_id)
            print("Creating a new game...")
        else:
            pool_pregames[game_id].ready = True
            player = 1

        start_new_thread(handleClient, (conn, player, pool_pregames, game_id))

    elif "P2P" in client_method:
        p2p_id_count += 1

        # get usernames from the method
        client_username = client_method.split(".")[1]
        opponent_username = client_method.split(".")[2]

        # pid changes if you are the client making the pregame
        pid = 1

        # check if a pregame has already been made for you and opponent
        game_id = -1

        for index, (key, pregame) in enumerate(p2p_pregames.items()):
            if client_username in pregame.usernames and opponent_username in pregame.usernames:
                game_id = index
                p2p_pregames[game_id].ready = True
                break

        # if pregame doesn't exist, make one
        if game_id == -1:
            pid = 0
            game_id = (p2p_id_count - 1) // 2
            
            print(f'Creating new game for {client_username} and {opponent_username}')

            new_pregame = Pregame(game_id)
            new_pregame.usernames = [client_username, opponent_username]
            p2p_pregames[game_id] = new_pregame

        start_new_thread(handleClient, (conn, pid, p2p_pregames, game_id))

        

