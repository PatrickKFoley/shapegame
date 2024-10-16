

class ShapeStats():
    '''class owned by shape to track stats'''

    def __init__(self, shape_id):
        self.shape_id = shape_id

        self.dmg_dealt = 0
        self.dmg_received = 0
        self.kills = 0
        self.resurrects = 0
        self.powerups_collected = 0

    def dealDamage(self, dmg: int): self.dmg_dealt += dmg

    def receiveDamage(self, dmg: int): self.dmg_received += dmg

    def killShape(self): self.kills += 1

    def resurrectShape(self): self.resurrects += 1

    def collectPowerup(self): self.powerups_collected += 1