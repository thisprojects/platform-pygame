import pygame
from config import PURPLE
from pygame.sprite import Sprite


class Obstacle(Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
