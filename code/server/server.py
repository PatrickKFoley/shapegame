import socket, pickle, random, datetime, time
from _thread import *
from .playerselections import PlayerSelections
from createdb import User, Shape, GamePlayed

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Server:
    def __init__(self):
        
        self.SessionMaker = sessionmaker(bind=create_engine("sqlite:///shapegame.db", echo=True), autoflush=False)
        self.session = self.SessionMaker()

        self.games_played = 0
        self.seeds = []
        for i in range(1000): self.seeds.append(random.randint(1, 99999999999))

        self.pool_selections = {}
        self.p2p_selections = {}
        self.pool_id_count = 0
        self.p2p_id_count = 0

        self.failed = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind(("192.168.2.12", 5555))
            self.socket.listen()
            print('Server started!\n')

        except Exception as e:
            print(f'Could not start server: {e}')
            self.failed = True

    def handleClient(self, connection, pid, all_selections, game_id):
        session = self.SessionMaker()

        connection.send(str.encode(str(pid)))

        u0 = None
        u1 = None
        s0 = None
        s1 = None
        users: list[User] = []
        shapes: list[Shape] = []

        game_played = False

        while True:

            # try to get data
            try:
                data = connection.recv(4096).decode()
            except Exception as e:
                print(f'Error receiving data: {e}')
                break

            try:
                if game_id in all_selections:
                    selections: PlayerSelections = all_selections[game_id]

                    if not data: break
                    else:

                        # apply changes to selections
                        selections.update(data, pid, connection, self.seeds)

                        # check if player disconnected
                        if selections.kill[pid]: break

                        # if players are ready and the game has not been simulated
                        if selections.players_ready[0] and selections.players_ready[1] and not game_played:

                            # player 0 signals the game to be simulated
                            if pid == 0:

                                # u0 = session.query(User).filter(User.id == int(selections.user_ids[0])).first()
                                # u1 = session.query(User).filter(User.id == int(selections.user_ids[1])).first()
                                # users = [u0, u1]

                                # s0 = session.query(Shape).filter(Shape.id == int(selections.shape_ids[0]))
                                # s1 = session.query(Shape).filter(Shape.id == int(selections.shape_ids[1]))
                                # shapes = [s0, s1]

                                # winner is the pid of the winning client
                                
                                t = time.time()
                                while time.time() - t < 5: pass
                                selections.winner = random.choice([0, 1])
                                print(f'winner: {selections.winner}')
                                game_played = True

                                # determine xp gained
                                selections.xp_earned = 10

                                connection.sendall(pickle.dumps(selections))

                            # player 0 waits for the winner to be named
                            elif pid == 1:
                                game_played = True

                                while selections.winner == None: pass
                                
                                connection.sendall(pickle.dumps(selections))

                        # after the simulation is done, player 0 signals the outcome to be reflected, player 1 does nothing
                        if game_played:
                            print('game played')

                            if pid == 1: break

                            if pid == 0:

                                # # if game was played for keeps, alter shape entries
                                # if selections.keeps[0] and selections.keeps[1]:

                                #     # alter shape data
                                #     shapes[0 if selections.winner == 1 else 1].owner_id = users[selections.winner].id
                                #     shapes[0 if selections.winner == 1 else 1].owner = users[selections.winner]
                                #     shapes[0 if selections.winner == 1 else 1].num_owners += 1
                                #     shapes[0 if selections.winner == 1 else 1].obtained_on = datetime.datetime.utcnow()

                                #     # reward the player a shape token if they are out of tokens and shapes
                                #     if len(users[0 if selections.winner == 1 else 1].shapes) == users[0 if selections.winner == 1 else 1].shape_tokens == 0:
                                #         users[0 if selections.winner == 1 else 1].shape_tokens += 1

                                #     # handle user losing their favorite shape
                                #     if shapes[0 if selections.winner == 1 else 1].id == users[0 if selections.winner == 1 else 1].favorite_id:
                                #         users[0 if selections.winner == 1 else 1].favorite_id = None

                                # # reward the winning shape and punish the losing shape
                                # shapes[selections.winner].num_wins += 1
                                # shapes[selections.winner].xp += selections.xp_earned
                                # shapes[0 if selections.winner == 1 else 1].num_losses += 1

                                # # add game_played entry to database
                                # session.add(GamePlayed(u0.id, u1.id, s0.id, s1.id, users[selections.winner].id))

                                # session.commit()
                                self.seeds.pop(0)
                                break

                else:
                    selections = PlayerSelections(-1)
                    selections.kill = [True, True]
                    connection.sendall(pickle.dumps(selections))

                    print('game_id not in selections collection')
                    break
            
            except Exception as e:
                print(f'Encountered error during selection handling: {e}')
                break

        print(f'Connection lost: pid: {pid}')

        # decrement player counters
        if selections == self.pool_selections: self.pool_id_count -= 1
        else: self.p2p_id_count -= 1
        connection.close()

        # delete selections entry
        try: 
            if all_selections == self.pool_selections:
                del self.pool_selections[game_id]
            else: del self.p2p_selections[game_id]

            print('deleted')
            self.seeds.pop(0)
        except: pass

    def start(self):
        while True:
            connection, addr = self.socket.accept()
            print("Connected to: ", addr)

            # server has to send first communication before client can send their method
            connection.send(str.encode(str("Server is ready")))

            try:
                client_method = connection.recv(4096).decode()
            except Exception:
                print(f'Error getting initial client communication')
                break


            if client_method == "STANDARD.":
                self.pool_id_count += 1
                player = 0
                game_id = (self.pool_id_count - 1) // 2

                if self.pool_id_count % 2 == 1:
                    self.pool_selections[game_id] = PlayerSelections(game_id)
                    print("Creating a new game...")
                else:
                    self.pool_selections[game_id].ready = True
                    player = 1

                start_new_thread(self.handleClient, (connection, player, self.pool_selections, game_id))

            elif "P2P" in client_method:
                self.p2p_id_count += 1

                # get usernames from the method
                client_username = client_method.split(".")[1]
                opponent_username = client_method.split(".")[2]

                # pid changes if you are the client making the selections
                pid = 1

                # check if a selections has already been made for you and opponent
                game_id = -1

                for index, (key, selections) in enumerate(self.p2p_selections.items()):
                    if client_username in selections.usernames and opponent_username in selections.usernames:

                        game_id = index
                        print(f'Joining game {game_id} for {client_username} and {opponent_username}')
                        self.p2p_selections[game_id].ready = True
                        # break

                # if selections doesn't exist, make one
                if game_id == -1:
                    pid = 0
                    game_id = (self.p2p_id_count - 1) // 2
                    
                    print(f'Creating game {game_id} for {client_username} and {opponent_username}')

                    new_selections = PlayerSelections(game_id)
                    new_selections.usernames = [client_username, opponent_username]
                    self.p2p_selections[game_id] = new_selections

                start_new_thread(self.handleClient, (connection, pid, self.p2p_selections, game_id))