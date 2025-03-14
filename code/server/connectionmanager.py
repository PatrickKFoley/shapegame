import socket
import pickle
from .playerselections import PlayerSelections
from threading import Thread

class ConnectionManager:
    def __init__(self, method):
        # "method" used for connecting to another player
        # "STANDARD." for normal matchmaking pool, "P2P.MY_USERNAME.THEIR_USERNAME." for trying to connect with another user
        self.method = method

        # client used for socket operations (send/receive data)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # server connection information
        # server ip 
        # self.server = "172.105.17.177"

        # local ip
        self.server = "192.168.2.24"
        self.port = 5555
        self.addr = (self.server, self.port)

        # connect to the server, which returns your id
        # (0 or 1, essentially the order you and opponent connected)
        self.pid = int(self.connect())

        # predefine selections object used for game state management, and create the thread responsible for updating it
        self.selections: PlayerSelections | None = None
        self.thread = Thread(target=self.updatePlayerSelections)

    # initial connection to the server, returns server's first communication (your pid)
    def connect(self):
        try:
            self.client.connect(self.addr)

            # server makes the first communication, no need to store this
            self.client.recv(2048).decode()

            # send the server your method, used by server to determine your selections object
            self.client.send(str.encode(self.method))

            # next response is your pid
            return self.client.recv(2048).decode()
        
        except Exception as exception:
            print(f'Error connecting to server: {exception}')

    # asynchronously send data (not used for GET or READY)
    def asyncSend(self, data):
        try:
            self.client.send(str.encode(data))
        
        except Exception as exception:
            if exception.args[0] not in [10053, 10054]:
                print(f'Error sending data to server: {exception}')

    # create a thread to send the provided data (used above)
    def send(self, data):
        Thread(target=self.asyncSend(data)).start()

    # send data regarding ready state change
    def readyUp(self, data):
        try:
            self.client.send(str.encode("READY_{}.".format(data)))

            self.selections = pickle.loads(self.client.recv(4096))

        except Exception as exception:
            print(f'Error sending ready state to server: {exception}')

    # send get request for updated selections object (called asynchronously in getPlayerSelections)
    def updatePlayerSelections(self):
        try:
            self.client.send(str.encode("GET."))

            self.selections = pickle.loads(self.client.recv(4096))

        except Exception as exception:
            if exception.args[0] not in [10053, 10054]:
                print(f'Error updating selections object from server: {exception}')

    # ensure that the selections updater thread is alive, return the selections object
    def getPlayerSelections(self):
        if not self.thread.is_alive():
            # threads cannot be restarted, kill it and make a new one
            del self.thread
            self.thread = Thread(target=self.updatePlayerSelections)

            self.thread.start()

        return self.selections
