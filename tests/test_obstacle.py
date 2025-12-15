import pytest
import pygame
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from obstacles import Obstacle
from config import PURPLE


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def obstacle(pygame_init):
    return Obstacle(100, 200, 60, 80)


class TestObstacle:
    def test_obstacle_creation(self, obstacle):
        assert obstacle.rect.x == 100
        assert obstacle.rect.y == 200
        assert obstacle.rect.width == 60
        assert obstacle.rect.height == 80

    def test_obstacle_is_sprite(self, obstacle):
        assert isinstance(obstacle, pygame.sprite.Sprite)

    def test_obstacle_has_surface(self, obstacle):
        assert isinstance(obstacle.image, pygame.Surface)

    def test_obstacle_color(self, obstacle):
        # Check that the obstacle has the correct color
        pixel_color = obstacle.image.get_at((0, 0))
        expected_color = pygame.Color(*PURPLE)
        assert pixel_color == expected_color

    def test_obstacle_position(self, pygame_init):
        obstacle = Obstacle(50, 100, 60, 80)
        assert obstacle.rect.x == 50
        assert obstacle.rect.y == 100

    def test_obstacle_custom_size(self, pygame_init):
        obstacle = Obstacle(0, 0, 100, 150)
        assert obstacle.rect.width == 100
        assert obstacle.rect.height == 150

    def test_obstacle_rect_positioning(self, pygame_init):
        obstacle = Obstacle(100, 200, 60, 80)
        assert obstacle.rect.topleft == (100, 200)
        assert obstacle.rect.bottomright == (160, 280)

    def test_multiple_obstacles(self, pygame_init):
        obstacles = [
            Obstacle(100, 200, 60, 80),
            Obstacle(300, 400, 60, 80),
            Obstacle(500, 100, 60, 80),
        ]
        assert len(obstacles) == 3
        assert obstacles[0].rect.x == 100
        assert obstacles[1].rect.x == 300
        assert obstacles[2].rect.x == 500

    def test_obstacle_in_sprite_group(self, pygame_init):
        obstacles_group = pygame.sprite.Group()
        obstacle = Obstacle(100, 200, 60, 80)
        obstacles_group.add(obstacle)

        assert len(obstacles_group) == 1
        assert obstacle in obstacles_group
