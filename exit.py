import pygame
from config import YELLOW
from pygame.sprite import Sprite


class Exit(Sprite):
    def __init__(self, x, y, width=60, height=60):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
