import socket
import pickle
from menu_files.network_pregame_files.pregame import Pregame
from threading import Thread

class Network:
    def __init__(self):
        # client used for socket operations (send/receive data)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # server connection information
        self.server = "172.105.8.221"
        self.port = 5555
        self.addr = (self.server, self.port)

        # connect to the server, which returns your id
        # (0 or 1, essentially the order you and opponent connected)
        self.pid = self.connect()

        # predefine pregame object used for game state management, and create the thread responsible for updating it
        self.pregame: Pregame | None = None
        self.thread = Thread(target=self.updatePregame)

    # initial connection to the server, returns server's first communication (your pid)
    def connect(self):
        try:
            self.client.connect(self.addr)

            return self.client.recv(2048).decode()
        
        except Exception as exception:
            print(f'Error connecting to server: {exception}')

    # asynchronously send data (not used for GET or READY)
    def asyncSend(self, data):
        try:
            self.client.send(str.encode(data))
        
        except Exception as exception:
            print(f'Error sending data to server: {exception}')

    # create a thread to send the provided data (used above)
    def send(self, data):
        Thread(target=self.asyncSend(data)).start()

    # send data regarding ready state change
    def readyUp(self, data):
        try:
            self.client.send(str.encode("READY_{}.".format(data)))

            self.pregame = pickle.loads(self.client.recv(4096))

        except Exception as exception:
            print(f'Error sending ready state to server: {exception}')

    # send get request for updated pregame object (called asynchronously in getPregame)
    def updatePregame(self):
        try:
            self.client.send(str.encode("GET."))

            self.pregame = pickle.loads(self.client.recv(4096))

        except Exception as exception:
            print(f'Error sending ready state to server: {exception}')

    # ensure that the pregame updater thread is alive, return the pregame object
    def getPregame(self):
        if not self.thread.is_alive():
            # threads cannot be restarted, kill it and make a new one
            del self.thread
            self.thread = Thread(target=self.updatePregame)

            self.thread.start()

        return self.pregame
