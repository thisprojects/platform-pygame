import pytest
import pygame
import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load the local platforms module to avoid conflict with built-in platform module
platforms_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'platforms.py'))
spec = importlib.util.spec_from_file_location("platform_module", platforms_path)
platform_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_module)
Platform = platform_module.Platform

from machinegunner import Machinegunner
from obstacles import Obstacle
from config import GRAVITY, SCREEN_HEIGHT, BLUE, ORANGE


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def machinegunner(pygame_init):
    return Machinegunner(100, 100)


class MockPlayer:
    """Mock player for testing facing direction."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.alive = True


class TestMachinegunner:
    def test_machinegunner_creation(self, pygame_init):
        mg = Machinegunner(100, 200)

        assert mg.rect.x == 100
        assert mg.rect.y == 200
        assert mg.vel_x == 0  # Should be stationary
        assert mg.vel_y == 0
        assert mg.on_ground is False

    def test_machinegunner_is_sprite(self, machinegunner):
        assert isinstance(machinegunner, pygame.sprite.Sprite)

    def test_machinegunner_is_blue(self, machinegunner):
        # Check the color of the sprite
        color = machinegunner.image.get_at((0, 0))
        assert color[:3] == BLUE

    def test_machinegunner_is_stationary(self, machinegunner):
        # Machinegunner should always have vel_x = 0
        assert machinegunner.vel_x == 0

    def test_machinegunner_gravity_applied(self, machinegunner):
        platforms = []
        obstacles = []
        initial_y = machinegunner.y
        initial_vel_y = machinegunner.vel_y

        machinegunner.update(platforms, obstacles, [], 0, 0.02)

        # Gravity is applied as GRAVITY * delta_time
        expected_vel_y = initial_vel_y + (GRAVITY * 0.02)
        assert abs(machinegunner.vel_y - expected_vel_y) < 1
        assert machinegunner.y > initial_y  # Should fall

    def test_machinegunner_lands_on_ground(self, pygame_init):
        mg = Machinegunner(100, 400)
        # Add a ground platform at bottom
        ground = Platform(0, SCREEN_HEIGHT - 20, 1280, 20)
        platforms = [ground]
        obstacles = []

        # Need iterations with delta_time for falling
        for _ in range(100):
            mg.update(platforms, obstacles, [], 0, 0.02)
            if mg.on_ground:
                break

        assert mg.on_ground is True
        assert mg.vel_y == 0
        assert mg.rect.bottom == ground.rect.top

    def test_machinegunner_collision_with_platform(self, pygame_init):
        mg = Machinegunner(100, 100)
        platform = Platform(90, 200, 100, 20)
        platforms = [platform]
        obstacles = []

        for _ in range(100):
            mg.update(platforms, obstacles, [], 0, 0.02)
            if mg.on_ground:
                break

        assert mg.on_ground is True
        assert mg.rect.bottom == platform.rect.top

    def test_machinegunner_faces_player_on_right(self, machinegunner):
        # Player to the right
        player = MockPlayer(600, 100)
        players = [player]

        machinegunner._update_facing_direction(players)
        assert machinegunner.facing_direction == 1  # Facing right

    def test_machinegunner_faces_player_on_left(self, machinegunner):
        # Player to the left (machinegunner at 100)
        player = MockPlayer(50, 100)
        players = [player]

        machinegunner._update_facing_direction(players)
        assert machinegunner.facing_direction == -1  # Facing left

    def test_machinegunner_tracks_player_movement(self, machinegunner):
        player = MockPlayer(600, 100)
        players = [player]

        # Initially facing right
        machinegunner._update_facing_direction(players)
        assert machinegunner.facing_direction == 1

        # Player moves to left
        player.rect.centerx = 50
        machinegunner._update_facing_direction(players)
        assert machinegunner.facing_direction == -1

    def test_machinegunner_ignores_dead_players(self, machinegunner):
        dead_player = MockPlayer(600, 100)
        dead_player.alive = False
        players = [dead_player]

        initial_direction = machinegunner.facing_direction
        machinegunner._update_facing_direction(players)
        # Should not change direction if all players are dead
        assert machinegunner.facing_direction == initial_direction

    def test_machinegunner_burst_fire_configuration(self, machinegunner):
        assert machinegunner.shots_per_burst == 6
        assert machinegunner.shot_interval == 0.25
        assert machinegunner.burst_cooldown == 3.0

    def test_machinegunner_initial_state(self, machinegunner):
        assert machinegunner.burst_shot_count == 0
        assert machinegunner.shoot_timer == 0.0
        assert machinegunner.in_cooldown is False

    def test_machinegunner_fires_first_shot(self, machinegunner):
        projectiles = pygame.sprite.Group()

        machinegunner.try_shoot(projectiles, 0.25)

        assert len(projectiles) == 1
        assert machinegunner.burst_shot_count == 1

    def test_machinegunner_fires_full_burst(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # Fire 6 shots
        for i in range(6):
            machinegunner.try_shoot(projectiles, 0.25)

        assert len(projectiles) == 6
        assert machinegunner.burst_shot_count == 6
        assert machinegunner.in_cooldown is True

    def test_machinegunner_enters_cooldown_after_burst(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # Fire full burst
        for _ in range(6):
            machinegunner.try_shoot(projectiles, 0.25)

        assert machinegunner.in_cooldown is True

    def test_machinegunner_does_not_shoot_during_cooldown(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # Fire full burst
        for _ in range(6):
            machinegunner.try_shoot(projectiles, 0.25)

        # Try to shoot during cooldown
        machinegunner.try_shoot(projectiles, 0.25)
        assert len(projectiles) == 6  # Still 6, no new shot

    def test_machinegunner_exits_cooldown_after_duration(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # Fire full burst
        for _ in range(6):
            machinegunner.try_shoot(projectiles, 0.25)

        # Wait for cooldown (3 seconds)
        for _ in range(12):  # 12 * 0.25 = 3 seconds
            machinegunner.try_shoot(projectiles, 0.25)

        assert machinegunner.in_cooldown is False
        assert machinegunner.burst_shot_count == 0

    def test_machinegunner_fires_new_burst_after_cooldown(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # First burst
        for _ in range(6):
            machinegunner.try_shoot(projectiles, 0.25)

        # Wait for cooldown
        for _ in range(12):
            machinegunner.try_shoot(projectiles, 0.25)

        # Fire first shot of new burst
        machinegunner.try_shoot(projectiles, 0.25)
        assert len(projectiles) == 7

    def test_machinegunner_projectile_properties(self, machinegunner):
        projectiles = pygame.sprite.Group()
        machinegunner.facing_direction = 1

        machinegunner.try_shoot(projectiles, 0.25)

        projectile = list(projectiles)[0]
        assert projectile.direction == 1
        assert projectile.owner_type == "enemy"
        # Check orange color
        color = projectile.image.get_at((0, 0))
        assert color[:3] == ORANGE

    def test_machinegunner_projectile_direction_changes_with_facing(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # Face left
        machinegunner.facing_direction = -1
        machinegunner.try_shoot(projectiles, 0.25)

        projectile = list(projectiles)[0]
        assert projectile.direction == -1

    def test_machinegunner_respects_shot_interval(self, machinegunner):
        projectiles = pygame.sprite.Group()

        # First shot
        machinegunner.try_shoot(projectiles, 0.25)
        assert len(projectiles) == 1

        # Try immediately without waiting (delta_time too small)
        machinegunner.try_shoot(projectiles, 0.1)
        assert len(projectiles) == 1  # No new shot

        # Wait for interval
        machinegunner.try_shoot(projectiles, 0.15)  # Total 0.25
        assert len(projectiles) == 2

    def test_machinegunner_updates_facing_during_update(self, pygame_init):
        mg = Machinegunner(100, 100)
        player = MockPlayer(600, 100)
        players = [player]
        platforms = []
        obstacles = []

        initial_direction = mg.facing_direction
        mg.update(platforms, obstacles, players, 0, 0.02)

        # Should face towards player
        if player.rect.centerx > mg.rect.centerx:
            assert mg.facing_direction == 1
        else:
            assert mg.facing_direction == -1
