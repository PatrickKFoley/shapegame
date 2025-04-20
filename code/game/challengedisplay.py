import pygame, random
from pygame import Surface  
from pygame.locals import *
from pygame.image import load
from pygame.transform import smoothscale
from pygame.sprite import Group, Sprite
from pygame.mixer import Sound

class ChallengeElement:
    def __init__(self, direction: str, icons: list[Surface], pos: int):
        super().__init__()
        self.direction = direction
        self.icon_w = smoothscale(icons[0], (75, 75))
        self.icon_b = smoothscale(icons[1], (75, 75))
        self.pos = pos  

        self.correct = False
        self.completed = False
        self.failed = False

        self.x = 50 + self.pos * 100
        self.y = 50

        self.rect = self.icon_w.get_rect()
        self.rect.center = (self.x, self.y)

    def markCorrect(self):
        self.correct = True

    def markIncorrect(self):
        self.correct = False

    def toggleCorrect(self):
        self.correct = not self.correct

    def markCompleted(self):
        self.completed = True

    def draw(self, surface: Surface):
        if self.correct:
            surface.blit(self.icon_w, self.rect)
        else:
            surface.blit(self.icon_b, self.rect)

    def update(self):
        pass

class ChallengeDisplay:
    def __init__(self, seed: int):
        self.seed = seed
        random.seed(self.seed)

        self.frames = 0

        icon_size = [75, 75]
        self.challenge_icons = {
            'd_g': load('assets/misc/challenge_shapes/d_g.png').convert_alpha(),
            'd_w': load('assets/misc/challenge_shapes/d_w.png').convert_alpha(),
            'l_g': load('assets/misc/challenge_shapes/l_g.png').convert_alpha(),
            'l_w': load('assets/misc/challenge_shapes/l_w.png').convert_alpha(),
            'r_g': load('assets/misc/challenge_shapes/r_g.png').convert_alpha(),
            'r_w': load('assets/misc/challenge_shapes/r_w.png').convert_alpha(),
            'u_g': load('assets/misc/challenge_shapes/u_g.png').convert_alpha(),
            'u_w': load('assets/misc/challenge_shapes/u_w.png').convert_alpha(),
        }

        self.win_sound = Sound('assets/sounds/challenge_win.wav')
        self.fail_sound = Sound('assets/sounds/challenge_loss.wav')
        self.fail_sound.set_volume(0.5)
        self.win_sound.set_volume(0.5)

        self.challenge_elements = []
        self.user_completed = False
        self.server_completed = False
        self.failed = False
        self.won = False
        self.frames_completed = 0


        self.width, self.height = 700, 100
        self.x, self.y = 10, -self.height*2 # position, alignment on topleft
        self.next_y = 0
        self.v = 0
        self.a = 2
        self.surface = Surface((self.width, self.height), pygame.SRCALPHA, 32).convert_alpha()
        self.icons_surface = Surface((self.width, self.height), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect()
        self.rect.topleft = (self.x, self.y)
        
        self.generateNewSequence()

    def generateNewSequence(self):
        
        # determine the length of the sequence with some randomness
        length = random.choices([5, 6, 7], weights=[0.6, 0.3, 0.1])[0]
        # lenght = 7
        
        # generate the random sequence
        self.sequence = [random.choice(['d', 'l', 'r', 'u']) for _ in range(length)]
        self.user_sequence = []

        # draw background to surface
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, 'black', [0, 0, length*100, self.height], border_radius=15)
        pygame.draw.rect(self.surface, 'white', [3, 3, length*100 - 6, self.height - 6], border_radius=12)

        # create challenge elements
        self.challenge_elements.clear()
        for i, icon_direction in enumerate(self.sequence):

            icons = [
                self.challenge_icons[f'{icon_direction}_w'],
                self.challenge_icons[f'{icon_direction}_g'],
            ]

            self.challenge_elements.append(ChallengeElement(icon_direction, icons, i))

    def draw(self, surface):

        [challenge_element.draw(self.icons_surface) for challenge_element in self.challenge_elements]

        surface.blit(self.surface, self.rect)
        surface.blit(self.icons_surface, self.rect)

    def update(self, events):

        self.frames += 1

        def getKeyFromEvent(event):

            if event.key == K_UP or event.key == K_w:
                return 'u'
            elif event.key == K_DOWN or event.key == K_s:
                return 'd'
            elif event.key == K_LEFT or event.key == K_a:
                return 'l'
            elif event.key == K_RIGHT or event.key == K_d:
                return 'r'
            else:
                return -1

        [element.update() for element in self.challenge_elements]

        if self.y != self.next_y:

            distance = abs(self.y - self.next_y)

            if distance > 50:
                self.v += self.a
            else:
                self.v = max(1, distance * 0.2)
                
            if self.y > self.next_y:
                self.y = max(self.y - self.v, self.next_y)

            elif self.y < self.next_y:
                self.y = min(self.y + self.v, self.next_y)

            if self.y == self.next_y:
                self.v = 0

        self.rect.topleft = (self.x, self.y)

        for event in events:
            if event.type == pygame.KEYDOWN and not self.user_completed:
                
                direction = getKeyFromEvent(event)

                if direction == -1: continue
                
                if direction == self.sequence[len(self.user_sequence)][:1]:
                    self.user_sequence.append(direction)

                    # update the icon of the sequence element which was just pressed    
                    self.challenge_elements[len(self.user_sequence) - 1].markCorrect()

                    if len(self.user_sequence) == len(self.sequence):
                        self.user_completed = True

                else:
                    [element.markIncorrect() for element in self.challenge_elements]
                    self.user_sequence = []

        if self.server_completed:
            
            self.frames_completed += 1

            if self.frames_completed % 10 == 0 and self.frames_completed <= 110:
                
                [element.toggleCorrect() for element in self.challenge_elements]


            if self.frames_completed == 130:
                self.next_y = -self.height*2

        # if self.frames > 300 and not self.completed: self.markFailed()

    def markWon(self):
        [element.markIncorrect() for element in self.challenge_elements]
        
        self.won = True
        self.server_completed = True
        self.win_sound.play()

    def markFailed(self):
        
        [element.markIncorrect() for element in self.challenge_elements]

        self.failed = True
        self.server_completed = True
        self.fail_sound.play()

    def markCancelled(self):

        [element.markIncorrect() for element in self.challenge_elements]

        self.server_completed = True
