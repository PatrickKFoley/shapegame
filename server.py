import socket, sys, pickle, random
from _thread import *
from request import Request

server = "192.168.2.28"
port = 5555
seeds = []
games_played = 0

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.bind((server, port))
except socket.error as error:
    print(str(error))

socket.listen(2)
print("Waiting for connection...")

requests = [Request(), Request()]
currentPlayer = 0

def threaded_client(conn, player):
    conn.send(pickle.dumps(requests[player]))
    reply = ""
    
    while True:
        try:
            data = pickle.loads(conn.recv(2048)) #2048 bits, increase if any issues
            requests[player] = data

            if not data:
                print("Disconnected!")
                break
            else:

                if requests[0].getReady() == requests[1].getReady() == True:
                    requests[0].setReady(seeds[games_played])
                    requests[1].setReady(seeds[games_played])
                    games_played += 1

                if player == 1:
                    reply = requests[0]
                else:
                    reply = requests[1]
                # print("Received: ", data)
                # print("Sending: ", reply)

            print(sys.getsizeof(reply))

            conn.sendall(pickle.dumps(reply))

        except:
            break

    print("Lost connection!")
    conn.close()

for i in range(100):
    seeds.append(random.randint(0, 1))

while True:
    conn, addr = socket.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1