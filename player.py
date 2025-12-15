from pygame.sprite import Sprite
import pygame
from projectile import Projectile
from config import (
    PLAYER_SPEED,
    PLAYER_JUMP,
    GRAVITY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    YELLOW,
)


class Player(Sprite):
    def __init__(self, x, y, color, controls):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.controls = controls
        self.alive = True

    def update(self, platforms, obstacles):
        if not self.alive:
            return

        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.vel_x = 0
        if keys[self.controls["left"]]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[self.controls["right"]]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        # Jumping
        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = PLAYER_JUMP
            self.on_ground = False

        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.rect.x += self.vel_x
        self.check_platform_collision(platforms, "horizontal")
        self.check_obstacle_collision(obstacles, "horizontal")

        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_platform_collision(platforms, "vertical")
        self.check_obstacle_collision(obstacles, "vertical")

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True

    def check_platform_collision(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                elif direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0

    def check_obstacle_collision(self, obstacles, direction):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = obstacle.rect.left
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = obstacle.rect.right
                elif direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = obstacle.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = obstacle.rect.bottom
                        self.vel_y = 0

    def shoot(self, projectiles_group):
        if not self.alive:
            return
        direction = 1 if self.facing_right else -1
        projectile = Projectile(
            self.rect.centerx, self.rect.centery, direction, YELLOW, "player"
        )
        projectiles_group.add(projectile)
