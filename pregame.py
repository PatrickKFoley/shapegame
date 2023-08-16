class Pregame:
    def __init__(self, id):
        self.id = id
        self.ready = False

        self.players_ready = [False, False]

        self.users_selected = [-1, -1]

        self.user_ids = [-1, -1]

        self.seed = False

