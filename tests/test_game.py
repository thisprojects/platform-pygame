import pytest
import pygame
from game import Game
from unittest.mock import patch, MagicMock


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def game(pygame_init):
    with patch('random.choice'):
        with patch('random.randint'):
            return Game(num_players=1)


class TestGame:
    def test_game_initialization_single_player(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)

                assert game.num_players == 1
                assert game.running is True
                assert game.game_over is False
                assert game.victory is False

    def test_game_initialization_two_players(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=2)

                assert game.num_players == 2
                assert len(game.players) == 2

    def test_game_initialization_max_players(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=5)

                assert game.num_players == 2

    def test_game_platforms_created(self, game):
        assert len(game.platforms) > 0

    def test_game_players_created(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)

                assert len(game.players) == 1

    def test_game_enemies_created(self, game):
        assert len(game.enemies) > 0

    def test_game_obstacles_created(self, game):
        assert len(game.obstacles) > 0

    def test_game_obstacles_count(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                # Should have 5 obstacles based on setup_level
                assert len(game.obstacles) == 5

    def test_game_obstacles_in_all_sprites(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                # All obstacles should be in all_sprites group
                for obstacle in game.obstacles:
                    assert obstacle in game.all_sprites

    def test_game_sprite_groups_initialized(self, game):
        assert isinstance(game.all_sprites, pygame.sprite.Group)
        assert isinstance(game.platforms, pygame.sprite.Group)
        assert isinstance(game.players, pygame.sprite.Group)
        assert isinstance(game.enemies, pygame.sprite.Group)
        assert isinstance(game.projectiles, pygame.sprite.Group)
        assert isinstance(game.obstacles, pygame.sprite.Group)

    def test_victory_when_all_enemies_defeated(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                game.enemies.empty()

                game.update()

                assert game.victory is True

    def test_game_over_when_all_players_dead(self, pygame_init):
        with patch('random.choice', return_value=2):
            with patch('random.randint', return_value=60):
                game = Game(num_players=1)

                for player in game.players:
                    player.alive = False
                    player.kill()

                game.update()

                assert game.game_over is True

    def test_player_projectile_hits_enemy(self, pygame_init):
        with patch('random.choice', return_value=0):  # Enemy won't move
            with patch('random.randint', return_value=1000):  # Large timer
                with patch('random.random', return_value=0.999):
                    game = Game(num_players=1)

                    # Clear all obstacles to ensure projectile path is clear
                    game.obstacles.empty()

                    initial_enemy_count = len(game.enemies)

                    player = list(game.players)[0]
                    enemy = list(game.enemies)[0]

                    # Create projectile directly at enemy position
                    from projectile import Projectile
                    from config import YELLOW
                    projectile = Projectile(enemy.rect.centerx, enemy.rect.centery,
                                          1, YELLOW, 'player')
                    game.projectiles.add(projectile)

                    game.update()

                    assert len(game.enemies) < initial_enemy_count
                    assert len(game.projectiles) == 0

    def test_enemy_projectile_hits_player(self, pygame_init):
        with patch('random.choice', return_value=2):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.999):
                    game = Game(num_players=1)
                    player = list(game.players)[0]

                    from projectile import Projectile
                    from config import PURPLE
                    enemy_projectile = Projectile(player.rect.x, player.rect.y,
                                                1, PURPLE, 'enemy')
                    game.projectiles.add(enemy_projectile)

                    game.update()

                    assert player.alive is False

    def test_update_does_nothing_when_game_over(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                game.game_over = True

                initial_projectile_count = len(game.projectiles)

                game.update()

                assert len(game.projectiles) == initial_projectile_count

    def test_update_does_nothing_when_victory(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                game.victory = True

                initial_projectile_count = len(game.projectiles)

                game.update()

                assert len(game.projectiles) == initial_projectile_count

    def test_handle_events_quit(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)

                quit_event = pygame.event.Event(pygame.QUIT)
                pygame.event.post(quit_event)

                game.handle_events()

                assert game.running is False

    def test_handle_events_player1_shoot(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)

                shoot_event = pygame.event.Event(pygame.KEYDOWN,
                                                 {'key': pygame.K_SPACE})
                pygame.event.post(shoot_event)

                game.handle_events()

                assert len(game.projectiles) == 1

    def test_handle_events_player2_shoot(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=2)

                shoot_event = pygame.event.Event(pygame.KEYDOWN,
                                                 {'key': pygame.K_RSHIFT})
                pygame.event.post(shoot_event)

                game.handle_events()

                assert len(game.projectiles) == 1

    def test_handle_events_restart_on_game_over(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                game.game_over = True

                restart_event = pygame.event.Event(pygame.KEYDOWN,
                                                   {'key': pygame.K_r})
                pygame.event.post(restart_event)

                game.handle_events()

                assert game.game_over is False

    def test_handle_events_quit_on_game_over(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                game.game_over = True

                quit_event = pygame.event.Event(pygame.KEYDOWN,
                                                {'key': pygame.K_q})
                pygame.event.post(quit_event)

                game.handle_events()

                assert game.running is False

    def test_player_shoot_when_no_players(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)
                game.players.empty()

                shoot_event = pygame.event.Event(pygame.KEYDOWN,
                                                 {'key': pygame.K_SPACE})
                pygame.event.post(shoot_event)

                game.handle_events()

                assert len(game.projectiles) == 0

    def test_multiple_players_alive_check(self, pygame_init):
        with patch('random.choice', return_value=2):
            with patch('random.randint', return_value=60):
                game = Game(num_players=2)

                player_list = list(game.players)
                player_list[0].alive = False
                player_list[0].kill()

                game.update()

                assert game.game_over is False

                player_list[1].alive = False
                player_list[1].kill()

                game.update()

                assert game.game_over is True

    def test_draw_does_not_crash(self, pygame_init):
        with patch('random.choice'):
            with patch('random.randint'):
                game = Game(num_players=1)

                try:
                    game.draw()
                    success = True
                except Exception:
                    success = False

                assert success is True

    def test_projectile_blocked_by_obstacle(self, pygame_init):
        with patch('random.choice', return_value=0):
            with patch('random.randint', return_value=60):
                game = Game(num_players=1)

                # Create projectile and obstacle
                from projectile import Projectile
                from config import YELLOW
                from obstacles import Obstacle

                obstacle = Obstacle(200, 200, 60, 80)
                game.obstacles.add(obstacle)

                projectile = Projectile(obstacle.rect.centerx, obstacle.rect.centery,
                                      1, YELLOW, 'player')
                game.projectiles.add(projectile)

                game.update()

                # Projectile should be destroyed by obstacle
                assert len(game.projectiles) == 0

    def test_enemy_projectile_blocked_by_obstacle(self, pygame_init):
        with patch('random.choice', return_value=0):
            with patch('random.randint', return_value=60):
                game = Game(num_players=1)

                # Create enemy projectile and obstacle
                from projectile import Projectile
                from config import PURPLE
                from obstacles import Obstacle

                obstacle = Obstacle(200, 200, 60, 80)
                game.obstacles.add(obstacle)

                projectile = Projectile(obstacle.rect.centerx, obstacle.rect.centery,
                                      -1, PURPLE, 'enemy')
                game.projectiles.add(projectile)

                game.update()

                # Projectile should be destroyed by obstacle
                assert len(game.projectiles) == 0
