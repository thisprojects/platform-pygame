import pygame
from config import BROWN, ORANGE
from pygame.sprite import Sprite


class Ladder(Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)

        # Draw vertical rails to make it look like a ladder
        rail_width = max(2, width // 10)
        pygame.draw.rect(self.image, ORANGE, (0, 0, rail_width, height))
        pygame.draw.rect(self.image, ORANGE, (width - rail_width, 0, rail_width, height))

        # Draw horizontal rungs
        rung_height = 3
        rung_spacing = max(15, height // 8)  # Space rungs evenly
        for rung_y in range(0, height, rung_spacing):
            pygame.draw.rect(self.image, ORANGE, (0, rung_y, width, rung_height))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
