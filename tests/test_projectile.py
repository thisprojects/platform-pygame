import pytest
import pygame
from projectile import Projectile
from config import PROJECTILE_SPEED, SCREEN_WIDTH, YELLOW, PURPLE


@pytest.fixture
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


class TestProjectile:
    def test_projectile_creation_player(self, pygame_init):
        projectile = Projectile(100, 200, 1, YELLOW, 'player')

        assert projectile.rect.centerx == 100
        assert projectile.rect.centery == 200
        assert projectile.direction == 1
        assert projectile.owner_type == 'player'

    def test_projectile_creation_enemy(self, pygame_init):
        projectile = Projectile(300, 150, -1, PURPLE, 'enemy')

        assert projectile.rect.centerx == 300
        assert projectile.rect.centery == 150
        assert projectile.direction == -1
        assert projectile.owner_type == 'enemy'

    def test_projectile_move_right(self, pygame_init):
        projectile = Projectile(100, 100, 1, YELLOW, 'player')
        initial_x = projectile.rect.x

        projectile.update(0.02)  # 20ms delta_time

        expected_distance = PROJECTILE_SPEED * 0.02
        assert abs(projectile.rect.x - (initial_x + expected_distance)) < 5  # Allow small delta_time rounding error

    def test_projectile_move_left(self, pygame_init):
        projectile = Projectile(100, 100, -1, PURPLE, 'enemy')
        initial_x = projectile.rect.x

        projectile.update(0.02)

        expected_distance = PROJECTILE_SPEED * 0.02
        assert abs(projectile.rect.x - (initial_x - expected_distance)) < 5  # Allow small delta_time rounding error

    def test_projectile_moves_multiple_updates(self, pygame_init):
        projectile = Projectile(100, 100, 1, YELLOW, 'player')
        initial_x = projectile.rect.x

        for _ in range(5):
            projectile.update(0.02)

        expected_distance = PROJECTILE_SPEED * 0.02 * 5
        assert abs(projectile.rect.x - (initial_x + expected_distance)) < 5  # Allow small delta_time rounding error

    def test_projectile_removed_when_off_screen_right(self, pygame_init):
        group = pygame.sprite.Group()
        projectile = Projectile(SCREEN_WIDTH + 10, 100, 1, YELLOW, 'player')
        group.add(projectile)

        projectile.update(0.02)

        assert len(group) == 0

    def test_projectile_removed_when_off_screen_left(self, pygame_init):
        group = pygame.sprite.Group()
        projectile = Projectile(-20, 100, -1, PURPLE, 'enemy')
        group.add(projectile)

        projectile.update(0.02)

        assert len(group) == 0

    def test_projectile_stays_on_screen(self, pygame_init):
        group = pygame.sprite.Group()
        projectile = Projectile(400, 100, 1, YELLOW, 'player')
        group.add(projectile)

        projectile.update(0.02)

        assert len(group) == 1
        assert projectile.alive()

    def test_projectile_is_sprite(self, pygame_init):
        projectile = Projectile(100, 100, 1, YELLOW, 'player')

        assert isinstance(projectile, pygame.sprite.Sprite)

    def test_projectile_has_image(self, pygame_init):
        projectile = Projectile(100, 100, 1, YELLOW, 'player')

        assert projectile.image is not None
        assert isinstance(projectile.image, pygame.Surface)
