import sys
import os
import pytest
import pygame
import importlib.util

# Add parent directory to path to import game modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Load the local platform module to avoid conflict with built-in platform module
# and inject it into sys.modules so other imports can find it
platform_path = os.path.join(parent_dir, 'platform.py')
spec = importlib.util.spec_from_file_location("platform", platform_path)
platform_module = importlib.util.module_from_spec(spec)
sys.modules['platform'] = platform_module
spec.loader.exec_module(platform_module)


@pytest.fixture(scope="session", autouse=True)
def pygame_init_session():
    """Initialize pygame once for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def pygame_display():
    """Provide a pygame display for tests that need it."""
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.display.set_mode((800, 600))
    yield
    pygame.display.quit()
