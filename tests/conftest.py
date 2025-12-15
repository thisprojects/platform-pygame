import sys
import os
import pytest
import pygame
import importlib.util

# Add parent directory to path to import game modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Note: We don't override the built-in platform module to avoid conflicts with pygame
# Individual test files load the platforms module directly as needed


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
