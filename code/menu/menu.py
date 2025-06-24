import math
import numpy
from pygame.locals import *
import pygame.mouse
from pygame.sprite import Group
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame.transform import smoothscale
from pygame.image import load
import pygame, time, itertools, sys, random
from typing import Union

from code.menu.menushape import MenuShape
from createdb import User, Shape as ShapeData, Notification, FRIEND_ADD, FRIEND_CONFIRM, CHALLENGE, generateRandomShape
from ..screen_elements.text import Text
from ..screen_elements.editabletext import EditableText
from ..screen_elements.clickabletext import ClickableText
from ..screen_elements.button import Button
from ..screen_elements.screenelement import ScreenElement
from ..game.gamedata import color_data, shape_data as shape_model_data, names, titles
from ..game.game2 import Game2
from .collection_window.collectionwindow import CollectionWindow
from .collection_window.collectionshape import CollectionShape
from .collection_window.movingshape import MovingShape
from .friends_window.friendswindow import FriendsWindow
from .friends_window.friendsprite import FriendSprite
from .notifications_window.notificationswindow import NotificationsWindow
from .notifications_window.notificationsprite import NotificationSprite
from ..server.connectionmanager import ConnectionManager
from ..server.playerselections import PlayerSelections
from sqlalchemy import create_engine, func, delete, select, case
from sqlalchemy.orm import sessionmaker as session_maker, Session
from ..game.gamedata import color_data, shape_data as shape_model_data, shape_names
from ..game.clouds2 import Clouds

from threading import Thread, Lock

NUM_MENU_SHAPES = 12

class Menu():
    def __init__(self):
        # load cursor and background
        self.screen = pygame.display.set_mode((1920, 1080))
        self.background = load('assets/backgrounds/BG1.png').convert_alpha()
        self.office_supplies = load('assets/backgrounds/grid_paper_w_sides_2.png').convert_alpha()
        self.cursor = smoothscale(load('assets/misc/cursor.png').convert_alpha(), (12, 12))
        self.cursor_rect = self.cursor.get_rect()
        self.cursor_rect.center = pygame.mouse.get_pos()

        # update the display
        self.title_text = Text('shapegame', 150, 1920/2, 2*1080/3, outline_color='white')
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.title_text.surface, self.title_text.rect)
        pygame.display.set_caption('shapegame')
        pygame.display.update()

        # misc attributes
        self.exit_clicked = False
        self.frames_since_exit_clicked = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('assets/misc/font.ttf', 80)
        
        self.target_fps = 60
        self.time_step = 1 / self.target_fps
        self.time_step_accumulator = 0
        self.current_time, self.prev_time = None, None
        self.frames = 0

        # database entries
        self.user: User | None = None
        self.prev_opponent: User | None = None

        # database session
        # self.engine = create_engine('postgresql://postgres:postgres@172.105.17.177/root/shapegame/shapegame/database.db', echo=False) # server db
        self.engine = create_engine('sqlite:///database.db', echo=False) # local db
        SessionMaker = session_maker(bind=self.engine, autoflush=False)
        self.session = SessionMaker()

        # sprite groups
        self.menu_shapes = Group()
        self.clouds_group = Group()
        self.moving_shapes = Group()

        # windows
        self.collection_window: CollectionWindow | None = None
        self.opponent_window: CollectionWindow | None = None
        self.friends_window: FriendsWindow | None = None
        self.notifications_window: NotificationsWindow | None = None

        self.connection_manager: ConnectionManager | None = None

        self.initSounds()
        self.initScreenElements()
        self.initMenuShapes()

        self.thread: Thread | None = None
        self.thread_running = False

        self.notification_poll_thread = None
        self.stop_notification_polling = False

        self.db_lock = Lock()

    # INIT HELPERS

    def initSounds(self):
        '''load all sounds'''
        
        self.click_sound = Sound('assets/sounds/click.wav')
        self.start_sound = Sound('assets/sounds/start.wav')
        self.open_sound = Sound('assets/sounds/open.wav')
        self.menu_music = Sound('assets/sounds/menu.wav')
        self.close_sound = Sound('assets/sounds/close.wav')
        self.open_sound.set_volume(.5)
        self.menu_music.set_volume(.15)
        self.close_sound.set_volume(.5)
        self.open_sound.play()

        self.death_sounds = []
        self.death_sounds.append(pygame.mixer.Sound('assets/sounds/death/1.wav'))
        self.death_sounds.append(pygame.mixer.Sound('assets/sounds/death/2.wav'))
        self.death_sounds.append(pygame.mixer.Sound('assets/sounds/death/3.wav'))
        self.death_sounds.append(pygame.mixer.Sound('assets/sounds/death/4.wav'))

        self.collision_sounds = []
        self.collision_sounds.append(pygame.mixer.Sound('assets/sounds/collisions/clink1.wav'))
        self.collision_sounds.append(pygame.mixer.Sound('assets/sounds/collisions/clink2.wav'))
        self.collision_sounds.append(pygame.mixer.Sound('assets/sounds/collisions/thud2.wav'))

        for sound in self.collision_sounds:
            sound.set_volume(.01)

        for sound in self.death_sounds:
            sound.set_volume(.10)

        # start playing menu music on loop
        self.menu_music.play(-1)

    def initScreenElements(self):
        '''create all screen elements'''

        # create all text elements
        self.logged_in_as_text: Text | None = None
        self.title_text = Text('shapegame', 150, 1920/2, 2*1080/3, outline_color='white')
        self.play_text = Text('play', 100, 1920/2, 4*1080/5, outline_color='white')
        self.connecting_to_text = Text('waiting for opponent...' , 35, 1920/2, 60)
        self.new_notification_text = Text('', 30, 1870, 0, align='topright', color='black', fast_off=True)

        # create all interactive elements
        self.network_match_clickable = ClickableText('network match', 50, 1920/2 - 200, 975, outline_color='white')
        self.local_match_clickable = ClickableText('local match', 50, 1920/2 + 200, 975, outline_color='white')
        self.exit_button = Button('exit', 45, [1920 - 25, 1080 - 25])
        self.back_button = Button('back', 45, [25, 1080 - 25])
        self.network_back_button = Button('exit', 45, [1920 - 25, 661 - 25])

        # login elements
        self.register_clickable = ClickableText('register', 50, 1920/2, 1030, outline_color='white')
        self.login_clickable = ClickableText('login', 50, 1920/2, 925, outline_color='white')
        self.or_text = Text('or', 35, 1920/2, 980, outline_color='white')
        self.logging_in_text = Text('logging in...', 40, 1920/2, 1030)

        self.username_editable = EditableText('Username: ', 60, 1920/3-50, 850, max_chars=10, outline_color='white')
        self.password_editable = EditableText('Password: ', 60, 2*1920/3+50, 850, max_chars=10, outline_color='white')
        self.password_confirm_editable = EditableText('Confirm Password: ', 50, 1920/2, 925, max_chars=10, outline_color='white')
        self.bad_credentials_text = Text('user not found!', 50, 1920/2, 600)
        self.bad_credentials_flag = False
        self.bad_credentials_timer = 0

        self.screen_elements: list[ScreenElement] = []
        self.screen_elements.append(self.title_text)
        self.screen_elements.append(self.play_text)
        self.screen_elements.append(self.connecting_to_text)
        self.screen_elements.append(self.network_back_button)
        self.screen_elements.append(self.login_clickable)
        self.screen_elements.append(self.network_match_clickable)
        self.screen_elements.append(self.local_match_clickable)
        self.screen_elements.append(self.exit_button)
        self.screen_elements.append(self.register_clickable)
        self.screen_elements.append(self.username_editable)
        self.screen_elements.append(self.password_editable)
        self.screen_elements.append(self.or_text)
        self.screen_elements.append(self.password_confirm_editable)
        self.screen_elements.append(self.bad_credentials_text)
        self.screen_elements.append(self.back_button)
        self.screen_elements.append(self.logging_in_text)
        self.screen_elements.append(self.new_notification_text)

        # show only title, exit, and login elements
        [element.fastOff() for element in self.screen_elements if element not in [self.title_text]]

    def initNetworkElements(self):

        self.pid = -1
        self.connection_manager: None | ConnectionManager =     None
        self.selections: None | PlayerSelections =              None
        self.opponent: None | User =                            None
        self.opponent_window: None | CollectionWindow =         None

    def initMenuShapes(self):
        '''initialize all shapes in the menu'''

        self.triangle_face_images = []
        for i in range(4):
            self.triangle_face_images.append(pygame.image.load(f'assets/shapes/faces/triangle/0/{i}.png').convert_alpha())

        self.square_face_images = []
        for i in range(4):
            self.square_face_images.append(pygame.image.load(f'assets/shapes/faces/square/0/{i}.png').convert_alpha())

        self.circle_face_images = []
        for i in range(4):
            self.circle_face_images.append(pygame.image.load(f'assets/shapes/faces/circle/0/{i}.png').convert_alpha())

        self.rhombus_face_images = []
        for i in range(4):
            self.rhombus_face_images.append(pygame.image.load(f'assets/shapes/faces/rhombus/0/{i}.png').convert_alpha())

        self.spiral_face_images = []
        for i in range(4):
            self.spiral_face_images.append(pygame.image.load(f'assets/shapes/faces/spiral/0/{i}.png').convert_alpha())
        
        self.cloud_images = []
        for i in range(5):
            self.cloud_images.append(pygame.transform.smoothscale(pygame.image.load(f'assets/powerups/screen_effects/clouds/{i}.png').convert_alpha(), [100, 100]))

        for i in range(NUM_MENU_SHAPES):
            shape_data = shape_model_data[random.choice(shape_names)]
            shape_data.color_id = random.randint(0, len(color_data) - 1)

            face_images = []
            if shape_data.type == 'triangle':
                face_images = self.triangle_face_images
            elif shape_data.type == 'square':
                face_images = self.square_face_images
            elif shape_data.type == 'circle':
                face_images = self.circle_face_images
            elif shape_data.type == 'rhombus':
                face_images = self.rhombus_face_images
            elif shape_data.type == 'spiral':
                face_images = self.spiral_face_images

            self.menu_shapes.add(MenuShape(i, shape_data, color_data[shape_data.color_id], face_images))

        # turn off all shapes
        [shape.turnOff() for shape in self.menu_shapes]

    # WINDOW CALLBACKS

    def startNetwork(self, opponent: Union[User, None] = None, send_notification: bool = True):

        # refresh database
        self.session.commit()
        
        # send notification to challenged user if necessary
        if send_notification: self.addDbNotification(opponent, self.user, CHALLENGE)

        # turn off auxiliary screen elements
        [shape.turnOff() for shape in self.menu_shapes]
        [window.close() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        [window.button.turnOff() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        self.notifications_window.sprite_count_text.turnOff()
        [element.turnOff() for element in self.screen_elements if element not in [self.title_text, self.logged_in_as_text, self.exit_button]]
        self.connecting_to_text.turnOn()

        if opponent: self.connecting_to_text.updateText(f'waiting for {opponent.username}...')
        else: self.connecting_to_text.updateText(f'waiting for opponent...')

        # create connection manager, send initial communication
        self.connection_manager = ConnectionManager('STANDARD.' if opponent == None else f'P2P.{self.user.username}.{opponent.username}')
        self.pid = self.connection_manager.pid
        self.selections = self.connection_manager.getPlayerSelections()
        self.connection_manager.send(f'USER_{self.user.id}.')


        # do network pregame
        self.network_connected = True
        self.preGame()
        
        # prepare game to be played if still connected
        if self.network_connected:
            # close windows before anything else
            while not self.collection_window.fully_closed or not self.opponent_window.fully_closed:

                self.updateMenuState()
                self.drawScreenElements()
                self.clock.tick(self.target_fps)

            # play game
            if self.pid == 0:
                Game2(
                    self.screen, 
                    self.collection_window.collection_shapes.sprites()[self.collection_window.selected_index].shape_data,
                    self.opponent_window.collection_shapes.sprites()[self.opponent_window.selected_index].shape_data,
                    self.user,
                    self.opponent,
                    self.selections.seed,
                    connection_manager=self.connection_manager
                ).play()
            else:
                Game2(
                        self.screen, 
                        self.opponent_window.collection_shapes.sprites()[self.opponent_window.selected_index].shape_data,
                        self.collection_window.collection_shapes.sprites()[self.collection_window.selected_index].shape_data,
                        self.opponent,
                        self.user,
                        self.selections.seed,
                        connection_manager=self.connection_manager
                    ).play()

            # clear time accumulation
            self.prev_time = time.time()

            # idle while waiting for results
            while self.selections.winner == None:
                self.selections = self.connection_manager.getPlayerSelections()
                self.updateMenuState()
                self.drawScreenElements()
                self.clock.tick(self.target_fps)

        # do network post game if still connected
        if self.network_connected:
            self.postGame()

        if not self.selections.kill_pregame[self.pid]: self.connection_manager.send('KILL_PREGAME.')

        # prepare to go back to the menu
        self.collection_window.changeModeTransition()
        if self.opponent_window: self.opponent_window.changeModeTransition()

        # if pregame was abandoned, wait for windows to close before returning to menu
        while not self.collection_window.fully_closed:
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # keep track of who opponent was for notification deletion
        if self.opponent: self.prev_opponent = self.opponent
        self.notifications_window.current_opp_id = -1


        # prepare to go back to the menu
        self.collection_window.changeModeCollection()
        if self.opponent_window: self.opponent_window.changeModeCollection()


        # delete what needs to be deleted
        # if self.connection_manager: del self.connection_manager
        if self.opponent_window: del self.opponent_window
        self.connection_manager = None
        self.opponent_window = None

        # turn on/off auxiliary screen elements
        [shape.turnOn() for shape in self.menu_shapes]
        [window.button.turnOn() for window in [self.friends_window, self.collection_window, self.notifications_window]]
        if self.notifications_window.sprite_count_text.text != '0': self.notifications_window.sprite_count_text.turnOn()
        [element.turnOn() for element in [self.play_text, self.logged_in_as_text, self.network_back_button, self.local_match_clickable, self.network_match_clickable, self.exit_button] if element != None]

        self.network_back_button.turnOff()

    def preGame(self):
        '''wait for user to connect and make selections'''

        # while awaiting opponent
        while (self.selections == None or self.selections.user_ids[0 if self.pid == 1 else 1] == -1 or any(not window.fully_closed for window in [self.friends_window, self.collection_window, self.notifications_window])) and self.network_connected:
            self.selections = self.connection_manager.getPlayerSelections()

            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # search for opponent, create collection window
        self.opponent = None
        if self.network_connected:
            self.session.commit()
            self.opponent = self.session.query(User).filter(User.id == int(self.selections.user_ids[0 if self.pid == 1 else 1])).first()
            self.notifications_window.current_opp_id = self.opponent.id

            self.opponent_window = CollectionWindow(self.opponent, self.session, True)
            self.opponent_window.changeModeNetwork(self.connection_manager)
            self.collection_window.changeModeNetwork(self.connection_manager)
            self.network_back_button.turnOn()

            # clear time accumulation
            self.prev_time = time.time()

        self.connecting_to_text.turnOff()

        # players connected to each other, making selections
        while self.network_connected:
            self.selections = self.connection_manager.getPlayerSelections()

            # break if other player disconnected
            if self.selections.kill_pregame[0 if self.pid == 1 else 1]:
                self.network_connected = False

            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

            # check if game is ready to be played
            if (self.selections.players_ready[0] == self.selections.players_ready[1] == True) and self.selections.seed != None: break

        # close windows
        if self.opponent_window:
            self.collection_window.toggle()
            self.opponent_window.toggle()
            self.network_back_button.turnOff()

    def postGame(self):
        '''animate the results of a network match'''

        self.session.commit()

        # determine amount of essence to add to each player
        opponent_amount = 0
        player_amount = 0
        if self.pid == self.selections.winner:
            opponent_amount = min(self.selections.essence_earned[0], self.selections.essence_earned[1])
            player_amount = max(self.selections.essence_earned[0], self.selections.essence_earned[1])
        else:
            opponent_amount = max(self.selections.essence_earned[0], self.selections.essence_earned[1])
            player_amount = min(self.selections.essence_earned[0], self.selections.essence_earned[1])
        
        # prepare windows for post game animation
        windows = [self.opponent_window, self.collection_window]
        for window in windows:
            window.toggle()
            window.nameplate.disable()
            window.selector.disable()

        # give windows time to open
        self.pauseFor(1)

        # if game was played for keeps, animate the shuffle between groups
        if self.selections.keeps[0] and self.selections.keeps[1]:

            # determine winner and loser windows and shape data to be moved
            if self.selections.winner == self.pid:
                winner_window = self.collection_window
                loser_window = self.opponent_window
                moved_shape = self.opponent_window.selected_shape
                moving_side = 'top'
            else:
                self.selections.users_selected[0 if self.pid == 1 else 1] = 0 # necessary to stop opponent window from fighting the movement, since it's selected shape is locked to the selection indicated by server
                winner_window = self.opponent_window
                loser_window = self.collection_window
                moved_shape = self.collection_window.selected_shape
                moving_side = 'bottom'

            # move all shapes to original position
            if winner_window.selected_index != 0:
                winner_window.moveSpritesHome()

            # add new shape to the front of the list
            new_shape = CollectionShape(moved_shape.shape_data, -1, winner_window.user.num_shapes, self.session, True, winner_window == self.opponent_window)
            collection_copy = winner_window.collection_shapes.sprites()
            winner_window.collection_shapes.empty()
            winner_window.collection_shapes.add(itertools.chain([new_shape, collection_copy]))
            winner_window.selector.addShape(new_shape.shape_data)

            # adjust selected shape and shape positions to introduce new shape from the right
            winner_window.selected_shape: CollectionShape = new_shape # type: ignore
            for shape in winner_window.collection_shapes: shape.moveRight()
            self.collection_window.woosh_sound.play()

            # adjust transparency of new shape and shape's stats (to 0)
            winner_window.selected_shape.alpha_lock = True
            winner_window.selected_shape.image.set_alpha(0)
            winner_window.selected_shape.stats_surface.set_alpha(0)
            winner_window.selected_shape.stats_alpha = 0
            winner_window.selected_shape.next_stats_alpha = 0

            # allow shapes to move to original position
            self.pauseFor(0.5)

            # remove loser's shape from shapes group
            loser_window.selected_shape.alpha = 0
            loser_window.selected_shape.stats_surface.set_alpha(0)
            # flag if the opponent is removing their last shape, in this case, the selections object needs to be altered similar to above
            flag = loser_window == self.opponent_window and loser_window.selected_index == len(loser_window.collection_shapes)-1 
            loser_window.removeSelectedShape()
            if flag: self.selections.users_selected[0 if self.pid == 1 else 1] = loser_window.selector.selected_index

            # renumber all sprites to match their altered lists
            [sprite.redrawPosition(position, len(loser_window.collection_shapes)) for position, sprite in enumerate(loser_window.collection_shapes.sprites())]
            [sprite.redrawPosition(position, len(winner_window.collection_shapes)) for position, sprite in enumerate(winner_window.collection_shapes.sprites())]
            
            # add false image of shape to some group so that it can be animated moving
            self.moving_shapes.add(MovingShape(moved_shape.image, moving_side))
            self.collection_window.woosh_sound.play()
            self.pauseFor(0.5)

            # once false image is in place, fade shape and stats back in
            winner_window.selected_shape.alpha_lock = False
            winner_window.selected_shape.next_stats_alpha = 255

            self.pauseFor(1)
            self.moving_shapes.empty() # kill false image on the way out
        
        self.collection_window.essence_bar.increaseEssenceBy(player_amount)
        self.opponent_window.essence_bar.increaseEssenceBy(opponent_amount)
        self.user.shape_essence += player_amount # each player handles the db entries of only their own essence
        self.session.commit()

        # hold while essence bars are updating
        self.updateMenuState() # required for essence bar's changing flag to be updated
        while self.opponent_window.essence_bar.changing or self.collection_window.essence_bar.changing:
            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        self.pauseFor(5)

        # prepare windows to return to main menu
        for window in windows:
            window.toggle()
            window.nameplate.enable()
            window.selector.enable()

        # hold while windows are open
        while not self.collection_window.fully_closed:
            # update state
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        # redraw the positions of shapes in collection group
        # (keeps the new shape at the front of the group)
        self.collection_window.renumberGroup()

        # redraw the player information in follow name tag/notification tag
        for sprite in self.friends_window.group.sprites():
            sprite: FriendSprite
            if sprite.friend == self.opponent: 
                sprite.initInfo()
        
        for sprite in self.notifications_window.group.sprites():
            sprite: NotificationSprite
            if sprite.user == self.opponent: 
                sprite.initInfo()

    def addFriend(self, username):
        '''add friend relationship in the database'''

        # lower flags
        self.friends_window.already_following_flag = False
        self.friends_window.bad_credentials_flag = False
        self.friends_window.thats_you_flag = False

        # query db for user
        try:
            searched_user = self.session.query(User).filter(User.username == username).one()
        except Exception as e:
            self.friends_window.bad_credentials_flag = True
            print(f'Could not add friend, none found: {e}')
            return

        # raise flags
        self.friends_window.already_following_flag = any(friend.username == username for friend in self.user.friends)
        self.friends_window.thats_you_flag = searched_user.username == self.user.username
        if self.friends_window.already_following_flag or self.friends_window.thats_you_flag: return

        # add searched user to user friends and create notification
        try:
            searched_user = self.session.query(User).filter(User.username == username).one()

            # if user is already in the searched users friends, send friend confirmation notification
            if any(friend.username == self.user.username for friend in searched_user.friends):                
                self.addDbNotification(searched_user, self.user, FRIEND_CONFIRM)

            else: 
                self.addDbNotification(searched_user, self.user, FRIEND_ADD)
            
            self.user.friends.append(searched_user)
            self.session.commit()

            self.friends_window.checkFriendsUpdate()

        except Exception as e:
            self.session.rollback()
            print(f'Error creating notification: {e}')
            return

    def addDbNotification(self, owner: User, sender: User, type: str):
        '''create and add notification to the database, replacing any similar existing notifications'''

        # Delete any existing similar notifications
        existing_notification = next((notification for notification in owner.notifications_owned 
                                   if notification.type == type and notification.sender == sender), None)

        if existing_notification:
            self.session.delete(existing_notification)
            
        # Add the new notification
        self.session.add(Notification(owner, sender, type))

    def notifyMenu(self, notification: Notification):
        '''create notification on main menu'''
        
        blurb = [f'new notification', f'from {notification.sender.username}']
        
        self.new_notification_text.updateText(blurb)
        self.new_notification_text.turnOnFor(250)

    # MENU SHAPE HELPERS

    def checkShapeCollisions(self):
        '''test collisions between all shapes'''

        for shape in self.menu_shapes:
            for other_shape in self.menu_shapes:
                if shape == other_shape: continue

                shape: MenuShape
                other_shape: MenuShape

                if self.determineShapeCollisions(shape, other_shape):

                    if other_shape in shape.shapes_touching or shape in other_shape.shapes_touching: continue
                    
                    shape.shapes_touching.append(other_shape)
                    other_shape.shapes_touching.append(shape)

                    # collideShapes will return the id and xy of any dead shape
                    self.addNewShape(self.collideShapes(shape, other_shape))

                # shapes not touching, remove from lists if present
                else:    
                    if other_shape in shape.shapes_touching: shape.shapes_touching.remove(other_shape)
                    if shape in other_shape.shapes_touching: other_shape.shapes_touching.remove(shape)

    def determineShapeCollisions(self, shape_1: MenuShape, shape_2: MenuShape):
        '''return true if two shapes are about to collide'''

        v1 = numpy.array(shape_1.getV())
        v2 = numpy.array(shape_2.getV())

        p1 = numpy.array(shape_1.getXY())
        p2 = numpy.array(shape_2.getXY())
        
        # if distance is greater than sum of radii * 1.5, no collision possible
        # if numpy.linalg.norm(p1 - p2) > (shape_1.r + shape_2.r) * 1.5:
        #     return False

        # get future positions
        p1f = p1 + v1
        p2f = p2 + v2

        # temp move collision mask
        shape_1.collision_mask_rect.center = p1f
        shape_2.collision_mask_rect.center = p2f

        # 4: determine if collision is taking place
        collision = shape_1.collision_mask.overlap(shape_2.collision_mask, [int(shape_2.collision_mask_rect.x - shape_1.collision_mask_rect.x), int(shape_2.collision_mask_rect.y - shape_1.collision_mask_rect.y)])

        # move collision mask back
        shape_1.collision_mask_rect.center = p1
        shape_2.collision_mask_rect.center = p2

        return bool(collision)

    def collideShapes(self, shape_1: MenuShape, shape_2: MenuShape):
        '''collide two shapes, determine winner and loser, and return the loser's id and xy if the loser is dead'''

        random.choice(self.collision_sounds).play()

        self.repositionShapes(shape_1, shape_2)

        winner = shape_1 if random.randint(0, 1) == 0 else shape_2
        loser = shape_2 if winner == shape_1 else shape_1

        loser.takeDamage(winner.getDamage())

        # check if loser is dead, spawn clouds and return loser's id and xy
        if loser.hp <= 0:
            random.choice(self.death_sounds).play()

            loser_id = loser.shape_id
            loser_xy = loser.getXY()
            self.clouds_group.add(Clouds(loser, self.cloud_images))
            loser.kill()

            if loser in winner.shapes_touching: winner.shapes_touching.remove(loser)

            return loser_id, loser_xy
    
        return None

    def repositionShapes(self, shape_1: MenuShape, shape_2: MenuShape):
        '''rectify the positions and velocities of two shapes which are currently colliding'''

        # STEP 1

        [x2, y2] = shape_2.getXY()
        [x1, y1] = shape_1.getXY()

        [vx1i, vy1i] = shape_1.getV()
        [vx2i, vy2i] = shape_2.getV()

        norm_vec = numpy.array([x2 - x1, y2 - y1])
        if norm_vec[0] == 0 and norm_vec[1] == 0: 
            return

        divisor = math.sqrt(norm_vec[0]**2 + norm_vec[1]**2)
        unit_vec = numpy.array([norm_vec[0] / divisor, norm_vec[1] / divisor])

        unit_tan_vec = numpy.array([-1 * unit_vec[1], unit_vec[0]])

        # STEP 2

        v1 = numpy.array(shape_1.getV())
        m1 = shape_1.getM()

        v2 = numpy.array(shape_2.getV())
        m2 = shape_2.getM()

        # STEP 3

        v1n = numpy.dot(unit_vec, v1)

        v1t = numpy.dot(unit_tan_vec, v1)

        v2n = numpy.dot(unit_vec, v2)

        v2t = numpy.dot(unit_tan_vec, v2)

        # STEP 4

        v1tp = v1t

        v2tp = v2t

        # STEP 5

        v1np = ((v1n * (m1 - m2)) + (2 * m2 * v2n)) / (m1 + m2)

        v2np = ((v2n * (m2 - m1)) + (2 * m1 * v1n)) / (m1 + m2)

        # STEP 6

        v1np_ = v1np * unit_vec
        v1tp_ = v1tp * unit_tan_vec

        v2np_ = v2np * unit_vec
        v2tp_ = v2tp * unit_tan_vec

        # STEP 7

        v1p = v1np_ + v1tp_
        shape_1.setV(v1p[0], v1p[1])

        v2p = v2np_ + v2tp_
        shape_2.setV(v2p[0], v2p[1])

    def addNewShape(self, dead = None):
        '''called if a shape is killed during collision, replaces them with a new shape'''

        if dead != None:
            shape_data = shape_model_data[random.choice(['triangle', 'square', 'circle'])]
            shape_data.color_id = random.randint(0, len(color_data) - 1)

            face_images = []
            if shape_data.type == 'triangle':
                face_images = self.triangle_face_images
            elif shape_data.type == 'square':
                face_images = self.square_face_images   
            elif shape_data.type == 'circle':
                face_images = self.circle_face_images

            self.menu_shapes.add(MenuShape(dead[0], shape_data, color_data[shape_data.color_id], face_images))

    # PLAY HELPERS

    def loginLoop(self):
        '''run the game loop for the login/register screen'''

        # start the time for accumulator
        self.prev_time = time.time()

        while self.user == None:
            self.updateMenuState()

            self.drawScreenElements()

            self.clock.tick(self.target_fps)

        # turn on/off screen elements
        turn_off = [self.username_editable, self.password_editable, self.login_clickable, self.register_clickable, self.password_editable, self.password_confirm_editable, self.or_text, self.back_button]
        turn_on = [self.play_text, self.network_match_clickable, self.local_match_clickable, self.exit_button, self.logged_in_as_text, self.friends_window.button, self.notifications_window.button, self.collection_window.button]
        
        [element.turnOff() for element in turn_off]
        [element.turnOn() for element in turn_on]

        self.prev_time = time.time()

    def userLogin(self, mouse_pos):
        '''check if user is logging in'''
        
        if self.thread and self.thread.is_alive(): return
        if self.thread and not self.thread.is_alive(): del self.thread

        self.thread_running = True
        self.thread = Thread(target=self.threadRunLoop)
        self.thread.start()

        # Get entered username and password
        username = self.username_editable.getText()
        password = self.password_editable.getText()        

        try:
            # Query for user with matching username and password
            user = self.session.query(User).filter(User.username == username).first()

            if user and user.check_password(password):
                [element.deselect() for element in [self.username_editable, self.password_editable, self.password_confirm_editable]]
                [element.turnOff() for element in [self.username_editable, self.password_editable, self.password_confirm_editable, self.register_clickable, self.back_button, self.login_clickable, self.or_text]]
                self.logging_in_text.turnOn()

                # Login successful
                self.logged_in_as_text = Text(f'logged in as: {user.username}', 35, 1920/2, 20, fast_off=True)
                self.screen_elements.append(self.logged_in_as_text)

                # Initialize windows after successful login
                self.collection_window = CollectionWindow(user, self.session)
                self.friends_window = FriendsWindow(user, self.session, self.addFriend, self.startNetwork)
                self.notifications_window = NotificationsWindow(user, self.session, self.addFriend, self.startNetwork, self.notifyMenu)
                self.user = user

                self.logging_in_text.turnOff()
            else:
                # provide feedback on what went wrong
                if user == None:
                    self.bad_credentials_text.updateText('user not found!')
                    self.bad_credentials_flag = True
                else:
                    self.bad_credentials_text.updateText('incorrect password!')
                    self.bad_credentials_flag = True

        except Exception as e:
            print(f'Login error: {e}')
            self.bad_credentials_flag = True

        self.thread_running = False

    def userRegister(self, mouse_pos):
        '''check if user is registering'''
                
        # if user is at inital screen, turn off login elements
        if not self.login_clickable.disabled:
            [element.turnOff() for element in [self.login_clickable, self.or_text]]
            self.password_confirm_editable.turnOn()
            self.back_button.turnOn()
        
        # if user is at register screen, attempt to register
        else:
            if self.thread and self.thread.is_alive(): return
            if self.thread and not self.thread.is_alive(): del self.thread

            self.thread_running = True
            self.thread = Thread(target=self.threadRunLoop)
            self.thread.start()

            username = self.username_editable.getText()
            password = self.password_editable.getText()
            password_confirm = self.password_confirm_editable.getText()

            try:
                # Validate username length
                if len(username) < 3:
                    self.bad_credentials_text.updateText('username must be at least 3 characters!')
                    self.bad_credentials_flag = True
                    self.thread_running = False
                    return

                # Validate password length
                if len(password) < 8:
                    self.bad_credentials_text.updateText('password must be 8-10 characters long!')
                    self.bad_credentials_flag = True
                    self.thread_running = False
                    return

                # Check if username already exists
                existing_user = self.session.query(User).filter(User.username == username).first()
                if existing_user:
                    self.bad_credentials_text.updateText('username taken!')
                    self.bad_credentials_flag = True
                    self.thread_running = False
                    return
                
                # Validate passwords match
                if password != password_confirm:
                    self.bad_credentials_text.updateText(f'passwords don\'t match!')
                    self.bad_credentials_flag = True
                    self.thread_running = False
                    return

                # Create new user
                new_user = User(username=username, password=password)
                self.session.add(new_user)
                self.session.commit()

                # new_shape = generateRandomShape(new_user, self.session)
                # new_user.favorite_id = new_shape.id
                # self.session.commit()

                [element.deselect() for element in [self.username_editable, self.password_editable, self.password_confirm_editable]]
                [element.turnOff() for element in [self.username_editable, self.password_editable, self.password_confirm_editable, self.register_clickable, self.back_button, self.login_clickable, self.or_text]]
                self.logging_in_text.updateText('registering...')
                self.logging_in_text.turnOn()


                # Log in as new user
                self.user = new_user
                self.logged_in_as_text = Text(f'logged in as: {self.user.username}', 35, 1920/2, 20, fast_off=True)
                self.screen_elements.append(self.logged_in_as_text)

                # Initialize windows for new user
                self.collection_window = CollectionWindow(self.user, self.session)
                self.friends_window = FriendsWindow(self.user, self.session, self.addFriend, self.startNetwork)
                self.notifications_window = NotificationsWindow(self.user, self.session, self.addFriend, self.startNetwork, self.notifyMenu)

                self.logging_in_text.turnOff()

            except Exception as e:
                print(f'Registration error: {e}')
                self.bad_credentials_flag = True

            self.thread_running = False

    def handleInputs(self, mouse_pos, events):
        '''handle any inputs from the user'''


        for event in events:
            if event.type != MOUSEBUTTONDOWN or event.button != 1: return

            self.click_sound.play()

            # check if user attempting to login
            if self.login_clickable.isHovAndEnabled(mouse_pos): self.userLogin(mouse_pos)

            # check if user attempting to register
            if self.register_clickable.isHovAndEnabled(mouse_pos): self.userRegister(mouse_pos)
            
            # quit network matchmaking
            if self.network_back_button.isHovAndEnabled(mouse_pos):
                self.network_connected = False

            # if exit/back button clicked while in register screen, go back to login screen
            if (self.exit_button.isHovAndEnabled(mouse_pos) and not self.back_button.disabled) or (self.back_button.isHovAndEnabled(mouse_pos)):
                self.password_confirm_editable.deselect()
                self.password_confirm_editable.turnOff()
                self.back_button.turnOff()
                self.or_text.turnOn()
                self.login_clickable.turnOn()

            # quit game
            elif self.exit_button.isHovAndEnabled(mouse_pos):


                # if any window is open, do not exit
                if self.collection_window:
                    if any(window.opened for window in [self.notifications_window, self.collection_window]): continue

                if self.connection_manager: 
                    self.connection_manager.send('KILL_PREGAME.')
                    self.network_connected = False
                
                else:
                    self.close_sound.play()
                    self.exit_clicked = True
                    pygame.mixer.Sound.fadeout(self.menu_music, 1000)

                    [element.deselect() for element in self.screen_elements if isinstance(element, EditableText)]
                    [element.turnOff() for element in self.screen_elements if element not in [self.title_text]]
                    [element.button.turnOff() for element in [self.friends_window, self.notifications_window, self.collection_window] if element != None]
                    self.notifications_window.sprite_count_text.turnOff()
                    [shape.turnOff() for shape in self.menu_shapes]

            # handle window interactions, if windows exist
            if self.collection_window:
                # if one window is being opened, close any windows that overlap
                side_windows = [self.friends_window, self.notifications_window]
                if self.collection_window.isButtonHovered(mouse_pos):
                    [window.close() for window in side_windows]
                elif any(window.isButtonHovered(mouse_pos) for window in side_windows):
                    self.collection_window.close()

                # if no window is clicked and not in pregame, close all windows
                windows = [self.collection_window, self.friends_window, self.notifications_window]
                if not any(window.rect.collidepoint(mouse_pos) for window in windows) and not self.opponent_window:
                    [window.close() for window in windows]
                
    def updateMenuState(self):
        '''progress the menu state by one tick'''

        self.current_time = time.time()

        self.time_step_accumulator += self.current_time - self.prev_time
        while self.time_step_accumulator >= self.time_step:
            self.time_step_accumulator -= self.time_step

            self.frames += 1
            self.updateScreenElements()

        self.prev_time = self.current_time

        # if self.frames % 120 == 0:
        #     self.session.commit()

        #     # if self.friends_window: self.friends_window.checkFriendsUpdate()
        #     if self.notifications_window: self.notifications_window.checkNotificationsUpdate()


        if self.exit_clicked:
            self.frames_since_exit_clicked += 1

            if self.frames_since_exit_clicked == self.target_fps: 
                self.notifications_window.markNotificationsAsRead()
                sys.exit()

        # Start notification polling when notifications window is created
        if self.notifications_window and not self.notification_poll_thread:
            self.startNotificationPolling()
        # Stop polling if notifications window is destroyed
        elif not self.notifications_window and self.notification_poll_thread:
            self.stopNotificationPolling()

    def updateScreenElements(self):
        '''update all elements on the screen'''

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        self.handleInputs(mouse_pos, events)

        self.cursor_rect.center = mouse_pos

        # [text.update() for text in self.texts]
        # [clickable.update(events, mouse_pos) for clickable in self.clickables if clickable not in [None]]
        # [editable.update(events, mouse_pos) for editable in self.login_editables]
        [element.update(events, mouse_pos) for element in self.screen_elements]

        # update sprites
        self.moving_shapes.update()
        self.menu_shapes.update()
        self.clouds_group.update()
        self.checkShapeCollisions()


        if self.collection_window: self.collection_window.update(mouse_pos, events)
        if self.friends_window: self.friends_window.update(mouse_pos, events)
        if self.notifications_window: self.notifications_window.update(mouse_pos, events)

        if self.opponent_window: self.opponent_window.update(mouse_pos, events)

        # draw bad credentials text if flag is true, and handle timer
        if self.bad_credentials_flag:
            self.bad_credentials_text.turnOn()

            self.bad_credentials_timer += 1
            if self.bad_credentials_timer == 200:
                self.bad_credentials_flag = False
                self.bad_credentials_timer = 0
                self.bad_credentials_text.turnOff()

        self.screen.blit(self.cursor, self.cursor_rect)

    def drawScreenElements(self):
        '''draw all elements to the screen'''

        # flip the display
        pygame.display.flip()

        # draw background
        self.screen.blit(self.background, (0, 0))
        self.menu_shapes.draw(self.screen)
        self.clouds_group.draw(self.screen)

        # draw screen elements
        for element in self.screen_elements: element.draw(self.screen)

        # draw windows if they exist
        if self.collection_window: self.collection_window.draw(self.screen)
        if self.friends_window: self.friends_window.draw(self.screen)
        if self.notifications_window: self.notifications_window.draw(self.screen)
        if self.opponent_window: self.opponent_window.draw(self.screen)

        # draw moving shapes on top of windows
        if self.moving_shapes:
            if self.moving_shapes.sprites()[0].image.get_alpha() != 0: self.moving_shapes.draw(self.screen)

        # draw bad credentials text if flag is true, and handle timer
        if self.bad_credentials_flag:
            self.bad_credentials_text.turnOn()

            self.bad_credentials_timer += 1
            if self.bad_credentials_timer == 200:
                self.bad_credentials_flag = False
                self.bad_credentials_timer = 0
                self.bad_credentials_text.turnOff()

        self.screen.blit(self.cursor, self.cursor_rect)

    def pauseFor(self, seconds):
        '''pause the game for a given number of seconds'''

        start_time = time.time()
        while time.time() - start_time < seconds:
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

    def play(self, username = None, password = None):
        '''run the game loop for the main menu'''
        # if provided username and password, try to log in and skip login loop
        do_login_loop = False
        if username != None and password != None:
            try:
                user = self.session.query(User).filter(User.username == username).first()
                
                if not user: 
                    print('Warning: username provided at command line not found')
                    do_login_loop = True
                
                elif user.check_password(str(password)):
                    self.user = user
                    
                    # Initialize windows after successful login
                    self.logged_in_as_text = Text(f'logged in as: {user.username}', 35, 1920/2, 20, fast_off=True)
                    self.screen_elements.append(self.logged_in_as_text)
                    self.collection_window = CollectionWindow(user, self.session)
                    self.friends_window = FriendsWindow(user, self.session, self.addFriend, self.startNetwork)
                    self.notifications_window = NotificationsWindow(user, self.session, self.addFriend, self.startNetwork, self.notifyMenu)
                    
                    print(f'Success: logged in as {user.username}')
                
                else:
                    print('Warning: incorrect password provied at command line')
                    do_login_loop = True
                    
            except Exception as e:
                print(f'ERROR: {e}')
                do_login_loop = True
        
        else: do_login_loop = True
        
        # start the time for accumulator
        self.prev_time = time.time()
        
        # turn on/off screen elements
        if do_login_loop:
            self.pauseFor(1)
            [element.turnOn() for element in [self.username_editable, self.password_editable, self.login_clickable, self.register_clickable, self.or_text, self.exit_button]]
        else: 
            turn_off = [self.username_editable, self.password_editable, self.login_clickable, self.register_clickable, self.password_editable, self.password_confirm_editable, self.or_text, self.back_button]
            turn_on = [self.play_text, self.network_match_clickable, self.local_match_clickable, self.exit_button, self.logged_in_as_text, self.friends_window.button, self.notifications_window.button, self.collection_window.button]
            [element.turnOff() for element in turn_off]
            [element.turnOn() for element in turn_on if element != None]

        self.pauseFor(1)
        [shape.turnOn() for shape in self.menu_shapes]
                
        if do_login_loop: self.loginLoop()

        while True: self.runGameLoop()
        
    def runGameLoop(self):
        '''run the game loop'''

        while True:
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

    def threadRunLoop(self):
        '''run the game loop while the user is not logged in'''

        while self.thread_running:
            self.updateMenuState()
            self.drawScreenElements()
            self.clock.tick(self.target_fps)

        del self.thread
        self.thread = None

    def startNotificationPolling(self):
        '''Start asynchronous polling for notifications'''
        
        def pollNotifications():
            '''Poll for notification updates in a separate thread'''
            
            while not self.stop_notification_polling:
                if self.notifications_window:
                    self.session.commit()
                    clear_prev_opponent, ids_to_update = self.notifications_window.checkNotificationsUpdate(self.prev_opponent)
                    if clear_prev_opponent: self.prev_opponent = None
                    
                    if ids_to_update != []:
                        for id in ids_to_update:
                            for sprite in self.friends_window.group.sprites():
                                if sprite.user.id == id:
                                    sprite.initSurface()
                        
                time.sleep(2)  # Poll every 2 seconds

        if self.notification_poll_thread is None:
            self.stop_notification_polling = False
            self.notification_poll_thread = Thread(target=pollNotifications)
            self.notification_poll_thread.daemon = True  # Thread will exit when main program exits
            self.notification_poll_thread.start()

    def stopNotificationPolling(self):
        '''Stop the notification polling thread'''
        self.stop_notification_polling = True
        if self.notification_poll_thread:
            self.notification_poll_thread.join()
            self.notification_poll_thread = None

    def pollNotifications(self):
        '''poll database for new notifications'''
        while self.running:
            try:
                with self.db_lock:
                    self.session.expire_all()
                    notifications = self.session.query(Notification).filter_by(owner_id=self.user.id).all()
                    self.user.notifications_owned = notifications
                    self.session.commit()
                
                time.sleep(1)
            except:
                with self.db_lock:
                    self.session.rollback()
