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
from player import Player
from exit import Exit
from map_loader import MapLoader
from maps import ALL_MAPS


class Game:
    def __init__(self, num_players=1, map_name="test"):
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Tower Climber")
        self.clock = pygame.time.Clock()
        self.running = True
        self.num_players = min(num_players, 2)
        self.map_name = map_name

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.exit_sprite = None

        # Camera settings
        self.camera_y = 0  # Camera vertical offset

        # Map loader
        self.map_loader = MapLoader(tile_size=40)

        # Store spawn points from map
        self.spawn_points = []

        self.setup_level()
        self.setup_players()
        self.initialize_camera()

        self.game_over = False
        self.victory = False

    def setup_level(self):
        # Load map data
        map_data = ALL_MAPS.get(self.map_name, ALL_MAPS["test"])

        # Parse the map
        map_objects = self.map_loader.load_map(map_data)
        sprites = self.map_loader.create_sprites(map_objects)

        # Add platforms
        for platform in sprites["platforms"]:
            self.platforms.add(platform)
            self.all_sprites.add(platform)

        # Add enemies
        for enemy in sprites["enemies"]:
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Add obstacles
        for obstacle in sprites["obstacles"]:
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Add ladders
        for ladder in sprites["ladders"]:
            self.ladders.add(ladder)
            self.all_sprites.add(ladder)

        # Store spawn points for player setup
        self.spawn_points = sprites["spawn_points"]

        # Create exit sprite
        if sprites["exit_pos"]:
            exit_x, exit_y = sprites["exit_pos"]
            self.exit_sprite = Exit(exit_x, exit_y)
            self.all_sprites.add(self.exit_sprite)

    def setup_players(self):
        # Use spawn points from map, or default positions if not available
        if len(self.spawn_points) > 0:
            spawn_x, spawn_y = self.spawn_points[0]
        else:
            spawn_x, spawn_y = 100, SCREEN_HEIGHT - 100

        # Player 1 controls
        player1_controls = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "shoot": pygame.K_SPACE,
        }
        player1 = Player(spawn_x, spawn_y, BLUE, player1_controls)
        self.players.add(player1)
        self.all_sprites.add(player1)

        if self.num_players == 2:
            # Player 2 spawn - use second spawn point if available, or offset from first
            if len(self.spawn_points) > 1:
                spawn2_x, spawn2_y = self.spawn_points[1]
            else:
                spawn2_x, spawn2_y = spawn_x + 60, spawn_y

            # Player 2 controls
            player2_controls = {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "jump": pygame.K_UP,
                "shoot": pygame.K_RSHIFT,
            }
            player2 = Player(spawn2_x, spawn2_y, CYAN, player2_controls)
            self.players.add(player2)
            self.all_sprites.add(player2)

    def initialize_camera(self):
        # Position camera so player spawn is visible at bottom of screen
        if len(self.spawn_points) > 0:
            spawn_y = self.spawn_points[0][1]
            # Position spawn point in lower portion of screen (about 2/3 down)
            target_screen_y = SCREEN_HEIGHT * 2 // 3
            self.camera_y = spawn_y - target_screen_y

    def update_camera(self):
        # Get the highest player position
        if len(self.players) == 0:
            return

        highest_player_y = min(player.rect.y for player in self.players if player.alive)

        # Calculate player's position on screen
        player_screen_y = highest_player_y - self.camera_y

        # Camera follows player to keep them in a comfortable viewing area
        # Define upper and lower thresholds
        upper_threshold = SCREEN_HEIGHT // 3  # Upper third of screen
        lower_threshold = SCREEN_HEIGHT * 2 // 3  # Lower third of screen

        if player_screen_y < upper_threshold:
            # Player is too high on screen - move camera up
            self.camera_y = highest_player_y - upper_threshold
        elif player_screen_y > lower_threshold:
            # Player is too low on screen - move camera down
            self.camera_y = highest_player_y - lower_threshold

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.game_over or self.victory:
                    if event.key == pygame.K_r:
                        self.__init__(self.num_players, self.map_name)  # Restart
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
            player.update(self.platforms, self.obstacles, self.ladders, delta_time)

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

        # Check if player reached the exit
        if self.exit_sprite:
            for player in self.players:
                if player.alive and player.rect.colliderect(self.exit_sprite.rect):
                    self.victory = True

        # Check if player fell off the bottom (below camera view)
        alive_players = [p for p in self.players if p.alive]
        for player in alive_players:
            if player.rect.y > self.camera_y + SCREEN_HEIGHT + 100:
                player.alive = False
                player.kill()

        # Remove enemies that fell too far off screen
        for enemy in list(self.enemies):
            if enemy.rect.y > self.camera_y + SCREEN_HEIGHT + 200:
                enemy.kill()

        # Check lose condition
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) == 0:
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw all sprites with camera offset
        # Draw ladders first (in background)
        for ladder in self.ladders:
            offset_rect = ladder.rect.copy()
            offset_rect.y -= self.camera_y
            # Only draw if on screen
            if -100 < offset_rect.y < SCREEN_HEIGHT + 100:
                self.screen.blit(ladder.image, offset_rect)

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

        # Draw exit
        if self.exit_sprite:
            offset_rect = self.exit_sprite.rect.copy()
            offset_rect.y -= self.camera_y
            if -100 < offset_rect.y < SCREEN_HEIGHT + 100:
                self.screen.blit(self.exit_sprite.image, offset_rect)

        # Draw UI
        font = pygame.font.Font(None, 36)

        # Height climbed (distance from spawn point)
        if len(self.players) > 0 and len(self.spawn_points) > 0:
            spawn_y = self.spawn_points[0][1]
            highest_player = (
                min(player.rect.y for player in self.players if player.alive)
                if any(p.alive for p in self.players)
                else spawn_y
            )
            height_climbed = max(0, spawn_y - highest_player)
            height_text = font.render(f"Height: {int(height_climbed)}", True, WHITE)
            self.screen.blit(height_text, (10, 10))

            # Progress to exit
            if self.exit_sprite:
                total_height = spawn_y - self.exit_sprite.rect.y
                progress = (
                    min(100, int((height_climbed / total_height) * 100))
                    if total_height > 0
                    else 0
                )
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
