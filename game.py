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
from platforms import Platform
from player import Player
from enemy import Enemy
from obstacles import Obstacle


class Game:
    def __init__(self, num_players=1):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Platformer")
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

        self.setup_level()
        self.setup_players()
        self.setup_enemies()

        self.game_over = False
        self.victory = False

    def setup_level(self):
        # Create platforms (Bubble Bobble style)
        platform_data = [
            # (x, y, width, height)
            (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),  # Ground
            (100, 480, 200, 15),
            (500, 480, 200, 15),
            (0, 380, 150, 15),
            (300, 380, 200, 15),
            (650, 380, 150, 15),
            (100, 280, 200, 15),
            (500, 280, 200, 15),
            (250, 180, 300, 15),
            (0, 80, 200, 15),
            (600, 80, 200, 15),
        ]

        for data in platform_data:
            platform = Platform(*data)
            self.platforms.add(platform)
            self.all_sprites.add(platform)

        # Create obstacles (2x player size: 60x80)
        obstacle_data = [
            # (x, y, width, height) - placed on top of platforms
            (150, 400, 60, 80),  # On platform at (100, 480)
            (580, 400, 60, 80),  # On platform at (500, 480)
            (350, 300, 60, 80),  # On platform at (300, 380)
            (150, 200, 60, 80),  # On platform at (100, 280)
            (350, 100, 60, 80),  # On platform at (250, 180)
        ]

        for data in obstacle_data:
            obstacle = Obstacle(*data)
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

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

    def setup_enemies(self):
        # Spawn enemies on upper platforms
        enemy_positions = [
            (150, 250),
            (550, 250),
            (350, 150),
            (50, 50),
            (650, 50),
        ]

        for pos in enemy_positions:
            enemy = Enemy(*pos)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

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

        # Check win/lose conditions
        if len(self.enemies) == 0:
            self.victory = True

        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) == 0:
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw all sprites
        self.platforms.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.players.draw(self.screen)
        self.enemies.draw(self.screen)

        # Draw UI
        font = pygame.font.Font(None, 36)

        # Enemy count
        enemy_text = font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemy_text, (10, 10))

        # Player status
        alive_players = sum(1 for p in self.players if p.alive)
        player_text = font.render(
            f"Players: {alive_players}/{self.num_players}", True, WHITE
        )
        self.screen.blit(player_text, (10, 50))

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
            victory_text = font.render("VICTORY!", True, GREEN)
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
