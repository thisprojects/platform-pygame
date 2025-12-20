import pytest
import pygame
from map_loader import MapLoader
from platforms import Platform
from enemy import Enemy
from obstacles import Obstacle
from ladder import Ladder


@pytest.fixture
def pygame_init():
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


@pytest.fixture
def map_loader(pygame_init):
    return MapLoader(tile_size=40)


class TestMapLoader:
    def test_map_loader_creation(self, map_loader):
        assert map_loader.tile_size == 40

    def test_load_empty_map(self, map_loader):
        empty_map = [
            "    ",
            "    ",
            "    ",
        ]

        result = map_loader.load_map(empty_map)

        assert result['platforms'] == []
        assert result['enemies'] == []
        assert result['obstacles'] == []
        assert result['ladders'] == []
        assert result['spawn_points'] == []
        assert result['exit_pos'] is None

    def test_load_simple_platform(self, map_loader):
        simple_map = [
            "----",
        ]

        result = map_loader.load_map(simple_map)

        # Should have 1 merged platform (4 tiles merged horizontally)
        assert len(result['platforms']) == 1
        platform = result['platforms'][0]
        assert platform == (0, 0, 160, 40)  # 4 tiles * 40px = 160px wide

    def test_load_enemy(self, map_loader):
        enemy_map = [
            "E   ",
        ]

        result = map_loader.load_map(enemy_map)

        assert len(result['enemies']) == 1
        assert result['enemies'][0] == (0, 0)

    def test_load_obstacle(self, map_loader):
        obstacle_map = [
            "O   ",
        ]

        result = map_loader.load_map(obstacle_map)

        assert len(result['obstacles']) == 1
        assert result['obstacles'][0] == (0, 0, 40, 40)

    def test_load_ladder(self, map_loader):
        ladder_map = [
            "H",
            "H",
            "H",
        ]

        result = map_loader.load_map(ladder_map)

        # Should have 1 merged ladder (3 tiles merged vertically)
        assert len(result['ladders']) == 1
        ladder = result['ladders'][0]
        assert ladder == (0, 0, 40, 120)  # 3 tiles * 40px = 120px tall

    def test_load_spawn_point(self, map_loader):
        spawn_map = [
            "P   ",
        ]

        result = map_loader.load_map(spawn_map)

        assert len(result['spawn_points']) == 1
        assert result['spawn_points'][0] == (0, 0)

    def test_load_exit(self, map_loader):
        exit_map = [
            "X   ",
        ]

        result = map_loader.load_map(exit_map)

        assert result['exit_pos'] == (0, 0)

    def test_load_complex_map(self, map_loader):
        complex_map = [
            "    X    ",
            "  -----  ",
            "    H    ",
            " E  H    ",
            " ---- OO ",
            "    H    ",
            "    P    ",
            "---------",
        ]

        result = map_loader.load_map(complex_map)

        assert len(result['platforms']) > 0
        assert len(result['enemies']) == 1
        assert len(result['obstacles']) == 2  # 2 separate O tiles (no merging for obstacles)
        assert len(result['ladders']) > 0
        assert len(result['spawn_points']) == 1
        assert result['exit_pos'] is not None

    def test_merge_platforms_horizontal(self, map_loader):
        # Three adjacent dashes should merge into one platform
        platform_map = [
            "---",
        ]

        result = map_loader.load_map(platform_map)

        assert len(result['platforms']) == 1
        assert result['platforms'][0] == (0, 0, 120, 40)

    def test_merge_platforms_separated(self, map_loader):
        # Separated platforms should not merge
        platform_map = [
            "-- --",
        ]

        result = map_loader.load_map(platform_map)

        assert len(result['platforms']) == 2

    def test_merge_ladders_vertical(self, map_loader):
        # Vertically adjacent H's should merge into one ladder
        ladder_map = [
            "H",
            "H",
            "H",
            "H",
        ]

        result = map_loader.load_map(ladder_map)

        assert len(result['ladders']) == 1
        assert result['ladders'][0] == (0, 0, 40, 160)  # 4 tiles tall

    def test_merge_ladders_separated(self, map_loader):
        # Separated ladders should not merge
        ladder_map = [
            "H",
            "H",
            " ",
            "H",
            "H",
        ]

        result = map_loader.load_map(ladder_map)

        assert len(result['ladders']) == 2

    def test_create_sprites(self, map_loader):
        simple_map = [
            "X   ",
            "-   ",
            "H   ",
            "E O ",
            "P   ",
        ]

        map_objects = map_loader.load_map(simple_map)
        sprites = map_loader.create_sprites(map_objects)

        assert len(sprites['platforms']) > 0
        assert len(sprites['enemies']) == 1
        assert len(sprites['obstacles']) == 1
        assert len(sprites['ladders']) > 0
        assert len(sprites['spawn_points']) == 1
        assert sprites['exit_pos'] is not None

        # Check that sprites are correct types
        assert isinstance(sprites['platforms'][0], Platform)
        assert isinstance(sprites['enemies'][0], Enemy)
        assert isinstance(sprites['obstacles'][0], Obstacle)
        assert isinstance(sprites['ladders'][0], Ladder)

    def test_multiple_spawn_points(self, map_loader):
        multi_spawn_map = [
            "P   P",
        ]

        result = map_loader.load_map(multi_spawn_map)

        assert len(result['spawn_points']) == 2
        assert result['spawn_points'][0] == (0, 0)
        assert result['spawn_points'][1] == (160, 0)

    def test_custom_tile_size(self, pygame_init):
        loader = MapLoader(tile_size=20)
        simple_map = [
            "--",
        ]

        result = loader.load_map(simple_map)

        # With tile_size=20, two tiles should be 40px wide
        assert result['platforms'][0] == (0, 0, 40, 20)
