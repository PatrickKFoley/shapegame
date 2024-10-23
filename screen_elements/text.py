from shared_functions import createText

class Text:
    def __init__(self, text, size, x, y, align = "center", color = "black"):
        self.text = text
        self.size = size
        self.x = x
        self.y = y
        self.y_init = y
        self.align = align
        self.color = color
        self.xy = [self.x, self.y]
        self.y_scroll = 0
        self.align = align

        self.surface, self.rect = createText(self.text, self.size, self.color)
        self.position()

    def position(self):
        self.xy = [self.x, self.y]

        if self.align == "center": self.rect.center = self.xy
        elif self.align == "topleft": self.rect.topleft = self.xy
        elif self.align == "topright": self.rect.topright = self.xy

    def scroll(self, amount):
        self.y_scroll += amount

        self.y = self.y_scroll + self.y_init
        self.position()

