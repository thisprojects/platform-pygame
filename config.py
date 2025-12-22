# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)

# Game settings (all speeds are now per second, not per frame)
GRAVITY = 2000  # pixels per second squared (was 0.8 per frame² * 50² FPS)
PLAYER_SPEED = 175  # pixels per second (was 3.5 per frame * 50 FPS)
PLAYER_JUMP = -928  # pixels per second (increased by 10% from -844)
PLAYER_CLIMB_SPEED = 150  # pixels per second for climbing ladders
PROJECTILE_SPEED = 400  # pixels per second (was 8 per frame * 50 FPS)
ENEMY_SPEED = 100  # pixels per second (was 2 per frame * 50 FPS)
ENEMY_SHOOT_CHANCE = 0.5  # Probability per second (was 0.01 per frame * 50 FPS)

# Enemy alert mode settings
ENEMY_ALERT_DURATION = 7.0  # Seconds to stay alert
ENEMY_ALERT_COOLDOWN = 2.0  # Cooldown before re-alert
ENEMY_RAYCAST_INTERVAL = 0.2  # Check for players every 0.2 seconds
ENEMY_DETECTION_VERTICAL_TOLERANCE = (
    150  # Vertical distance for detection (within 2-3 platform heights)
)

# Enemy burst fire settings (alert mode)
ENEMY_BURST_SHOT_COUNT = 3  # Number of shots per burst
ENEMY_BURST_SHOT_INTERVAL = 0.5  # Seconds between shots in burst (quick fire)
ENEMY_BURST_COOLDOWN = 3.0  # Seconds to wait after burst before next burst
