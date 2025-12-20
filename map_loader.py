from platforms import Platform
from enemy import Enemy
from obstacles import Obstacle
from ladder import Ladder


class MapLoader:
    def __init__(self, tile_size=40):
        self.tile_size = tile_size

    def load_map(self, map_data):
        """
        Parse a 2D map and return game objects.

        Returns:
            dict with keys: 'platforms', 'enemies', 'obstacles', 'ladders', 'spawn_points', 'exit_pos'
        """
        platforms = []
        enemies = []
        obstacles = []
        ladders = []
        spawn_points = []
        exit_pos = None

        # Parse map from top to bottom
        for row_idx, row in enumerate(map_data):
            for col_idx, char in enumerate(row):
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size

                if char == '-':
                    # Platform tile
                    platforms.append((x, y, self.tile_size, self.tile_size))
                elif char == 'E':
                    # Enemy spawn
                    enemies.append((x, y))
                elif char == 'O':
                    # Obstacle
                    obstacles.append((x, y, self.tile_size, self.tile_size))
                elif char == 'H':
                    # Ladder tile
                    ladders.append((x, y, self.tile_size, self.tile_size))
                elif char == 'P':
                    # Player spawn point
                    spawn_points.append((x, y))
                elif char == 'X':
                    # Exit marker
                    exit_pos = (x, y)

        # Merge adjacent platform tiles horizontally for efficiency
        merged_platforms = self._merge_platforms(platforms)

        # Merge adjacent ladder tiles vertically for efficiency
        merged_ladders = self._merge_ladders(ladders)

        return {
            'platforms': merged_platforms,
            'enemies': enemies,
            'obstacles': obstacles,
            'ladders': merged_ladders,
            'spawn_points': spawn_points,
            'exit_pos': exit_pos
        }

    def _merge_platforms(self, platform_tiles):
        """Merge adjacent horizontal platform tiles into longer platforms."""
        if not platform_tiles:
            return []

        # Sort by y, then x
        platform_tiles.sort(key=lambda p: (p[1], p[0]))

        merged = []
        current = None

        for x, y, width, height in platform_tiles:
            if current is None:
                current = [x, y, width, height]
            elif current[1] == y and current[0] + current[2] == x:
                # Same row and adjacent - extend current platform
                current[2] += width
            else:
                # Different row or not adjacent - save current and start new
                merged.append(tuple(current))
                current = [x, y, width, height]

        # Don't forget the last platform
        if current is not None:
            merged.append(tuple(current))

        return merged

    def _merge_ladders(self, ladder_tiles):
        """Merge adjacent vertical ladder tiles into taller ladders."""
        if not ladder_tiles:
            return []

        # Sort by x, then y (for vertical merging)
        ladder_tiles.sort(key=lambda p: (p[0], p[1]))

        merged = []
        current = None

        for x, y, width, height in ladder_tiles:
            if current is None:
                current = [x, y, width, height]
            elif current[0] == x and current[1] + current[3] == y:
                # Same column and adjacent vertically - extend current ladder downward
                current[3] += height
            else:
                # Different column or not adjacent - save current and start new
                merged.append(tuple(current))
                current = [x, y, width, height]

        # Don't forget the last ladder
        if current is not None:
            merged.append(tuple(current))

        return merged

    def create_sprites(self, map_objects):
        """
        Create pygame sprite objects from parsed map data.

        Args:
            map_objects: dict from load_map()

        Returns:
            dict with sprite groups
        """
        platform_sprites = []
        enemy_sprites = []
        obstacle_sprites = []
        ladder_sprites = []

        for x, y, width, height in map_objects['platforms']:
            platform_sprites.append(Platform(x, y, width, height))

        for x, y in map_objects['enemies']:
            enemy_sprites.append(Enemy(x, y))

        for x, y, width, height in map_objects['obstacles']:
            obstacle_sprites.append(Obstacle(x, y, width, height))

        for x, y, width, height in map_objects['ladders']:
            ladder_sprites.append(Ladder(x, y, width, height))

        return {
            'platforms': platform_sprites,
            'enemies': enemy_sprites,
            'obstacles': obstacle_sprites,
            'ladders': ladder_sprites,
            'spawn_points': map_objects['spawn_points'],
            'exit_pos': map_objects['exit_pos']
        }
