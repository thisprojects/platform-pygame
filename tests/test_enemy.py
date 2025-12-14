import pytest
import pygame
import sys
import os
import importlib.util
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load the local platform module to avoid conflict with built-in platform module
platform_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'platform.py'))
spec = importlib.util.spec_from_file_location("platform_module", platform_path)
platform_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_module)
Platform = platform_module.Platform

from enemy import Enemy
from config import ENEMY_SPEED, GRAVITY, SCREEN_WIDTH, SCREEN_HEIGHT


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def enemy(pygame_init):
    with patch('random.choice', return_value=ENEMY_SPEED):
        with patch('random.randint', return_value=60):
            return Enemy(100, 100)


class TestEnemy:
    def test_enemy_creation(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(100, 200)

                assert enemy.rect.x == 100
                assert enemy.rect.y == 200
                assert enemy.vel_x in [-ENEMY_SPEED, ENEMY_SPEED]
                assert enemy.vel_y == 0
                assert enemy.on_ground is False

    def test_enemy_is_sprite(self, enemy):
        assert isinstance(enemy, pygame.sprite.Sprite)

    def test_enemy_gravity_applied(self, enemy):
        platforms = []
        initial_y = enemy.rect.y
        initial_vel_y = enemy.vel_y

        enemy.update(platforms)

        assert enemy.vel_y == initial_vel_y + GRAVITY
        assert enemy.rect.y > initial_y

    def test_enemy_movement(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(100, 100)
                platforms = []
                initial_x = enemy.rect.x

                enemy.update(platforms)

                assert enemy.rect.x == initial_x + ENEMY_SPEED

    def test_enemy_screen_boundary_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(0, 100)
                platforms = []

                enemy.update(platforms)

                assert enemy.rect.left >= 0
                assert enemy.vel_x == ENEMY_SPEED

    def test_enemy_screen_boundary_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(SCREEN_WIDTH - 30, 100)
                platforms = []

                enemy.update(platforms)

                assert enemy.rect.right <= SCREEN_WIDTH
                assert enemy.vel_x == -ENEMY_SPEED

    def test_enemy_lands_on_ground(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(100, SCREEN_HEIGHT - 50)
                platforms = []

                for _ in range(20):
                    enemy.update(platforms)

                assert enemy.rect.bottom == SCREEN_HEIGHT
                assert enemy.on_ground is True
                assert enemy.vel_y == 0

    def test_enemy_collision_with_platform(self, pygame_init):
        with patch('random.choice', return_value=0):
            with patch('random.randint', return_value=60):
                enemy = Enemy(100, 100)
                platform = Platform(90, 150, 100, 20)
                platforms = [platform]

                for _ in range(20):
                    enemy.update(platforms)

                assert enemy.on_ground is True
                assert enemy.rect.bottom == platform.rect.top

    def test_enemy_platform_collision_horizontal_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(95, 100)
                platform = Platform(100, 90, 50, 60)
                platforms = [platform]

                enemy.update(platforms)

                assert enemy.rect.right == platform.rect.left
                assert enemy.vel_x == -ENEMY_SPEED

    def test_enemy_platform_collision_horizontal_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(101, 100)
                platform = Platform(50, 90, 50, 60)
                platforms = [platform]

                enemy.update(platforms)

                assert enemy.rect.left == platform.rect.right
                assert enemy.vel_x == ENEMY_SPEED

    def test_enemy_direction_change_timer(self, pygame_init):
        with patch('random.choice', side_effect=[ENEMY_SPEED, -ENEMY_SPEED]):
            with patch('random.randint', return_value=1):
                enemy = Enemy(100, 100)
                platforms = []

                initial_vel_x = enemy.vel_x
                enemy.direction_timer = enemy.direction_change_interval - 1

                enemy.update(platforms)

                assert enemy.direction_timer == 0
                assert enemy.vel_x != initial_vel_x

    def test_enemy_try_shoot_success(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = ENEMY_SPEED
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles)

                    assert len(projectiles) == 1
                    projectile = list(projectiles)[0]
                    assert projectile.owner_type == 'enemy'

    def test_enemy_try_shoot_fail(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.999):
                    enemy = Enemy(100, 100)
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles)

                    assert len(projectiles) == 0

    def test_enemy_shoot_direction_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = ENEMY_SPEED
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles)

                    projectile = list(projectiles)[0]
                    assert projectile.direction == 1

    def test_enemy_shoot_direction_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = -ENEMY_SPEED
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles)

                    projectile = list(projectiles)[0]
                    assert projectile.direction == -1

    def test_enemy_shoot_direction_when_stationary(self, pygame_init):
        with patch('random.choice', side_effect=[0, 1]):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = 0
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles)

                    projectile = list(projectiles)[0]
                    assert projectile.direction in [-1, 1]
