from pygame import Surface
from pygame.sprite import Sprite
from config import PROJECTILE_SPEED, SCREEN_WIDTH


class Projectile(Sprite):
    def __init__(self, x, y, direction, color, owner_type):
        super().__init__()
        self.image = Surface((8, 8))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.x = float(x)  # Store position as float
        self.y = float(y)
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.direction = direction  # 1 for right, -1 for left
        self.owner_type = owner_type  # 'player' or 'enemy'

    def update(self, delta_time):
        # Update position using delta_time
        self.x += PROJECTILE_SPEED * self.direction * delta_time
        self.rect.x = int(self.x)

        # Remove if off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
