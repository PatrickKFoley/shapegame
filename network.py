import socket
import pickle, sys

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.2.28"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.init_request = self.connect()

    def getInitRequest(self):
        return self.init_request

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            response = self.client.recv(2048)
            if sys.getsizeof(response) > 0:
                print(response)
                return pickle.loads(response)
        except socket.error as error:
            print(str(error))


