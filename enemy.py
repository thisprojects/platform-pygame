from pygame.sprite import Sprite
import pygame
from config import (
    RED,
    ENEMY_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    GRAVITY,
    ENEMY_SHOOT_CHANCE,
    PURPLE,
)
from projectile import Projectile
import random


class Enemy(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
        self.vel_y = 0
        self.on_ground = False
        self.direction_timer = 0
        self.direction_change_interval = random.randint(60, 180)  # Frames

    def update(self, platforms, obstacles):
        # Randomly change direction
        self.direction_timer += 1
        if self.direction_timer >= self.direction_change_interval:
            self.vel_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED, 0])
            self.direction_timer = 0
            self.direction_change_interval = random.randint(60, 180)

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

        # Keep enemy on screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = ENEMY_SPEED
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x = -ENEMY_SPEED
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
                        self.vel_x = -ENEMY_SPEED
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                        self.vel_x = ENEMY_SPEED
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
                        self.vel_x = -ENEMY_SPEED
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = obstacle.rect.right
                        self.vel_x = ENEMY_SPEED
                elif direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = obstacle.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = obstacle.rect.bottom
                        self.vel_y = 0

    def try_shoot(self, projectiles_group):
        if random.random() < ENEMY_SHOOT_CHANCE:
            direction = 1 if self.vel_x >= 0 else -1
            if self.vel_x == 0:
                direction = random.choice([-1, 1])
            projectile = Projectile(
                self.rect.centerx, self.rect.centery, direction, PURPLE, "enemy"
            )
            projectiles_group.add(projectile)
