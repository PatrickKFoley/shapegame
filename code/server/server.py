import socket, pickle, random, datetime, time
from _thread import *
from .playerselections import PlayerSelections
from createdb import User, Shape, GamePlayed

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Server:
    def __init__(self):
        
        self.SessionMaker = sessionmaker(bind=create_engine("sqlite:///database.db", echo=False), autoflush=False)
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

                                u0 = session.query(User).filter(User.id == int(selections.user_ids[0])).first()
                                u1 = session.query(User).filter(User.id == int(selections.user_ids[1])).first()
                                users = [u0, u1]

                                print(selections.shape_ids[0], selections.shape_ids[1])
                                s0 = session.query(Shape).filter(Shape.id == int(selections.shape_ids[0])).first()
                                s1 = session.query(Shape).filter(Shape.id == int(selections.shape_ids[1])).first()
                                shapes = [s0, s1]

                                # simulate game to determine winner                                
                                t = time.time()
                                while time.time() - t < 5: pass
                                winner_pid = random.choice([0, 1])
                                print(f'winner: {winner_pid}')
                                game_played = True

                                # determine winner & loser
                                loser_pid = 0 if winner_pid == 1 else 1
                                winner: User = users[winner_pid]
                                loser: User = users[loser_pid]
                                winner_shape: Shape = shapes[winner_pid]
                                loser_shape: Shape = shapes[loser_pid]

                                # record results (non-keeps related things)
                                winner.num_wins += 1
                                winner_shape.num_wins += 1
                                loser_shape.num_losses += 1

                                game_entry = GamePlayed(users[0].id, users[1].id, shapes[0].id, shapes[1].id, winner.id)
                                session.add(game_entry)

                                # shuffle shapes

                                loser_lost_last_shape = False
                                if selections.keeps[0] and selections.keeps[1]:
                                    winner.num_shapes += 1
                                    loser.num_shapes -= 1

                                    loser_shape.owner_id = winner.id
                                    loser_shape.num_owners += 1
                                    loser_shape.obtained_on = datetime.datetime.utcnow()

                                    # remove user's favorite shape if they are losing it  
                                    if loser_shape.id == loser.favorite_id: loser.favorite_id = -1

                                    # # don't let user run out of shapes and shape tokes
                                    if loser.num_shapes == 0 and int(loser.shape_essence) == 0:
                                        loser_lost_last_shape = True
                                    # DO THIS WITH SHAPE ESS

                                # determine xp gained
                                selections.xp_earned = 10
                                # MAKE THE CHANGE TO REWARD MORE SHAPE ESS, USE THAT TO LEVEL UP SHAPES
                                amount = round(random.uniform(0.5, 1.0), 2)
                                loser_amount = round(amount/4, 2)
                                if selections.keeps[0] and selections.keeps[1]: amount *= 2 # if game was played for keeps, double the reward of the winner
                                print(f'determined shape ess amount: {amount, loser_amount}')

                                selections.essence_earned = [loser_amount, amount]
                                selections.winner = winner_pid # do this last, as it signals the other thread to send the last selections object

                                if loser_lost_last_shape:
                                    selections.essence_earned[0] += 1
                                    selections.essence_earned[0] = max(selections.essence_earned[0], 1)  # Ensure minimum value is 1
                                    selections.essence_earned[1] = max(selections.essence_earned[1], selections.essence_earned[0])  # Ensure the other value is the maximum

                                session.commit()
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

            self.seeds.pop(0)
        except: pass

    def handleClientPregame(self, connection, pid, all_selections, game_id):
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
                    # no need for this I bet
                    else:

                        # apply changes to selections
                        selections.update(data, pid, connection, self.seeds)

                        # check if player disconnected
                        if selections.kill[pid]: break

                        # if players are ready and the game has not been simulated
                        if selections.players_ready[0] and selections.players_ready[1] and not game_played:

                            # enter handling for game
                            self.handleClientGame(connection, pid, all_selections, game_id)
                            print('finished game?')
                            
                            # player 0 signals the game to be simulated
                            if pid == 0:

                                u0 = session.query(User).filter(User.id == int(selections.user_ids[0])).first()
                                u1 = session.query(User).filter(User.id == int(selections.user_ids[1])).first()
                                users = [u0, u1]

                                print(selections.shape_ids[0], selections.shape_ids[1])
                                s0 = session.query(Shape).filter(Shape.id == int(selections.shape_ids[0])).first()
                                s1 = session.query(Shape).filter(Shape.id == int(selections.shape_ids[1])).first()
                                shapes = [s0, s1]

                                # simulate game to determine winner                                
                                t = time.time()
                                while time.time() - t < 5: pass
                                winner_pid = random.choice([0, 1])
                                print(f'winner: {winner_pid}')
                                game_played = True

                                # determine winner & loser
                                loser_pid = 0 if winner_pid == 1 else 1
                                winner: User = users[winner_pid]
                                loser: User = users[loser_pid]
                                winner_shape: Shape = shapes[winner_pid]
                                loser_shape: Shape = shapes[loser_pid]

                                # record results (non-keeps related things)
                                winner.num_wins += 1
                                winner_shape.num_wins += 1
                                loser_shape.num_losses += 1

                                game_entry = GamePlayed(users[0].id, users[1].id, shapes[0].id, shapes[1].id, winner.id)
                                session.add(game_entry)

                                # shuffle shapes

                                loser_lost_last_shape = False
                                if selections.keeps[0] and selections.keeps[1]:
                                    winner.num_shapes += 1
                                    loser.num_shapes -= 1

                                    loser_shape.owner_id = winner.id
                                    loser_shape.num_owners += 1
                                    loser_shape.obtained_on = datetime.datetime.utcnow()

                                    # remove user's favorite shape if they are losing it  
                                    if loser_shape.id == loser.favorite_id: loser.favorite_id = -1

                                    # # don't let user run out of shapes and shape tokes
                                    if loser.num_shapes == 0 and int(loser.shape_essence) == 0:
                                        loser_lost_last_shape = True
                                    # DO THIS WITH SHAPE ESS

                                # determine xp gained
                                selections.xp_earned = 10
                                # MAKE THE CHANGE TO REWARD MORE SHAPE ESS, USE THAT TO LEVEL UP SHAPES
                                amount = round(random.uniform(0.5, 1.0), 2)
                                loser_amount = round(amount/4, 2)
                                if selections.keeps[0] and selections.keeps[1]: amount *= 2 # if game was played for keeps, double the reward of the winner
                                print(f'determined shape ess amount: {amount, loser_amount}')

                                selections.essence_earned = [loser_amount, amount]
                                selections.winner = winner_pid # do this last, as it signals the other thread to send the last selections object

                                if loser_lost_last_shape:
                                    selections.essence_earned[0] += 1
                                    selections.essence_earned[0] = max(selections.essence_earned[0], 1)  # Ensure minimum value is 1
                                    selections.essence_earned[1] = max(selections.essence_earned[1], selections.essence_earned[0])  # Ensure the other value is the maximum

                                session.commit()
                                connection.sendall(pickle.dumps(selections))

                            # player 0 waits for the winner to be named
                            elif pid == 1:
                                game_played = True

                                while selections.winner == None: pass
                                
                                connection.sendall(pickle.dumps(selections))

                        # after the simulation is done, player 0 signals the outcome to be reflected, player 1 does nothing
                        if game_played:
                            if pid == 1: break
                            if pid == 0: self.seeds.pop(0); break

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

            self.seeds.pop(0)
        except: pass

    def handleClientGame(self, connection, pid, all_selections, game_id):


        while all_selections[game_id].winners[pid] == None:

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
                        selections.update(data, pid, connection, self.seeds)

                        if selections.kill[pid]: 
                            selections.kill[pid] = False
                            break

                        if pid == 0:

                            # check if both players have subbitted a timestamp for the challenge
                            if len(selections.challenges_completed[0]) > selections.num_challenges_completed and len(selections.challenges_completed[1]) > selections.num_challenges_completed:

                                selections.num_challenges_completed += 1

                                winner_pid = 0 if selections.challenges_completed[0][selections.num_challenges_completed] >= selections.challenges_completed[1][selections.num_challenges_completed] else 1

                                frame_to_reward = max(selections.frames[0], selections.frames[1]) + 300
                                
                                selections.challenge_rewards = [winner_pid, frame_to_reward]

                                connection.sendall(pickle.dumps(selections))

                else:
                    selections = PlayerSelections(-1)
                    selections.kill = [True, True]
                    connection.sendall(pickle.dumps(selections))
                    break

            except Exception as e:
                print(f'Encountered error during selection handling: {e}')
                break
                        
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

                start_new_thread(self.handleClientPregame, (connection, pid, self.p2p_selections, game_id))