import pygame
from config import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    BLACK,
    WHITE,
    RED,
    FPS,
    CYAN,
    BLUE,
    GREEN,
)
import sys
import random
from platforms import Platform
from player import Player
from enemy import Enemy
from obstacles import Obstacle


class Game:
    def __init__(self, num_players=1):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Tower Climber")
        self.clock = pygame.time.Clock()
        self.running = True
        self.num_players = min(num_players, 2)

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        # Tower/Camera settings
        self.camera_y = 0  # Camera vertical offset
        self.tower_height = 10000  # Total height of the tower
        self.platform_generation_threshold = SCREEN_HEIGHT * 2  # Generate platforms ahead
        self.highest_platform_y = 0  # Track highest generated platform

        self.setup_level()
        self.setup_players()

        self.game_over = False
        self.victory = False

    def setup_level(self):
        # Generate initial platforms for the tower
        # Start with ground platform
        ground = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
        self.platforms.add(ground)
        self.all_sprites.add(ground)

        # Set starting position for generation
        self.highest_platform_y = SCREEN_HEIGHT - 20

        # Generate initial set of platforms
        self.generate_platforms_upward()

    def generate_platforms_upward(self):
        # Generate platforms from highest_platform_y up to the threshold
        target_y = self.highest_platform_y - self.platform_generation_threshold

        # Don't generate below the tower top
        if self.highest_platform_y <= -self.tower_height:
            return

        current_y = self.highest_platform_y
        new_platforms = []

        # Fixed platform properties
        platform_width = int(SCREEN_WIDTH / 3)  # Exactly 1/3 of screen width (266 pixels)
        platform_height = 15
        player_height = 60  # Height of player sprite

        # Vertical spacing: at least 1 player height + 25%
        vertical_gap = int(player_height * 1.25)  # 75 pixels

        # Staggered positions: alternating left-right pattern with overlap
        # Player can jump ~110 pixels horizontally at 75px height
        # Use 2 positions that overlap to ensure all jumps are reachable

        # Position platforms with significant overlap for safety
        left_x = 100  # Left platform: 100-366
        right_x = 280  # Right platform: 280-546 (overlaps left by 86 pixels)

        positions = [left_x, right_x]

        # Determine starting position based on number of existing platforms
        # Ground platform doesn't count, so subtract 1 to start at position 0 (left)
        platform_count = len(self.platforms) - 1  # Subtract 1 for ground platform
        position_index = platform_count % 2

        while current_y > target_y and current_y > -self.tower_height:
            current_y -= vertical_gap

            # Get position for this platform (cycles through left, center, right)
            platform_x = positions[position_index]

            # Create the platform
            platform = Platform(platform_x, current_y, platform_width, platform_height)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
            new_platforms.append(platform)

            # Move to next position in cycle
            position_index = (position_index + 1) % 2

        # Update highest platform position
        self.highest_platform_y = current_y

        # Generate enemies on some of the new platforms
        self.generate_enemies_on_platforms(new_platforms)

    def generate_enemies_on_platforms(self, platforms):
        # Spawn enemies on approximately 30% of platforms
        for platform in platforms:
            # Skip ground platform and very low platforms
            if platform.rect.y >= SCREEN_HEIGHT - 100:
                continue

            # 30% chance to spawn an enemy on this platform
            if random.random() < 0.3:
                # Place enemy on top of platform, roughly in the middle
                enemy_x = platform.rect.x + platform.rect.width // 2 - 15
                enemy_y = platform.rect.y - 40  # Enemy height is about 40px

                enemy = Enemy(enemy_x, enemy_y)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

    def setup_players(self):
        # Player 1 controls
        player1_controls = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "shoot": pygame.K_SPACE,
        }
        player1 = Player(100, SCREEN_HEIGHT - 100, BLUE, player1_controls)
        self.players.add(player1)
        self.all_sprites.add(player1)

        if self.num_players == 2:
            # Player 2 controls
            player2_controls = {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "jump": pygame.K_UP,
                "shoot": pygame.K_RSHIFT,
            }
            player2 = Player(
                SCREEN_WIDTH - 130, SCREEN_HEIGHT - 100, CYAN, player2_controls
            )
            self.players.add(player2)
            self.all_sprites.add(player2)

    def update_camera(self):
        # Get the highest player position
        if len(self.players) == 0:
            return

        highest_player_y = min(player.rect.y for player in self.players if player.alive)

        # Camera follows player when they're in the upper half of the screen
        camera_threshold = SCREEN_HEIGHT // 3
        if highest_player_y < camera_threshold:
            # Move camera up
            self.camera_y = highest_player_y - camera_threshold

        # Generate more platforms if needed
        if self.camera_y < self.highest_platform_y + self.platform_generation_threshold:
            self.generate_platforms_upward()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.game_over or self.victory:
                    if event.key == pygame.K_r:
                        self.__init__(self.num_players)  # Restart
                    elif event.key == pygame.K_q:
                        self.running = False
                else:
                    # Player 1 shoot
                    if event.key == pygame.K_SPACE:
                        player_list = list(self.players)
                        if len(player_list) > 0:
                            player_list[0].shoot(self.projectiles)

                    # Player 2 shoot
                    if event.key == pygame.K_RSHIFT:
                        player_list = list(self.players)
                        if len(player_list) > 1:
                            player_list[1].shoot(self.projectiles)

    def update(self, delta_time):
        if self.game_over or self.victory:
            return

        # Update camera position
        self.update_camera()

        # Update all sprites with delta_time
        for player in self.players:
            player.update(self.platforms, self.obstacles, delta_time)

        for enemy in self.enemies:
            enemy.update(self.platforms, self.obstacles, delta_time)
            enemy.try_shoot(self.projectiles, delta_time)

        self.projectiles.update(delta_time)

        # Check projectile collisions
        for projectile in self.projectiles:
            # Check if projectile hits obstacles
            hit_obstacles = pygame.sprite.spritecollide(
                projectile, self.obstacles, False
            )
            if hit_obstacles:
                projectile.kill()
                continue

            if projectile.owner_type == "player":
                # Player projectiles hit enemies
                hit_enemies = pygame.sprite.spritecollide(
                    projectile, self.enemies, True
                )
                if hit_enemies:
                    projectile.kill()

            elif projectile.owner_type == "enemy":
                # Enemy projectiles hit players
                for player in self.players:
                    if player.alive and projectile.rect.colliderect(player.rect):
                        player.alive = False
                        player.kill()
                        projectile.kill()

        # Check if player reached the top
        for player in self.players:
            if player.alive and player.rect.y <= -self.tower_height + 100:
                self.victory = True

        # Check if player fell off the bottom (below camera view)
        alive_players = [p for p in self.players if p.alive]
        for player in alive_players:
            if player.rect.y > self.camera_y + SCREEN_HEIGHT + 100:
                player.alive = False
                player.kill()

        # Check lose condition
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) == 0:
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw all sprites with camera offset
        for platform in self.platforms:
            offset_rect = platform.rect.copy()
            offset_rect.y -= self.camera_y
            # Only draw if on screen
            if -50 < offset_rect.y < SCREEN_HEIGHT + 50:
                self.screen.blit(platform.image, offset_rect)

        for obstacle in self.obstacles:
            offset_rect = obstacle.rect.copy()
            offset_rect.y -= self.camera_y
            if -100 < offset_rect.y < SCREEN_HEIGHT + 100:
                self.screen.blit(obstacle.image, offset_rect)

        for projectile in self.projectiles:
            offset_rect = projectile.rect.copy()
            offset_rect.y -= self.camera_y
            if -50 < offset_rect.y < SCREEN_HEIGHT + 50:
                self.screen.blit(projectile.image, offset_rect)

        for player in self.players:
            offset_rect = player.rect.copy()
            offset_rect.y -= self.camera_y
            self.screen.blit(player.image, offset_rect)

        for enemy in self.enemies:
            offset_rect = enemy.rect.copy()
            offset_rect.y -= self.camera_y
            if -100 < offset_rect.y < SCREEN_HEIGHT + 100:
                self.screen.blit(enemy.image, offset_rect)

        # Draw UI
        font = pygame.font.Font(None, 36)

        # Height climbed (distance from starting ground)
        if len(self.players) > 0:
            highest_player = min(player.rect.y for player in self.players if player.alive) if any(p.alive for p in self.players) else SCREEN_HEIGHT
            height_climbed = max(0, (SCREEN_HEIGHT - 20) - highest_player)
            height_text = font.render(f"Height: {int(height_climbed)}", True, WHITE)
            self.screen.blit(height_text, (10, 10))

            # Progress to top
            progress = min(100, int((height_climbed / self.tower_height) * 100))
            progress_text = font.render(f"Progress: {progress}%", True, WHITE)
            self.screen.blit(progress_text, (10, 50))

        # Enemy count
        enemy_text = font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemy_text, (10, 90))

        # Player status
        alive_players = sum(1 for p in self.players if p.alive)
        player_text = font.render(
            f"Players: {alive_players}/{self.num_players}", True, WHITE
        )
        self.screen.blit(player_text, (10, 130))

        # Game over / victory messages
        if self.game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            restart_text = font.render("Press R to restart or Q to quit", True, WHITE)
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        if self.victory:
            victory_text = font.render("YOU REACHED THE TOP!", True, GREEN)
            restart_text = font.render("Press R to restart or Q to quit", True, WHITE)
            text_rect = victory_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(victory_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            # Get delta_time in seconds
            delta_time = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()
