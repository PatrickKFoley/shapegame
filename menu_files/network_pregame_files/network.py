import socket
import pickle
from menu_files.network_pregame_files.pregame import Pregame
from threading import Thread

class Network:
    def __init__(self, method):
        # "method" used for connecting to another player
        # "STANDARD." for normal matchmaking pool, "P2P.MY_USERNAME.THEIR_USERNAME." for trying to connect with another user
        self.method = method

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

            # server makes the first communication, no need to store this
            self.client.recv(2048).decode()

            # send the server your method, used by server to determine your pregame object
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
            # this exception is thrown after the server closes the connection to the client
            # if no one sent a kill signal to the server, this was an actual error
            if True not in self.pregame.kill:
                print(f'Error updating pregame object from server: {exception}')

    # ensure that the pregame updater thread is alive, return the pregame object
    def getPregame(self):
        if not self.thread.is_alive():
            # threads cannot be restarted, kill it and make a new one
            del self.thread
            self.thread = Thread(target=self.updatePregame)

            self.thread.start()

        return self.pregame
