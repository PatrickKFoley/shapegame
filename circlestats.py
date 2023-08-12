class CircleStats:
    def __init__(self, flag = False):
        self.dmg_dealt = 0
        self.dmg_received = 0
        self.hp_healed = 0
        self.powerups_activated = 0
        self.kills = 0
        self.players_killed = []

        self.instakills_used = 0
        self.players_resurrected = 0
        self.stars_used = 0
        self.muscles_used = 0
        self.speeds_used = 0
        self.bombs_used = 0
        self.laser_hits = 0
        self.blue_laser_hits = 0

        if flag: self.dmg_dealt = 1

    def dealDamage(self, amount):
        self.dmg_dealt += amount

    def receiveDamage(self, amount):
        self.dmg_received += amount

    def heal(self, amount):
        self.hp_healed += amount

    def activatePowerup(self):
        self.powerups_activated += 1

    def killPlayer(self, id):
        if id not in self.players_killed:
            self.players_killed.append(id)
            self.kills += 1

    def useInstakill(self):
        self.instakills_used += 1

    def resurrectPlayer(self):
        self.players_resurrected += 1

    def useStar(self):
        self.stars_used += 1

    def useMuscle(self):
        self.muscles_used += 1

    def useSpeed(self):
        self.speeds_used += 1

    def useBomb(self):
        self.bombs_used += 1
    
    def laserHit(self):
        self.laser_hits += 1

    def blueLaserHit(self):
        self.blue_laser_hits += 1

    def report(self):
        return [
            self.dmg_dealt,
            self.dmg_received,
            self.hp_healed,
            self.players_resurrected ,
            self.powerups_activated,
            self.instakills_used,
            self.muscles_used,
            self.speeds_used,
            self.bombs_used,
            self.laser_hits,
            self.blue_laser_hits,
            self.kills,
        ]

    def copy(self, other):
        self.dmg_dealt =        other.dmg_dealt
        self.dmg_received =     other.dmg_received
        self.hp_healed =        other.hp_healed
        self.powerups_activated = other.powerups_activated
        self.kills =            other.kills
        self.players_killed =   other.players_killed

        self.instakills_used =  other.instakills_used
        self.players_resurrected = other.players_resurrected
        self.stars_used =       other.stars_used
        self.muscles_used =     other.muscles_used
        self.speeds_used =      other.speeds_used
        self.bombs_used =       other.bombs_used
        self.laser_hits =       other.laser_hits