import pytest
import pygame
from exit import Exit
from config import YELLOW


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


class TestExit:
    def test_exit_creation(self, pygame_init):
        exit_sprite = Exit(100, 200)

        assert exit_sprite.rect.x == 100
        assert exit_sprite.rect.y == 200
        assert exit_sprite.rect.width == 60
        assert exit_sprite.rect.height == 60

    def test_exit_custom_size(self, pygame_init):
        exit_sprite = Exit(100, 200, width=80, height=80)

        assert exit_sprite.rect.width == 80
        assert exit_sprite.rect.height == 80

    def test_exit_position(self, pygame_init):
        x, y = 50, 100
        exit_sprite = Exit(x, y)

        assert exit_sprite.rect.topleft == (x, y)

    def test_exit_is_sprite(self, pygame_init):
        exit_sprite = Exit(0, 0)

        assert isinstance(exit_sprite, pygame.sprite.Sprite)

    def test_exit_has_image(self, pygame_init):
        exit_sprite = Exit(0, 0)

        assert exit_sprite.image is not None
        assert isinstance(exit_sprite.image, pygame.Surface)

    def test_exit_color(self, pygame_init):
        exit_sprite = Exit(0, 0)

        # Check that the exit has the yellow color
        pixel_color = exit_sprite.image.get_at((0, 0))
        expected_color = pygame.Color(*YELLOW)
        assert pixel_color == expected_color

    def test_exit_in_sprite_group(self, pygame_init):
        exits_group = pygame.sprite.Group()
        exit_sprite = Exit(100, 200)
        exits_group.add(exit_sprite)

        assert len(exits_group) == 1
        assert exit_sprite in exits_group

    def test_exit_default_size(self, pygame_init):
        exit_sprite = Exit(100, 100)

        # Default size is 60x60
        assert exit_sprite.rect.width == 60
        assert exit_sprite.rect.height == 60
