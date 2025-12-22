from pygame.sprite import Sprite
import pygame
from config import BLUE, GRAVITY, ORANGE
from projectile import Projectile


class Machinegunner(Sprite):
    """
    Stationary enemy that always faces the player and fires in bursts.
    Fires 6 shots 0.25 seconds apart, with a 3 second cooldown between bursts.
    """

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.x = float(x)
        self.y = float(y)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Machinegunner is always stationary
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        # Facing direction (1 = right, -1 = left)
        self.facing_direction = 1

        # Burst fire settings
        self.shots_per_burst = 6
        self.shot_interval = 0.25  # seconds between shots
        self.burst_cooldown = 3.0  # seconds between bursts

        self.burst_shot_count = 0  # Current shot in burst
        self.shoot_timer = 0.0
        self.in_cooldown = False

    def update(self, platforms, obstacles, players, camera_y, delta_time):
        """Update machinegunner state - tracks player and handles gravity."""
        # Always face towards the nearest player
        self._update_facing_direction(players)

        # Apply gravity
        self.vel_y += GRAVITY * delta_time

        # Update vertical position
        self.y += self.vel_y * delta_time
        self.rect.y = int(self.y)
        self.on_ground = False
        self.check_platform_collision(platforms, "vertical")
        self.check_obstacle_collision(obstacles, "vertical")

    def _update_facing_direction(self, players):
        """Always face towards the nearest alive player."""
        if not players:
            return

        # Find nearest alive player
        nearest_player = None
        min_distance = float('inf')

        for player in players:
            if player.alive:
                distance = abs(player.rect.centerx - self.rect.centerx)
                if distance < min_distance:
                    min_distance = distance
                    nearest_player = player

        if nearest_player:
            # Update facing direction based on player position
            if nearest_player.rect.centerx > self.rect.centerx:
                self.facing_direction = 1  # Face right
            else:
                self.facing_direction = -1  # Face left

    def check_platform_collision(self, platforms, direction):
        """Handle collision with platforms."""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = platform.rect.top
                        self.y = float(self.rect.y)
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Moving up
                        self.rect.top = platform.rect.bottom
                        self.y = float(self.rect.y)
                        self.vel_y = 0

    def check_obstacle_collision(self, obstacles, direction):
        """Handle collision with obstacles."""
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if direction == "vertical":
                    if self.vel_y > 0:  # Falling
                        self.rect.bottom = obstacle.rect.top
                        self.y = float(self.rect.y)
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Moving up
                        self.rect.top = obstacle.rect.bottom
                        self.y = float(self.rect.y)
                        self.vel_y = 0

    def try_shoot(self, projectiles_group, delta_time):
        """
        Fire in bursts: 6 shots 0.25 seconds apart, then 3 second cooldown.
        """
        self.shoot_timer += delta_time

        if self.in_cooldown:
            # Wait for cooldown to complete
            if self.shoot_timer >= self.burst_cooldown:
                # Cooldown complete, start new burst
                self.in_cooldown = False
                self.burst_shot_count = 0
                self.shoot_timer = 0.0
        else:
            # In burst phase
            if self.burst_shot_count < self.shots_per_burst:
                # Check if it's time to fire next shot
                if self.shoot_timer >= self.shot_interval:
                    self.shoot_timer = 0.0
                    self.burst_shot_count += 1

                    # Fire projectile
                    projectile = Projectile(
                        self.rect.centerx,
                        self.rect.centery,
                        self.facing_direction,
                        ORANGE,
                        "enemy"
                    )
                    projectiles_group.add(projectile)

                    # Check if burst is complete after firing
                    if self.burst_shot_count >= self.shots_per_burst:
                        self.in_cooldown = True
                        self.shoot_timer = 0.0
