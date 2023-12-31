import socket, pickle, random
from _thread import *
from pregame import Pregame

server = "192.168.2.28"
port = 5555
seeds = []
for i in range(1000): seeds.append(random.randint(1, 99999999999))
games_played = 0

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.bind((server, port))
except:
    pass

socket.listen()
print("Waiting for connection...")

connected = set()
pregames = {}
id_count = 0

def threaded_client(conn, player, game_id):
    global id_count
    conn.send(str.encode(str(player)))

    reply = None
    while True:
        data = conn.recv(4096).decode()

        try:
            if game_id in pregames:
                pregame = pregames[game_id]

                if not data:
                    break
                else:
                    # if data[:5] == "FACE_":
                    #     pregame.faces[player] = int(data[5:])
                    # elif data[:6] == "COLOR_":
                    #     pregame.colors[player] = int(data[6:])
                    if data[:5] == "USER_":
                        user_id = data[5:]

                        pregame.user_ids[player] = user_id
                    
                    elif data[:9] == "SELECTED_":
                        pregame.users_selected[player] = int(data[9:])

                    elif data == "READY":
                        pregame.players_ready[player] = True

                    elif data == "KILL":
                        break

                    if pregame.players_ready[0] and pregame.players_ready[1]:
                        pregame.ready = True
                        pregame.seed = seeds[game_id]

                    reply = pregame
                    conn.sendall(pickle.dumps(reply))
            else:
                break
        except:
            break
    
    print("Lost connection!")

    # try to delete game
    try: del pregames[game_id]; print("Closing game: ", game_id); seeds.pop(0)
    except: pass

    id_count -= 1
    conn.close()

while True:
    conn, addr = socket.accept()
    print("Connected to: ", addr)

    id_count += 1
    player = 0
    game_id = (id_count - 1) // 2

    if id_count % 2 == 1:
        pregames[game_id] = Pregame(game_id)
        print("Creating a new game...")
    else:
        pregames[game_id].ready = True
        player = 1

    start_new_thread(threaded_client, (conn, player, game_id))