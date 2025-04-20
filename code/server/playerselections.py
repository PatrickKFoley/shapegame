import pickle
import threading
def processData(data):
    '''process any data sent from user into their selections object'''

    parts = data.split('.')

    started, challenge, winner, frame, exit = None, None, None, None, None
    
    user = None
    locked = None
    selected = None
    shape = None
    keeps = None
    ready = None
    kill_game = None
    kill_pregame = None
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

        if part[:10] == "CHALLENGE_":
            print(f'challenge completed on fram: {part[10:]}')
            challenge = int(part[10:])

        elif part[:7] == "WINNER_":
            winner = int(part[7:])

        elif part[:6] == "FRAME_":  
            frame = int(part[6:])

        elif part == "STARTED":
            started = True

        elif part == "KILL_GAME":
            kill_game = True

        elif part == "KILL_PREGAME":
            kill_pregame = True

        elif part == "GET":
            get = True

        elif part == "EXIT":
            exit = True
    
    return user, selected, shape, keeps, ready, kill_game, kill_pregame, get, locked, started, challenge, winner, frame, exit

class PlayerSelections:
    def __init__(self, id):
        self.id = id
        self.ready = False

        self.results_computed_flag = False
        self.results_computing_flag = False

        # ALL BELLOW NEEDED FOR NETWORK PREGAME

        # used for connecting players in p2p matchmaking only
        self.usernames = ["", ""]

        self.players_ready = [False, False]

        self.users_selected = [-1, -1]

        self.shape_ids = [-1, -1]

        self.user_ids = [-1, -1]

        self.locked = [False, False]

        self.keeps = [False, False]

        self.seed = None

        self.player_exit = [False, False] # if true, the player has exited the game
        self.kill_game = [False, False] # if true, the game has been stopped (finished simulating, if was necessary)
        self.kill_pregame = [False, False]
        self.player_quit = [False, False] # if true, a player's thread has finshed 

        self.winner = None

        self.essence_earned = [-1, -1]

        # ALL BELLOW NEEDED FOR NETWORK GAME

        self.started = [False, False]
        '''if true, the game has started'''

        self.frames = [0, 0]

        self.challenges_completed = [[], []]
        '''when a player completes a challenge, the frame the challenge was completed on is added to the list'''

        self.winners = [None, None]
        '''the winner of the game, according to each player'''

        self.num_challenges_completed = 0

        self.challenge_reward = [None, None]
        '''to who and when the next challenge is rewarded'''


        
    def __repr__(self):
        return "id: {} ready: {} players_ready: {} users_selected: {} shape_ids: {} user_ids: {} keeps: {} seed: {}".format(self.id, self.ready, self.players_ready, self.users_selected, self.shape_ids, self.user_ids, self.keeps, self.seed)

    def update(self, data, pid, connection, seeds):
        user, selected, shape, keeps, ready, kill_game, kill_pregame, get, locked, started, challenge, winner, frame, exit = processData(data)

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

        if started != None:
            self.started[pid] = True

        if challenge != None:
            # also update the frame the challenge was completed on
            self.frames[pid] = challenge
            self.challenges_completed[pid].append(challenge)

        if frame != None:
            self.frames[pid] = frame

        if winner != None:
            self.winners[pid] = winner

        if kill_game != None:
            self.kill_game[pid] = kill_game

        if kill_pregame != None:
            self.kill_pregame[pid] = kill_pregame

        if self.players_ready[0] and self.players_ready[1]:
            self.seed = seeds[self.id]

        if exit != None:
            self.player_exit[pid] = exit

        if ready != None or get:
            # print(f'sending: {self}')
            connection.sendall(pickle.dumps(self))