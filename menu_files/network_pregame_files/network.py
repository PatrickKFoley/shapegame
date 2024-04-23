import socket
import pickle, sys, random
from menu_files.network_pregame_files.pregame import Pregame
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
        self.thread = Thread(target=self.updatePregame)
        self.request_count = 0

    def getPlayer(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        
        except:
            pass

    def asyncSend(self, data):
        try:
            self.client.send(str.encode(data))
        
        except socket.error as error:
            print(str(error))

    def send(self, data):
        thread = Thread(target=self.asyncSend(data))
        thread.start()

    def readyUp(self, data):
        try:
            self.client.send(str.encode("READY_{}.".format(data)))

            response = pickle.loads(self.client.recv(4096))
            self.pregame = response
        except:
            pass

    def receive(self):
        try:
            self.pregame = pickle.loads(self.client.recv(4096))
        except:
            pass
        

    def updatePregame(self):
        try:
            self.client.send(str.encode("GET."))

            response = pickle.loads(self.client.recv(4096))
            self.pregame = response
        except Exception as e:
            print(e)

    def getPregame(self):
        if not self.thread.is_alive():
            del self.thread
            self.thread = Thread(target=self.updatePregame)

            self.thread.start()

        return self.pregame