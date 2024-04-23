from shared_functions import createText

class Text:
    def __init__(self, text, size, x, y, align = "center", color = "white"):
        self.text = text
        self.size = size
        self.x = x
        self.y = y
        self.align = align
        self.color = color
        self.xy = [self.x, self.y]

        self.surface, self.rect = createText(self.text, self.size, self.color)

        if self.align == "center": self.rect.center = self.xy
        elif self.align == "topleft": self.rect.topleft = self.xy
        elif self.align == "topright": self.rect.topright = self.xy