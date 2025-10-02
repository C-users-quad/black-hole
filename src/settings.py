import pygame
from pygame.constants import K_w, K_s, K_a, K_d, SRCALPHA, QUIT, RESIZABLE, MOUSEWHEEL
import numpy as np
import sys
import matplotlib.pyplot as plt
from typing import Sequence
from numba import njit, prange

WINDOW_WIDTH, WINDOW_HEIGHT = 900, 800
HALF_WORLD_LENGTH = 10000
WORLD_RECT = (
    -HALF_WORLD_LENGTH, -HALF_WORLD_LENGTH, 
    2*HALF_WORLD_LENGTH, 2*HALF_WORLD_LENGTH
)
FPS = 300
NUM_RAYS = 100
MIN_ZOOM = 0.217

G = 1
h = 1
c = 5
epsilon = 1e-2
