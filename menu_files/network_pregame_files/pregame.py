class Pregame:
    def __init__(self, id):
        self.id = id
        self.ready = False

        # used for connecting players in p2p matchmaking only
        self.usernames = ["", ""]

        self.players_ready = [False, False]

        self.users_selected = [-1, -1]

        self.shape_ids = [-1, -1]

        self.user_ids = [-1, -1]

        self.keeps = [0, 0]

        self.seed = False

        self.kill = [False, False]

        self.winner = None

        self.xp_earned = None

    def __repr__(self):
        return "id: {} ready: {} players_ready: {} users_selected: {} shape_ids: {} user_ids: {} keeps: {} seed: {} kill: {}".format(self.id, self.ready, self.players_ready, self.users_selected, self.shape_ids, self.user_ids, self.keeps, self.seed, self.kill)
