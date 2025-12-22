from pygame.sprite import Sprite
import pygame
from config import (
    RED,
    ENEMY_SPEED,
    SCREEN_WIDTH,
    GRAVITY,
    ENEMY_SHOOT_CHANCE,
    PURPLE,
    ENEMY_ALERT_DURATION,
    ENEMY_RAYCAST_INTERVAL,
    ENEMY_DETECTION_VERTICAL_TOLERANCE,
    ENEMY_BURST_SHOT_COUNT,
    ENEMY_BURST_SHOT_INTERVAL,
    ENEMY_BURST_COOLDOWN,
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

        # Alert mode state variables
        self.alert_state = "PATROL"  # "PATROL", "ALERT", or "COOLDOWN"
        self.alert_timer = 0.0
        self.alert_duration = ENEMY_ALERT_DURATION
        self.shoot_timer = 0.0
        self.last_seen_player_x = None
        self.facing_direction = 1 if self.vel_x >= 0 else -1
        self.raycast_interval = ENEMY_RAYCAST_INTERVAL
        self.raycast_timer = 0.0

        # Burst fire settings
        self.burst_shot_count = 0  # Tracks shots fired in current burst
        self.burst_shots_per_burst = ENEMY_BURST_SHOT_COUNT
        self.burst_shot_interval = ENEMY_BURST_SHOT_INTERVAL
        self.burst_cooldown = ENEMY_BURST_COOLDOWN

    def update(self, platforms, obstacles, players, camera_y, delta_time):
        # Update alert state machine
        self._update_alert_state(players, platforms, obstacles, camera_y, delta_time)

        # Movement behavior depends on alert state
        if self.alert_state == "ALERT":
            # Completely stationary when alerted
            self.vel_x = 0
        else:
            # Normal patrol behavior
            # Check for platform edges and reverse direction
            if self._check_platform_edge(platforms, delta_time):
                self.vel_x = -self.vel_x
                self.facing_direction = 1 if self.vel_x > 0 else -1

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
            self.facing_direction = 1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = float(self.rect.x)
            self.vel_x = -ENEMY_SPEED
            self.facing_direction = -1

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

    def _raycast_to_player(self, player, platforms, obstacles, max_distance=SCREEN_WIDTH):
        """
        Cast a ray from enemy to player to check if there's a clear line of sight.
        Returns True if player is visible (no obstacles blocking).
        """
        # Get center positions
        enemy_center_x = self.rect.centerx
        enemy_center_y = self.rect.centery
        player_center_x = player.rect.centerx
        player_center_y = player.rect.centery

        # Check if player is roughly at same height (within tolerance)
        vertical_distance = abs(player_center_y - enemy_center_y)
        if vertical_distance > ENEMY_DETECTION_VERTICAL_TOLERANCE:
            return False

        # Determine horizontal direction and distance
        direction = 1 if player_center_x > enemy_center_x else -1
        horizontal_distance = abs(player_center_x - enemy_center_x)

        if horizontal_distance > max_distance:
            return False

        # Cast ray in steps checking for collisions
        step_size = 10  # Check every 10 pixels
        num_steps = int(horizontal_distance / step_size)

        for i in range(1, num_steps + 1):
            # Calculate point along ray
            check_x = enemy_center_x + (direction * step_size * i)
            check_y = enemy_center_y

            # Create small test rect
            test_rect = pygame.Rect(check_x - 2, check_y - 2, 4, 4)

            # Check collision with platforms
            for platform in platforms:
                if test_rect.colliderect(platform.rect):
                    return False  # Line of sight blocked

            # Check collision with obstacles
            for obstacle in obstacles:
                if test_rect.colliderect(obstacle.rect):
                    return False  # Line of sight blocked

        return True  # Clear line of sight

    def _check_player_detection(self, players, platforms, obstacles, delta_time):
        """
        Check if any player is visible via raycast. Returns detected player or None.
        Uses timer to avoid raycasting every frame.
        """
        self.raycast_timer += delta_time

        # Only raycast periodically for performance
        if self.raycast_timer < self.raycast_interval:
            return None

        self.raycast_timer = 0.0

        # Only raycast when on ground (enemies on ground are more stable)
        if not self.on_ground:
            return None

        # Check each player
        for player in players:
            if not player.alive:
                continue

            can_see = self._raycast_to_player(player, platforms, obstacles)
            if can_see:
                return player

        return None

    def _enter_alert_state(self, player):
        """Enter alert state when player is detected."""
        self.alert_state = "ALERT"
        self.alert_timer = 0.0
        self.shoot_timer = self.burst_shot_interval  # Set to interval so it fires immediately
        self.burst_shot_count = 0  # Reset burst counter
        self.last_seen_player_x = player.rect.centerx
        self.facing_direction = 1 if player.rect.centerx > self.rect.centerx else -1

    def _exit_alert_state(self):
        """Exit alert state and enter cooldown."""
        self.alert_state = "COOLDOWN"
        self.alert_cooldown = 0.0
        # Resume patrol movement in current facing direction
        self.vel_x = self.facing_direction * ENEMY_SPEED

    def _update_alert_state(self, players, platforms, obstacles, camera_y, delta_time):
        """
        Update alert state machine based on player detection and timers.
        """
        if self.alert_state == "PATROL":
            # Check for player detection via raycast
            detected_player = self._check_player_detection(players, platforms, obstacles, delta_time)

            if detected_player:
                self._enter_alert_state(detected_player)

        elif self.alert_state == "ALERT":
            # Update alert timer
            self.alert_timer += delta_time

            # Check if alert duration expired
            if self.alert_timer >= self.alert_duration:
                self._exit_alert_state()
            else:
                # Re-check for player to refresh alert or update facing
                detected_player = self._check_player_detection(players, platforms, obstacles, delta_time)

                if detected_player:
                    # Refresh alert timer and update facing (but don't reset shoot timer)
                    self.alert_timer = 0.0
                    self.last_seen_player_x = detected_player.rect.centerx
                    self.facing_direction = 1 if detected_player.rect.centerx > self.rect.centerx else -1

        elif self.alert_state == "COOLDOWN":
            # Cooldown timer
            self.alert_cooldown += delta_time

            if self.alert_cooldown >= 2.0:  # 2 second cooldown
                self.alert_state = "PATROL"
                self.alert_cooldown = 0.0

    def try_shoot(self, projectiles_group, delta_time):
        """
        Shooting behavior depends on alert state.
        PATROL: Random shooting
        ALERT: Burst fire - 3 shots 1 second apart, then 3 second cooldown
        """
        if self.alert_state == "ALERT":
            # Alert mode: burst fire
            self.shoot_timer += delta_time

            # Check if we're in burst phase or cooldown phase
            if self.burst_shot_count < self.burst_shots_per_burst:
                # We're in burst phase - check if it's time to fire next shot
                if self.shoot_timer >= self.burst_shot_interval:
                    self.shoot_timer = 0.0
                    self.burst_shot_count += 1

                    # Fire projectile
                    projectile = Projectile(
                        self.rect.centerx,
                        self.rect.centery,
                        self.facing_direction,
                        PURPLE,
                        "enemy"
                    )
                    projectiles_group.add(projectile)
            else:
                # We're in cooldown phase - wait for burst_cooldown before next burst
                if self.shoot_timer >= self.burst_cooldown:
                    # Reset for next burst - set timer to interval so it fires immediately
                    self.shoot_timer = self.burst_shot_interval
                    self.burst_shot_count = 0
        else:
            # Patrol mode: random shooting (existing behavior)
            if random.random() < ENEMY_SHOOT_CHANCE * delta_time:
                direction = 1 if self.vel_x >= 0 else -1
                if self.vel_x == 0:
                    direction = self.facing_direction  # Use stored facing direction
                projectile = Projectile(
                    self.rect.centerx, self.rect.centery, direction, PURPLE, "enemy"
                )
                projectiles_group.add(projectile)
