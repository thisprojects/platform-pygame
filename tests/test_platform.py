import pytest
import pygame
from platforms import Platform


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


class TestPlatform:
    def test_platform_creation(self, pygame_init):
        platform = Platform(100, 200, 150, 20)

        assert platform.rect.x == 100
        assert platform.rect.y == 200
        assert platform.rect.width == 150
        assert platform.rect.height == 20

    def test_platform_position(self, pygame_init):
        x, y, width, height = 50, 100, 200, 30
        platform = Platform(x, y, width, height)

        assert platform.rect.topleft == (x, y)
        assert platform.rect.bottomright == (x + width, y + height)

    def test_platform_is_sprite(self, pygame_init):
        platform = Platform(0, 0, 100, 10)

        assert isinstance(platform, pygame.sprite.Sprite)

    def test_platform_has_image(self, pygame_init):
        platform = Platform(0, 0, 100, 10)

        assert platform.image is not None
        assert isinstance(platform.image, pygame.Surface)

    def test_multiple_platforms(self, pygame_init):
        platforms = [
            Platform(0, 500, 800, 20),
            Platform(100, 400, 200, 15),
            Platform(500, 300, 150, 15)
        ]

        assert len(platforms) == 3
        assert platforms[0].rect.y == 500
        assert platforms[1].rect.y == 400
        assert platforms[2].rect.y == 300
