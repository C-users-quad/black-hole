import pygame
from pygame.constants import K_w, K_s, K_a, K_d, SRCALPHA, QUIT, RESIZABLE, MOUSEWHEEL
import numpy as np
import sys
from typing import Sequence, Literal, TYPE_CHECKING

# settings
WINDOW_WIDTH, WINDOW_HEIGHT = 900, 800
HALF_WORLD_LENGTH = 2500
WORLD_RECT = ( # (left, top, width, height)
    0, 0, 
    2*HALF_WORLD_LENGTH, 2*HALF_WORLD_LENGTH
)
FPS = 120
NUM_RAYS = 350
MIN_ZOOM = 0.217
CLEAR_COLOR = (0, 0, 0)
RAY_TRAIL_RADIUS = 5
RAY_TRAIL_COLOR = (255, 255, 255)

# physical constants
G = 1
h = 1
c = 15
epsilon = 1e-2
