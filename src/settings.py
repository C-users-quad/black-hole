import pygame
import numpy as np
import sys
import matplotlib.pyplot as plt
from typing import Sequence

WINDOW_WIDTH, WINDOW_HEIGHT = 900, 800
WORLD_RECT = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
FPS = 120

G = c = h = 1
epsilon = 1e-2
