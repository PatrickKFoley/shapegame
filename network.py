import socket
import pickle, sys, random
from threading import Thread

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "172.105.8.221"

        # self.server = "192.168.2.12"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player = self.connect()
        self.pregame = None

    def getPlayer(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
        
        except socket.error as error:
            print(str(error))

    def readyUp(self):
        try:
            self.client.send(str.encode("READY"))

            response = pickle.loads(self.client.recv(4096))
            self.pregame = response
        except:
            pass

    def updatePregame(self):
        try:
            self.client.send(str.encode("GET"))

            response = pickle.loads(self.client.recv(4096))
            self.pregame = response
        except:
            pass

    def getPregame(self):
        thread = Thread(target=self.updatePregame)
        thread.start()
        thread.join()
        return self.pregame