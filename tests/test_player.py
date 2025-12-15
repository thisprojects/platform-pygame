import pytest
import pygame
import sys
import os
import importlib.util
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load the local platforms module to avoid conflict with built-in platform module
platforms_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'platforms.py'))
spec = importlib.util.spec_from_file_location("platform_module", platforms_path)
platform_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_module)
Platform = platform_module.Platform

from player import Player
from obstacles import Obstacle
from config import (PLAYER_SPEED, PLAYER_JUMP, GRAVITY, SCREEN_WIDTH,
                    SCREEN_HEIGHT, BLUE, YELLOW)


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def player_controls():
    return {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'jump': pygame.K_w,
        'shoot': pygame.K_SPACE
    }


@pytest.fixture
def player(pygame_init, player_controls):
    return Player(100, 100, BLUE, player_controls)


class TestPlayer:
    def test_player_creation(self, player):
        assert player.rect.x == 100
        assert player.rect.y == 100
        assert player.alive is True
        assert player.vel_x == 0
        assert player.vel_y == 0
        assert player.on_ground is False
        assert player.facing_right is True

    def test_player_is_sprite(self, player):
        assert isinstance(player, pygame.sprite.Sprite)

    @patch('pygame.key.get_pressed')
    def test_player_move_right(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        platforms = []
        obstacles = []

        # Create a dict-like object that returns False for any key not explicitly set
        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['right']] = True
        mock_keys.return_value = keys_pressed
        initial_x = player.rect.x

        player.update(platforms, obstacles)

        assert player.facing_right is True
        assert player.rect.x == initial_x + PLAYER_SPEED

    @patch('pygame.key.get_pressed')
    def test_player_move_left(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['left']] = True
        mock_keys.return_value = keys_pressed
        initial_x = player.rect.x

        player.update(platforms, obstacles)

        assert player.facing_right is False
        assert player.rect.x == initial_x - PLAYER_SPEED

    @patch('pygame.key.get_pressed')
    def test_player_gravity_applied(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        mock_keys.return_value = keys_pressed
        initial_y = player.rect.y
        initial_vel_y = player.vel_y

        player.update(platforms, obstacles)

        assert player.vel_y == initial_vel_y + GRAVITY
        assert player.rect.y > initial_y

    @patch('pygame.key.get_pressed')
    def test_player_jump(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        player.on_ground = True
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['jump']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        # After update, gravity is applied, so vel_y = PLAYER_JUMP + GRAVITY
        assert player.vel_y == PLAYER_JUMP + GRAVITY
        assert player.on_ground is False

    @patch('pygame.key.get_pressed')
    def test_player_cannot_jump_in_air(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        player.on_ground = False
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['jump']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        assert player.vel_y != PLAYER_JUMP

    @patch('pygame.key.get_pressed')
    def test_player_screen_boundary_left(self, mock_keys, pygame_init, player_controls):
        player = Player(0, 100, BLUE, player_controls)
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['left']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        assert player.rect.left >= 0

    @patch('pygame.key.get_pressed')
    def test_player_screen_boundary_right(self, mock_keys, pygame_init, player_controls):
        player = Player(SCREEN_WIDTH - 30, 100, BLUE, player_controls)
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['right']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        assert player.rect.right <= SCREEN_WIDTH

    @patch('pygame.key.get_pressed')
    def test_player_lands_on_ground(self, mock_keys, pygame_init, player_controls):
        player = Player(100, SCREEN_HEIGHT - 50, BLUE, player_controls)
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        mock_keys.return_value = keys_pressed

        for _ in range(10):
            player.update(platforms, obstacles)

        assert player.rect.bottom == SCREEN_HEIGHT
        assert player.on_ground is True
        assert player.vel_y == 0

    @patch('pygame.key.get_pressed')
    def test_player_collision_with_platform(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        platform = Platform(90, 150, 100, 20)
        platforms = [platform]
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        mock_keys.return_value = keys_pressed

        for _ in range(20):
            player.update(platforms, obstacles)

        assert player.on_ground is True
        assert player.rect.bottom == platform.rect.top

    def test_player_shoot(self, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        projectiles = pygame.sprite.Group()

        player.shoot(projectiles)

        assert len(projectiles) == 1
        projectile = list(projectiles)[0]
        assert projectile.owner_type == 'player'

    def test_player_shoot_direction_right(self, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        player.facing_right = True
        projectiles = pygame.sprite.Group()

        player.shoot(projectiles)

        projectile = list(projectiles)[0]
        assert projectile.direction == 1

    def test_player_shoot_direction_left(self, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        player.facing_right = False
        projectiles = pygame.sprite.Group()

        player.shoot(projectiles)

        projectile = list(projectiles)[0]
        assert projectile.direction == -1

    def test_player_dead_cannot_shoot(self, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        player.alive = False
        projectiles = pygame.sprite.Group()

        player.shoot(projectiles)

        assert len(projectiles) == 0

    @patch('pygame.key.get_pressed')
    def test_player_dead_does_not_update(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        player.alive = False
        platforms = []
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['right']] = True
        mock_keys.return_value = keys_pressed
        initial_x = player.rect.x

        player.update(platforms, obstacles)

        assert player.rect.x == initial_x

    @patch('pygame.key.get_pressed')
    def test_player_horizontal_platform_collision(self, mock_keys, pygame_init, player_controls):
        player = Player(50, 100, BLUE, player_controls)
        platform = Platform(100, 100, 50, 50)
        platforms = [platform]
        obstacles = []

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['right']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        assert player.rect.right <= platform.rect.left

    @patch('pygame.key.get_pressed')
    def test_player_collision_with_obstacle_vertical(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 100, BLUE, player_controls)
        obstacle = Obstacle(90, 150, 60, 80)
        platforms = []
        obstacles = [obstacle]

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        mock_keys.return_value = keys_pressed

        for _ in range(20):
            player.update(platforms, obstacles)

        assert player.on_ground is True
        assert player.rect.bottom == obstacle.rect.top

    @patch('pygame.key.get_pressed')
    def test_player_collision_with_obstacle_horizontal_right(self, mock_keys, pygame_init, player_controls):
        player = Player(50, 100, BLUE, player_controls)
        obstacle = Obstacle(100, 100, 60, 80)
        platforms = []
        obstacles = [obstacle]

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['right']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        assert player.rect.right <= obstacle.rect.left

    @patch('pygame.key.get_pressed')
    def test_player_collision_with_obstacle_horizontal_left(self, mock_keys, pygame_init, player_controls):
        player = Player(200, 100, BLUE, player_controls)
        obstacle = Obstacle(100, 100, 60, 80)
        platforms = []
        obstacles = [obstacle]

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['left']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        assert player.rect.left >= obstacle.rect.right

    @patch('pygame.key.get_pressed')
    def test_player_collision_with_multiple_obstacles(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 50, BLUE, player_controls)
        obstacle1 = Obstacle(90, 100, 60, 80)
        obstacle2 = Obstacle(200, 100, 60, 80)
        platforms = []
        obstacles = [obstacle1, obstacle2]

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        mock_keys.return_value = keys_pressed

        for _ in range(20):
            player.update(platforms, obstacles)

        assert player.on_ground is True
        assert player.rect.bottom == obstacle1.rect.top

    @patch('pygame.key.get_pressed')
    def test_player_obstacle_blocks_jump_through(self, mock_keys, pygame_init, player_controls):
        player = Player(100, 150, BLUE, player_controls)
        player.on_ground = True
        obstacle = Obstacle(100, 50, 60, 80)
        platforms = []
        obstacles = [obstacle]

        from collections import defaultdict
        keys_pressed = defaultdict(bool)
        keys_pressed[player_controls['jump']] = True
        mock_keys.return_value = keys_pressed

        player.update(platforms, obstacles)

        # Player should hit bottom of obstacle when jumping
        assert player.rect.top >= obstacle.rect.bottom or player.rect.bottom <= obstacle.rect.top
