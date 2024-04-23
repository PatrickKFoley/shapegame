import pygame

def createText(text, size, color = "white"):
    font = pygame.font.Font("backgrounds/font.ttf", size)
    

    if type(text) == type("string"):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        return text_surface, text_rect
    
    elif type(text) == type(["array"]):
        text_surfaces = []
        for element in text:
            text_surfaces.append(font.render(element, True, color))

        max_line_length = max(surface.get_size()[0] for surface in text_surfaces)
        line_height = text_surfaces[0].get_size()[1]

        surface = pygame.Surface((max_line_length, (len(text_surfaces) + 1) * line_height), pygame.SRCALPHA, 32)

        for i, text_surface in enumerate(text_surfaces):
            surface.blit(text_surface, [max_line_length/2 - text_surface.get_size()[0]/2, line_height * (i+1)])

        return surface, surface.get_rect()