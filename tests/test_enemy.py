import pytest
import pygame
import sys
import os
import importlib.util
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load the local platforms module to avoid conflict with built-in platform module
platforms_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'platforms.py'))
spec = importlib.util.spec_from_file_location("platform_module", platforms_path)
platform_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_module)
Platform = platform_module.Platform

from enemy import Enemy
from obstacles import Obstacle
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
        obstacles = []
        initial_y = enemy.y  # Use float position for precision
        initial_vel_y = enemy.vel_y

        enemy.update(platforms, obstacles, [], 0, 0.02)

        # Gravity is applied as GRAVITY * delta_time
        expected_vel_y = initial_vel_y + (GRAVITY * 0.02)
        assert abs(enemy.vel_y - expected_vel_y) < 1
        assert enemy.y > initial_y  # Enemy should fall

    def test_enemy_movement(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.uniform', return_value=60):
                enemy = Enemy(100, 100)
                platforms = []
                obstacles = []
                initial_x = enemy.rect.x

                enemy.update(platforms, obstacles, [], 0, 0.02)

                # Movement is ENEMY_SPEED * delta_time
                expected_x = initial_x + (ENEMY_SPEED * 0.02)
                assert abs(enemy.rect.x - expected_x) < 1

    def test_enemy_screen_boundary_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(0, 100)
                platforms = []
                obstacles = []

                enemy.update(platforms, obstacles, [], 0, 0.02)

                assert enemy.rect.left >= 0
                assert enemy.vel_x == ENEMY_SPEED

    def test_enemy_screen_boundary_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(SCREEN_WIDTH - 30, 100)
                platforms = []
                obstacles = []

                enemy.update(platforms, obstacles, [], 0, 0.02)

                assert enemy.rect.right <= SCREEN_WIDTH
                assert enemy.vel_x == -ENEMY_SPEED

    def test_enemy_lands_on_ground(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.uniform', return_value=60):
                enemy = Enemy(100, 400)
                # Add a ground platform at bottom
                ground = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
                platforms = [ground]
                obstacles = []

                # Need more iterations with delta_time
                for _ in range(100):
                    enemy.update(platforms, obstacles, [], 0, 0.02)
                    if enemy.on_ground:
                        break

                assert enemy.on_ground is True
                assert enemy.vel_y == 0
                assert enemy.rect.bottom == ground.rect.top

    def test_enemy_collision_with_platform(self, pygame_init):
        with patch('random.choice', return_value=0):
            with patch('random.uniform', return_value=60):
                enemy = Enemy(100, 100)
                platform = Platform(90, 200, 100, 20)
                platforms = [platform]
                obstacles = []

                for _ in range(100):
                    enemy.update(platforms, obstacles, [], 0, 0.02)
                    if enemy.on_ground:
                        break

                assert enemy.on_ground is True
                assert enemy.rect.bottom == platform.rect.top

    def test_enemy_platform_collision_horizontal_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(95, 100)
                platform = Platform(100, 90, 50, 60)
                platforms = [platform]
                obstacles = []

                enemy.update(platforms, obstacles, [], 0, 0.02)

                assert enemy.rect.right == platform.rect.left
                assert enemy.vel_x == -ENEMY_SPEED

    def test_enemy_platform_collision_horizontal_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(101, 100)
                platform = Platform(50, 90, 50, 60)
                platforms = [platform]
                obstacles = []

                enemy.update(platforms, obstacles, [], 0, 0.02)

                assert enemy.rect.left == platform.rect.right
                assert enemy.vel_x == ENEMY_SPEED

    def test_enemy_collision_with_obstacle_vertical(self, pygame_init):
        with patch('random.choice', return_value=0):
            with patch('random.uniform', return_value=60):
                enemy = Enemy(100, 100)
                obstacle = Obstacle(90, 200, 60, 80)
                platforms = []
                obstacles = [obstacle]

                for _ in range(100):
                    enemy.update(platforms, obstacles, [], 0, 0.02)
                    if enemy.on_ground:
                        break

                assert enemy.on_ground is True
                assert enemy.rect.bottom == obstacle.rect.top

    def test_enemy_collision_with_obstacle_horizontal_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(95, 100)
                obstacle = Obstacle(100, 90, 60, 80)
                platforms = []
                obstacles = [obstacle]

                enemy.update(platforms, obstacles, [], 0, 0.02)

                # Enemy reverses direction when hitting obstacle
                assert enemy.rect.right == obstacle.rect.left
                assert enemy.vel_x == -ENEMY_SPEED

    def test_enemy_collision_with_obstacle_horizontal_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                enemy = Enemy(101, 100)
                obstacle = Obstacle(50, 90, 60, 80)
                platforms = []
                obstacles = [obstacle]

                enemy.update(platforms, obstacles, [], 0, 0.02)

                # Enemy reverses direction when hitting obstacle
                assert enemy.rect.left == obstacle.rect.right
                assert enemy.vel_x == ENEMY_SPEED

    def test_enemy_try_shoot_success(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = ENEMY_SPEED
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles, 0.02)

                    assert len(projectiles) == 1
                    projectile = list(projectiles)[0]
                    assert projectile.owner_type == 'enemy'

    def test_enemy_try_shoot_fail(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.999):
                    enemy = Enemy(100, 100)
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles, 0.02)

                    assert len(projectiles) == 0

    def test_enemy_shoot_direction_right(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = ENEMY_SPEED
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles, 0.02)

                    projectile = list(projectiles)[0]
                    assert projectile.direction == 1

    def test_enemy_shoot_direction_left(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = -ENEMY_SPEED
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles, 0.02)

                    projectile = list(projectiles)[0]
                    assert projectile.direction == -1

    def test_enemy_shoot_direction_when_stationary(self, pygame_init):
        with patch('random.choice', side_effect=[0, 1]):
            with patch('random.randint', return_value=60):
                with patch('random.random', return_value=0.001):
                    enemy = Enemy(100, 100)
                    enemy.vel_x = 0
                    projectiles = pygame.sprite.Group()

                    enemy.try_shoot(projectiles, 0.02)

                    projectile = list(projectiles)[0]
                    assert projectile.direction in [-1, 1]

    def test_enemy_detects_right_platform_edge(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            # Small platform - enemy near right edge
            platform = Platform(90, 130, 50, 20)
            platforms = [platform]
            obstacles = []

            # Position enemy on platform near right edge
            enemy.x = platform.rect.right - 35.0  # 5 pixels from edge (enemy is 30px wide)
            enemy.rect.x = int(enemy.x)
            enemy.y = platform.rect.top - 31.0  # Just above platform
            enemy.rect.y = int(enemy.y)
            enemy.vel_x = ENEMY_SPEED  # Moving right toward edge
            enemy.vel_y = 1.0  # Slight downward velocity to trigger collision
            enemy.on_ground = True  # Simulate being on ground

            initial_vel_x = enemy.vel_x
            enemy.update(platforms, obstacles, [], 0, 0.02)

            # Should have reversed direction at edge
            assert enemy.vel_x == -initial_vel_x

    def test_enemy_detects_left_platform_edge(self, pygame_init):
        with patch('random.choice', return_value=-ENEMY_SPEED):
            enemy = Enemy(100, 100)
            # Small platform
            platform = Platform(90, 130, 50, 20)
            platforms = [platform]
            obstacles = []

            # Position enemy on platform near left edge
            enemy.x = platform.rect.left + 5.0  # 5 pixels from left edge
            enemy.rect.x = int(enemy.x)
            enemy.y = platform.rect.top - 31.0  # Just above platform
            enemy.rect.y = int(enemy.y)
            enemy.vel_x = -ENEMY_SPEED  # Moving left toward edge
            enemy.vel_y = 1.0  # Slight downward velocity to trigger collision
            enemy.on_ground = True  # Simulate being on ground

            initial_vel_x = enemy.vel_x
            enemy.update(platforms, obstacles, [], 0, 0.02)

            # Should have reversed direction at edge
            assert enemy.vel_x == -initial_vel_x

    def test_enemy_no_edge_detection_when_ground_continues(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            # Large platform - plenty of ground ahead
            platform = Platform(90, 130, 500, 20)
            platforms = [platform]
            obstacles = []

            # Position enemy in middle of platform
            enemy.x = float(platform.rect.centerx)
            enemy.rect.x = int(enemy.x)
            enemy.y = platform.rect.top - 31.0  # Just above platform
            enemy.rect.y = int(enemy.y)
            enemy.vel_x = ENEMY_SPEED
            enemy.vel_y = 1.0  # Slight downward velocity to trigger collision
            enemy.on_ground = True  # Simulate being on ground

            initial_vel_x = enemy.vel_x
            enemy.update(platforms, obstacles, [], 0, 0.02)

            # Should NOT have reversed - plenty of ground ahead
            assert enemy.vel_x == initial_vel_x

    def test_enemy_no_edge_detection_when_in_air(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            # Enemy is falling (in air)
            assert enemy.on_ground is False
            assert enemy.vel_x == ENEMY_SPEED

            # Update while falling
            initial_vel = enemy.vel_x
            enemy.update(platforms, obstacles, [], 0, 0.02)

            # Should NOT reverse direction while in air
            assert enemy.vel_x == initial_vel

    def test_enemy_no_edge_detection_when_stationary(self, pygame_init):
        with patch('random.choice', return_value=0):
            enemy = Enemy(100, 100)
            # Small platform
            platform = Platform(90, 130, 50, 20)
            platforms = [platform]
            obstacles = []

            # Land enemy on platform
            for _ in range(100):
                enemy.update(platforms, obstacles, [], 0, 0.02)
                if enemy.on_ground:
                    break

            # Make enemy stationary
            enemy.vel_x = 0

            # Edge detection should return False for stationary enemy
            edge_detected = enemy._check_platform_edge(platforms, 0.02)
            assert edge_detected is False

    def test_enemy_patrols_on_platform_without_falling(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            # Small platform for testing patrol (100px wide, enemy is 30px)
            platform = Platform(200, 300, 100, 20)
            platforms = [platform]
            obstacles = []

            # Position enemy on platform
            enemy.x = float(platform.rect.centerx)
            enemy.rect.x = int(enemy.x)
            enemy.y = platform.rect.top - 31.0  # Just above
            enemy.rect.y = int(enemy.y)
            enemy.vel_y = 1.0
            enemy.vel_x = ENEMY_SPEED
            enemy.on_ground = True

            # Simulate patrol for several seconds
            direction_changes = 0
            last_vel = enemy.vel_x
            max_y = enemy.rect.bottom  # Track maximum fall

            for _ in range(500):  # 10 seconds at 0.02 delta_time
                enemy.update(platforms, obstacles, [], 0, 0.02)

                # Track direction changes
                if enemy.vel_x != last_vel and last_vel != 0:
                    direction_changes += 1
                last_vel = enemy.vel_x

                # Enemy should never fall significantly below platform
                # Allow some tolerance for collision resolution
                max_y = max(max_y, enemy.rect.bottom)
                assert enemy.rect.bottom <= platform.rect.top + 50, f"Enemy fell too far: bottom={enemy.rect.bottom}, platform top={platform.rect.top}"

                # Enemy center should stay within platform horizontal bounds (with small margin)
                assert enemy.rect.centerx >= platform.rect.left - 5, f"Enemy fell off left: {enemy.rect.centerx} < {platform.rect.left}"
                assert enemy.rect.centerx <= platform.rect.right + 5, f"Enemy fell off right: {enemy.rect.centerx} > {platform.rect.right}"

            # Should have changed direction at least once (patrol behavior)
            assert direction_changes >= 2, f"Expected at least 2 direction changes, got {direction_changes}"

    def test_enemy_edge_detection_with_multiple_platforms(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            # Multiple platforms at different positions
            platform1 = Platform(90, 130, 50, 20)  # Enemy lands here
            platform2 = Platform(200, 130, 50, 20)  # Different platform (no edge)
            platforms = [platform1, platform2]
            obstacles = []

            # Land enemy on platform1
            for _ in range(100):
                enemy.update(platforms, obstacles, [], 0, 0.02)
                if enemy.on_ground:
                    break

            # Position enemy near right edge of platform1
            # Platform2 is far away, so edge should be detected
            enemy.x = platform1.rect.right - 35.0
            enemy.rect.x = int(enemy.x)
            enemy.vel_x = ENEMY_SPEED

            initial_vel = enemy.vel_x
            enemy.update(platforms, obstacles, [], 0, 0.02)

            # Should have reversed at platform1's edge
            # (platform2 is too far to prevent edge detection)
            assert enemy.vel_x == -initial_vel

    # ========== Alert Mode Tests ==========

    def test_enemy_initial_alert_state(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)

            assert enemy.alert_state == "PATROL"
            assert enemy.alert_timer == 0.0
            assert enemy.shoot_timer == 0.0
            assert enemy.burst_shot_count == 0

    def test_enemy_enter_alert_state(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)

            # Create mock player
            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)

            player = MockPlayer()

            # Enter alert state
            enemy._enter_alert_state(player)

            assert enemy.alert_state == "ALERT"
            assert enemy.alert_timer == 0.0
            assert enemy.burst_shot_count == 0
            assert enemy.last_seen_player_x == player.rect.centerx
            # Should face player
            assert enemy.facing_direction == 1  # Player is to the right

    def test_enemy_enter_alert_state_player_on_left(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(200, 100)

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(50, 100, 30, 30)  # Left of enemy

            player = MockPlayer()
            enemy._enter_alert_state(player)

            assert enemy.facing_direction == -1  # Player is to the left

    def test_enemy_stops_moving_when_alerted(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)
                    self.alive = True

            player = MockPlayer()

            # Enter alert state
            enemy._enter_alert_state(player)
            assert enemy.alert_state == "ALERT"

            # Update enemy
            initial_x = enemy.x
            enemy.update(platforms, obstacles, [player], 0, 0.02)

            # Should be stationary (vel_x = 0)
            assert enemy.vel_x == 0
            # Position should not change horizontally (only gravity affects Y)

    def test_enemy_alert_timer_expires(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)
                    self.alive = True

            player = MockPlayer()

            # Enter alert and simulate time passing
            enemy._enter_alert_state(player)
            assert enemy.alert_state == "ALERT"

            # Simulate 7+ seconds passing (alert duration)
            for _ in range(400):  # 400 * 0.02 = 8 seconds
                enemy._update_alert_state([player], platforms, obstacles, 0, 0.02)

            # Should have exited to COOLDOWN
            assert enemy.alert_state == "COOLDOWN"

    def test_enemy_alert_state_transitions_to_patrol(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            # Manually set to cooldown
            enemy.alert_state = "COOLDOWN"
            enemy.alert_cooldown = 0.0

            # Simulate 2+ seconds
            for _ in range(110):  # 110 * 0.02 = 2.2 seconds
                enemy._update_alert_state([], platforms, obstacles, 0, 0.02)

            # Should be back to PATROL
            assert enemy.alert_state == "PATROL"

    def test_enemy_exit_alert_state_resumes_movement(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)

            # Set facing direction
            enemy.facing_direction = 1

            # Exit alert state
            enemy._exit_alert_state()

            # Should resume patrol
            assert enemy.alert_state == "COOLDOWN"
            assert enemy.vel_x == ENEMY_SPEED  # Moving in facing direction

    # ========== Raycasting Tests ==========

    def test_enemy_raycast_detects_player_same_height(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(300, 100, 30, 30)  # Same height, to the right

            player = MockPlayer()

            # Should detect player
            can_see = enemy._raycast_to_player(player, platforms, obstacles)
            assert can_see is True

    def test_enemy_raycast_blocked_by_platform(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)

            # Platform blocking the raycast
            blocking_platform = Platform(150, 90, 50, 60)
            platforms = [blocking_platform]
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(300, 100, 30, 30)

            player = MockPlayer()

            # Should NOT detect player (blocked)
            can_see = enemy._raycast_to_player(player, platforms, obstacles)
            assert can_see is False

    def test_enemy_raycast_blocked_by_obstacle(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []

            # Obstacle blocking the raycast
            from obstacles import Obstacle
            blocking_obstacle = Obstacle(150, 90, 50, 60)
            obstacles = [blocking_obstacle]

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(300, 100, 30, 30)

            player = MockPlayer()

            # Should NOT detect player (blocked)
            can_see = enemy._raycast_to_player(player, platforms, obstacles)
            assert can_see is False

    def test_enemy_raycast_fails_when_player_too_high(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    # Player 300 pixels above enemy (beyond tolerance)
                    self.rect = pygame.Rect(150, -200, 30, 30)

            player = MockPlayer()

            # Should NOT detect (vertical distance too large)
            can_see = enemy._raycast_to_player(player, platforms, obstacles)
            assert can_see is False

    def test_enemy_raycast_fails_when_player_too_low(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    # Player 300 pixels below enemy (beyond tolerance)
                    self.rect = pygame.Rect(150, 400, 30, 30)

            player = MockPlayer()

            # Should NOT detect (vertical distance too large)
            can_see = enemy._raycast_to_player(player, platforms, obstacles)
            assert can_see is False

    def test_enemy_check_player_detection_when_on_ground(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            enemy.on_ground = True
            enemy.raycast_timer = 1.0  # Force raycast this update
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)
                    self.alive = True

            player = MockPlayer()

            # Should detect player
            detected = enemy._check_player_detection([player], platforms, obstacles, 0.02)
            assert detected == player

    def test_enemy_check_player_detection_skips_when_in_air(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            enemy.on_ground = False  # In air
            enemy.raycast_timer = 1.0
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)
                    self.alive = True

            player = MockPlayer()

            # Should NOT detect (not on ground)
            detected = enemy._check_player_detection([player], platforms, obstacles, 0.02)
            assert detected is None

    def test_enemy_check_player_detection_skips_dead_players(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            enemy.on_ground = True
            enemy.raycast_timer = 1.0
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)
                    self.alive = False  # Dead

            player = MockPlayer()

            # Should NOT detect dead player
            detected = enemy._check_player_detection([player], platforms, obstacles, 0.02)
            assert detected is None

    def test_enemy_raycast_throttled_by_timer(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            enemy.on_ground = True
            enemy.raycast_timer = 0.0  # Just raycasted
            platforms = []
            obstacles = []

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)
                    self.alive = True

            player = MockPlayer()

            # Should NOT raycast yet (timer not expired)
            detected = enemy._check_player_detection([player], platforms, obstacles, 0.01)
            assert detected is None

            # After enough time, should raycast
            detected = enemy._check_player_detection([player], platforms, obstacles, 0.2)
            assert detected == player

    # ========== Burst Fire Tests ==========

    def test_enemy_burst_fire_first_shot_immediate(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            projectiles = pygame.sprite.Group()

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)

            player = MockPlayer()

            # Enter alert state
            enemy._enter_alert_state(player)

            # First shot should fire immediately (shoot_timer set to interval)
            initial_count = len(projectiles)
            enemy.try_shoot(projectiles, 0.01)  # Small delta

            assert len(projectiles) == initial_count + 1

    def test_enemy_burst_fire_three_shots(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            projectiles = pygame.sprite.Group()

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)

            player = MockPlayer()

            enemy._enter_alert_state(player)

            shot_times = []
            time = 0.0
            delta_time = 0.1

            # Simulate 3 seconds
            while time < 3.0:
                before = len(projectiles)
                enemy.try_shoot(projectiles, delta_time)
                after = len(projectiles)

                if after > before:
                    shot_times.append(time)

                time += delta_time

            # Should have fired 3 shots in burst
            assert len(shot_times) == 3

            # Verify timing (0.5 second intervals)
            assert 0.0 <= shot_times[0] <= 0.2  # First shot immediate
            assert 0.4 <= shot_times[1] <= 0.7  # Second shot ~0.5s later
            assert 0.9 <= shot_times[2] <= 1.2  # Third shot ~1.0s total

    def test_enemy_burst_fire_cooldown_between_bursts(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            projectiles = pygame.sprite.Group()

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)

            player = MockPlayer()

            enemy._enter_alert_state(player)

            shot_times = []
            time = 0.0
            delta_time = 0.1

            # Simulate 10 seconds to see multiple bursts
            while time < 10.0:
                before = len(projectiles)
                enemy.try_shoot(projectiles, delta_time)
                after = len(projectiles)

                if after > before:
                    shot_times.append(time)

                time += delta_time

            # Should have multiple bursts
            assert len(shot_times) >= 6  # At least 2 full bursts

            # Verify cooldown between burst 1 and burst 2
            # Burst 1: shots at ~0.0, ~0.5, ~1.0
            # Cooldown: 3.0 seconds
            # Burst 2: shots at ~4.5, ~5.0, ~5.5
            cooldown_period = shot_times[3] - shot_times[2]
            assert 3.0 <= cooldown_period <= 3.3  # 3 second cooldown with tolerance

    def test_enemy_burst_fire_counter_resets(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            projectiles = pygame.sprite.Group()

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(200, 100, 30, 30)

            player = MockPlayer()

            enemy._enter_alert_state(player)

            # Fire first burst
            for _ in range(100):  # Plenty of time
                enemy.try_shoot(projectiles, 0.05)

            # Should have 3+ shots (burst + possibly next burst)
            assert len(projectiles) >= 3

            # Verify burst_shot_count cycles properly
            # After cooldown completes, should reset to 0 and start new burst
            time = 0.0
            shot_count_when_shooting = []

            for _ in range(200):
                before = len(projectiles)
                enemy.try_shoot(projectiles, 0.05)
                after = len(projectiles)

                if after > before:
                    shot_count_when_shooting.append(enemy.burst_shot_count)

                time += 0.05

            # Should see counts of 1, 2, 3, 1, 2, 3, ... (cycling)
            # Verify pattern exists
            assert 1 in shot_count_when_shooting
            assert 2 in shot_count_when_shooting
            assert 3 in shot_count_when_shooting

    def test_enemy_no_burst_fire_in_patrol_mode(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            with patch('random.random', return_value=0.999):  # Don't shoot randomly
                enemy = Enemy(100, 100)
                projectiles = pygame.sprite.Group()

                # Enemy in PATROL mode (not alerted)
                assert enemy.alert_state == "PATROL"

                # Try to shoot many times
                for _ in range(100):
                    enemy.try_shoot(projectiles, 0.1)

                # Should not have fired (random chance is too low)
                assert len(projectiles) == 0

    def test_enemy_burst_fire_uses_facing_direction(self, pygame_init):
        with patch('random.choice', return_value=ENEMY_SPEED):
            enemy = Enemy(100, 100)
            projectiles = pygame.sprite.Group()

            class MockPlayer:
                def __init__(self):
                    self.rect = pygame.Rect(50, 100, 30, 30)  # Left of enemy

            player = MockPlayer()

            # Enter alert (player on left)
            enemy._enter_alert_state(player)
            assert enemy.facing_direction == -1

            # Fire shot
            enemy.try_shoot(projectiles, 0.01)

            # Projectile should go left
            projectile = list(projectiles)[0]
            assert projectile.direction == -1
