from pygame.sprite import Sprite
import pygame
from config import (
    RED,
    ENEMY_SPEED,
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
        self.x = float(x)  # Store position as floats
        self.y = float(y)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.vel_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms, obstacles, delta_time):
        # Check for platform edges and reverse direction
        if self._check_platform_edge(platforms, delta_time):
            self.vel_x = -self.vel_x

        # Apply gravity (multiply by delta_time)
        self.vel_y += GRAVITY * delta_time

        # Update position using floats (multiply by delta_time)
        self.x += self.vel_x * delta_time
        self.rect.x = int(self.x)
        self.check_platform_collision(platforms, "horizontal")
        self.check_obstacle_collision(obstacles, "horizontal")

        self.y += self.vel_y * delta_time
        self.rect.y = int(self.y)
        self.on_ground = False
        self.check_platform_collision(platforms, "vertical")
        self.check_obstacle_collision(obstacles, "vertical")

        # Keep enemy within horizontal screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = float(self.rect.x)
            self.vel_x = ENEMY_SPEED
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = float(self.rect.x)
            self.vel_x = -ENEMY_SPEED

    def check_platform_collision(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = platform.rect.left
                        self.x = float(self.rect.x)
                        self.vel_x = -ENEMY_SPEED
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                        self.x = float(self.rect.x)
                        self.vel_x = ENEMY_SPEED
                elif direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = platform.rect.top
                        self.y = float(self.rect.y)
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = platform.rect.bottom
                        self.y = float(self.rect.y)
                        self.vel_y = 0

    def check_obstacle_collision(self, obstacles, direction):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = obstacle.rect.left
                        self.x = float(self.rect.x)
                        self.vel_x = -ENEMY_SPEED
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = obstacle.rect.right
                        self.x = float(self.rect.x)
                        self.vel_x = ENEMY_SPEED
                elif direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = obstacle.rect.top
                        self.y = float(self.rect.y)
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Jumping
                        self.rect.top = obstacle.rect.bottom
                        self.y = float(self.rect.y)
                        self.vel_y = 0

    def _check_platform_edge(self, platforms, delta_time):
        """Check if enemy is approaching a platform edge."""
        # Only check edges when on ground and moving
        if not self.on_ground or self.vel_x == 0:
            return False

        # Calculate lookahead distance
        lookahead_distance = abs(self.vel_x * delta_time) + 5

        # Determine check position based on direction
        if self.vel_x > 0:  # Moving right
            check_x = self.rect.right + lookahead_distance
        else:  # Moving left
            check_x = self.rect.left - lookahead_distance

        check_y = self.rect.bottom + 10  # Check 10px below feet

        # Create small test rect
        test_rect = pygame.Rect(check_x - 2, check_y - 2, 4, 4)

        # Check if any platform exists at this position
        for platform in platforms:
            if test_rect.colliderect(platform.rect):
                return False  # Ground exists - safe

        return True  # No ground - edge detected

    def try_shoot(self, projectiles_group, delta_time):
        # Convert per-second probability to per-frame using delta_time
        if random.random() < ENEMY_SHOOT_CHANCE * delta_time:
            direction = 1 if self.vel_x >= 0 else -1
            if self.vel_x == 0:
                direction = random.choice([-1, 1])
            projectile = Projectile(
                self.rect.centerx, self.rect.centery, direction, PURPLE, "enemy"
            )
            projectiles_group.add(projectile)
