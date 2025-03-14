import pickle

def processData(data):
    '''process any data sent from user into their selections object'''

    parts = data.split('.')

    user = None
    locked = None
    selected = None
    shape = None
    keeps = None
    ready = None
    kill = None
    get = None

    for part in parts:
        if part[:5] == "USER_":
            user = int(part[5:])

        elif part[:9] == "SELECTED_":
            selected = int(part[9:])

        elif part[:6] == "SHAPE_":
            shape = int(part[6:])

        elif part[:6] == "READY_":
            ready = int(part[6:])

        elif part[:7] == 'LOCKED_':
            locked = int(part[7:])

        elif part[:6] == "KEEPS_":
            keeps = int(part[6:])

        elif part == "KILL":
            kill = True

        elif part == "GET":
            get = True
    
    return user, selected, shape, keeps, ready, kill, get, locked

class PlayerSelections:
    def __init__(self, id):
        self.id = id
        self.ready = False

        # used for connecting players in p2p matchmaking only
        self.usernames = ["", ""]

        self.players_ready = [False, False]

        self.users_selected = [-1, -1]

        self.shape_ids = [-1, -1]

        self.user_ids = [-1, -1]

        self.locked = [False, False]

        self.keeps = [False, False]

        self.seed = None

        self.kill = [False, False]

        self.winner = None

        self.essence_earned = [-1, -1]

    def __repr__(self):
        return "id: {} ready: {} players_ready: {} users_selected: {} shape_ids: {} user_ids: {} keeps: {} seed: {} kill: {}".format(self.id, self.ready, self.players_ready, self.users_selected, self.shape_ids, self.user_ids, self.keeps, self.seed, self.kill)

    def update(self, data, pid, connection, seeds):
        user, selected, shape, keeps, ready, kill, get, locked = processData(data)

        if user != None:
            self.user_ids[pid] = user
        
        if selected != None:
            self.users_selected[pid] = selected

        if locked != None:
            self.locked[pid] = locked

        if shape != None:
            self.shape_ids[pid] = shape

        if keeps != None:
            self.keeps[pid] = keeps

        if ready != None:
            self.players_ready[pid] = ready

        if kill != None:
            self.kill[pid] = kill

        if self.players_ready[0] and self.players_ready[1]:
            self.seed = seeds[self.id]

        if ready != None or get:
            # print(f'sending: {self}')
            connection.sendall(pickle.dumps(self))