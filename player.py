from pygame.sprite import Sprite
import pygame
from projectile import Projectile
from spritesheet import SpriteSheet
from config import (
    PLAYER_SPEED,
    PLAYER_JUMP,
    PLAYER_CLIMB_SPEED,
    GRAVITY,
    SCREEN_WIDTH,
    YELLOW,
)


class Player(Sprite):
    def __init__(self, x, y, color, controls):
        super().__init__()

        # Load sprite animations
        self.animation_delay = 4  # Lower delay for faster animation
        self.idle_counter = 0
        self.run_counter = 0

        # Idle animation (11 frames)
        self.idle_state = 0
        self.idle_length = 11
        player_idle = SpriteSheet(pygame.image.load("./Assets/Player/player_idle.png"))
        self.idle_frames = [
            player_idle.getimage(32 * x, 0, 32, 32) for x in range(self.idle_length)
        ]
        self.idle_frames_flipped = []
        for i in range(len(self.idle_frames)):
            self.idle_frames[i] = pygame.transform.scale(self.idle_frames[i], (45, 60))
            self.idle_frames_flipped.append(
                pygame.transform.flip(self.idle_frames[i], True, False)
            )

        # Run animation (12 frames)
        self.run_state = 0
        self.run_length = 12
        player_run = SpriteSheet(pygame.image.load("./Assets/Player/player_run.png"))
        self.run_frames = [
            player_run.getimage(32 * x, 0, 32, 32) for x in range(self.run_length)
        ]
        self.run_frames_flipped = []
        for i in range(len(self.run_frames)):
            self.run_frames[i] = pygame.transform.scale(self.run_frames[i], (45, 60))
            self.run_frames_flipped.append(
                pygame.transform.flip(self.run_frames[i], True, False)
            )

        # Jump and fall (single frames)
        self.jump_frame = pygame.transform.scale(
            pygame.image.load("./Assets/Player/player_jump.png"), (45, 60)
        )
        self.jump_frame_flipped = pygame.transform.flip(self.jump_frame, True, False)

        self.fall_frame = pygame.transform.scale(
            pygame.image.load("./Assets/Player/player_fall.png"), (45, 60)
        )
        self.fall_frame_flipped = pygame.transform.flip(self.fall_frame, True, False)

        # Set initial image
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.x = float(x)  # Store position as floats
        self.y = float(y)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.controls = controls
        self.alive = True
        self.color = color  # Keep for backwards compatibility

        # Climbing state
        self.on_ladder = False
        self.climbing = False

    def update(self, platforms, obstacles, ladders, delta_time):
        if not self.alive:
            return

        keys = pygame.key.get_pressed()

        # Check if player is touching a ladder
        self.on_ladder = self._check_ladder_collision(ladders)

        # Determine climbing state
        if self.on_ladder:
            # Start climbing if player presses up while on ladder
            if keys[self.controls["jump"]]:  # W or UP key
                self.climbing = True
        else:
            self.climbing = False

        # Handle movement based on climbing state
        if self.climbing:
            # Climbing mode - disable gravity and allow up/down movement
            self.vel_y = 0

            # Vertical climbing movement
            if keys[self.controls["jump"]]:  # W or UP - climb up
                self.vel_y = -PLAYER_CLIMB_SPEED
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:  # S or DOWN - climb down
                self.vel_y = PLAYER_CLIMB_SPEED

            # Horizontal movement (slower while on ladder)
            self.vel_x = 0
            if keys[self.controls["left"]]:
                self.vel_x = -PLAYER_SPEED * 0.5  # Half speed on ladder
                self.facing_right = False
            if keys[self.controls["right"]]:
                self.vel_x = PLAYER_SPEED * 0.5  # Half speed on ladder
                self.facing_right = True

            # Jump off ladder
            if (keys[self.controls["left"]] or keys[self.controls["right"]]) and (
                keys[pygame.K_SPACE] or keys[pygame.K_RSHIFT]
            ):
                # Player wants to jump off sideways
                self.climbing = False
                self.vel_y = PLAYER_JUMP * 0.7  # Smaller jump when jumping off ladder
                self.on_ground = False

        else:
            # Normal movement mode
            # Horizontal movement
            self.vel_x = 0
            if keys[self.controls["left"]]:
                self.vel_x = -PLAYER_SPEED
                self.facing_right = False
            if keys[self.controls["right"]]:
                self.vel_x = PLAYER_SPEED
                self.facing_right = True

            # Jumping (only when on ground, not on ladder)
            if keys[self.controls["jump"]] and self.on_ground:
                self.vel_y = PLAYER_JUMP
                self.on_ground = False

            # Apply gravity (only when not climbing)
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

        # Exit climbing if moved too far from ladder
        if self.climbing and not self.on_ladder:
            self.climbing = False

        # Keep player on screen horizontally (but allow vertical movement for scrolling)
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = float(self.rect.x)
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = float(self.rect.x)

        # Update sprite direction
        self._update_animation()

    def _check_ladder_collision(self, ladders):
        """Check if player is touching any ladder."""
        for ladder in ladders:
            if self.rect.colliderect(ladder.rect):
                return True
        return False

    def check_platform_collision(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:  # Moving right
                        self.rect.right = platform.rect.left
                        self.x = float(self.rect.x)
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                        self.x = float(self.rect.x)
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
                    elif self.vel_x < 0:  # Moving left
                        self.rect.left = obstacle.rect.right
                        self.x = float(self.rect.x)
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

    def _update_animation(self):
        """Animate when walking, static when idle"""
        if self.vel_x != 0:
            # Walking - animate through run frames
            if self.run_counter >= self.animation_delay:
                self.run_state = (self.run_state + 1) % self.run_length
                self.run_counter = 0
            else:
                self.run_counter += 1

            if self.facing_right:
                self.image = self.run_frames[self.run_state]
            else:
                self.image = self.run_frames_flipped[self.run_state]
        else:
            # Standing still - static idle frame
            self.run_counter = 0
            self.run_state = 0

            if self.facing_right:
                self.image = self.idle_frames[0]
            else:
                self.image = self.idle_frames_flipped[0]

    def shoot(self, projectiles_group):
        if not self.alive:
            return
        direction = 1 if self.facing_right else -1
        projectile = Projectile(
            self.rect.centerx, self.rect.centery, direction, YELLOW, "player"
        )
        projectiles_group.add(projectile)
