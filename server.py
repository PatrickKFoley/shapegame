import socket, sys
from _thread import *

server = "192.168.2.28"
port = 5555

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.bind((server, port))
except socket.error as error:
    print(str(error))

socket.listen(2)
print("Waiting for connection...")

players = [[0, 0], [0, 0]]
currentPlayer = 0

def decodePlayer(string):
    tuple = string.split(",")
    return int(tuple[0]), int(tuple[1])

def encodePlayer(tuple):
    return str(tuple[0]) + "," + str(tuple[1])

def threaded_client(conn, player):
    conn.send(str.encode(encodePlayer(players[player])))
    reply = ""
    
    while True:
        try:
            data = decodePlayer(conn.recv(2048).decode()) #2048 bits, increase if any issues
            players[player] = data

            if not data:
                print("Disconnected!")
                break
            else:
                if player == 1:
                    reply = players[0]
                else:
                    reply = players[1]
                print("Received: ", data)
                print("Sending: ", reply)

            conn.sendall(str.encode(encodePlayer(reply)))

        except:
            break

    print("Lost connection!")
    conn.close()

while True:
    conn, addr = socket.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1