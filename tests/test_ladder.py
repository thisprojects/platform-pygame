import pytest
import pygame
from ladder import Ladder


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


class TestLadder:
    def test_ladder_creation(self, pygame_init):
        ladder = Ladder(100, 200, 40, 160)

        assert ladder.rect.x == 100
        assert ladder.rect.y == 200
        assert ladder.rect.width == 40
        assert ladder.rect.height == 160

    def test_ladder_position(self, pygame_init):
        x, y, width, height = 50, 100, 40, 200
        ladder = Ladder(x, y, width, height)

        assert ladder.rect.topleft == (x, y)
        assert ladder.rect.bottomright == (x + width, y + height)

    def test_ladder_is_sprite(self, pygame_init):
        ladder = Ladder(0, 0, 40, 100)

        assert isinstance(ladder, pygame.sprite.Sprite)

    def test_ladder_has_image(self, pygame_init):
        ladder = Ladder(0, 0, 40, 100)

        assert ladder.image is not None
        assert isinstance(ladder.image, pygame.Surface)

    def test_ladder_vertical(self, pygame_init):
        # Ladders are typically tall and narrow
        ladder = Ladder(100, 100, 40, 200)

        assert ladder.rect.height > ladder.rect.width

    def test_ladder_different_sizes(self, pygame_init):
        short_ladder = Ladder(0, 0, 40, 80)
        tall_ladder = Ladder(0, 0, 40, 400)

        assert tall_ladder.rect.height > short_ladder.rect.height
        assert tall_ladder.rect.width == short_ladder.rect.width

    def test_ladder_in_sprite_group(self, pygame_init):
        ladders_group = pygame.sprite.Group()
        ladder = Ladder(100, 200, 40, 160)
        ladders_group.add(ladder)

        assert len(ladders_group) == 1
        assert ladder in ladders_group

    def test_multiple_ladders(self, pygame_init):
        ladders = [
            Ladder(100, 100, 40, 200),
            Ladder(300, 150, 40, 250),
            Ladder(500, 200, 40, 300)
        ]

        assert len(ladders) == 3
        assert ladders[0].rect.x == 100
        assert ladders[1].rect.x == 300
        assert ladders[2].rect.x == 500
