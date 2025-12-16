# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Game settings (all speeds are now per second, not per frame)
GRAVITY = 2000  # pixels per second squared (was 0.8 per frame² * 50² FPS)
PLAYER_SPEED = 175  # pixels per second (was 3.5 per frame * 50 FPS)
PLAYER_JUMP = -750  # pixels per second (was -15 per frame * 50 FPS)
PROJECTILE_SPEED = 400  # pixels per second (was 8 per frame * 50 FPS)
ENEMY_SPEED = 100  # pixels per second (was 2 per frame * 50 FPS)
ENEMY_SHOOT_CHANCE = 0.5  # Probability per second (was 0.01 per frame * 50 FPS)
