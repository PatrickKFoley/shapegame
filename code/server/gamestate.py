import pickle

def processGameStateData(data):
    started, challenge, winner, get, kill, frame = None, None, None, None, None, None
    parts = data.split('.')

    for part in parts:
        if part[:10] == "CHALLENGE_":
            challenge = int(part[10:])

        elif part[:7] == "WINNER_":
            winner = int(part[7:])

        elif part[:6] == "FRAME_":  
            frame = int(part[6:])

        elif part == "STARTED":
            started = True

        elif part == "GET_GAME_STATE":
            get = True

        elif part == "KILL":
            kill = True

    return started, challenge, winner, get, kill, frame
            

class GameState:
    def __init__(self, game_id):
        self.game_id = game_id

        self.started = [False, False]
        '''if true, the game has started'''

        self.frames = [0, 0]

        self.challenges_completed = [[], []]
        '''when a player completes a challenge, the frame the challenge was completed on is added to the list'''

        self.winners = [None, None]
        '''the winner of the game, according to each player'''

        self.kill = [False, False]
        '''if kill signal is recieved from each player''' 

        self.num_challenges_completed = 0

        self.challenge_reward = [None, None]
        '''to who and when the next challenge is rewarded'''

    def __repr__(self):
        return f'GameState(game_id={self.game_id}, game_state={self.game_state})'

    def update(self, data, pid, connection):
        started, challenge, winner, get, kill, frame = processData(data)

        

        if kill != None:
            self.kill[pid] = kill

        if get:
            connection.sendall(pickle.dumps(self))
