import socket
import pickle, sys

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname("shapegame-server.onrender.com")
        print(self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player = self.connect()

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

            try: response = pickle.loads(self.client.recv(4096))
            except: response = None

            return response
        
        except socket.error as error:
            print(str(error))


