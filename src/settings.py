import numpy as np
import math
import moderngl
import moderngl_window as glw
import glm

# general
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
EPSILON = 1e-4

# rendering params
Z_NEAR, Z_FAR = 0.1, 100.0
UP = (0, 1, 0)
FOV = 45
CLEAR_COLOR = (0.0, 0.0, 0.0)

# cam params
MIN_ZOOM, MAX_ZOOM = 1, 10
PAN_SPEED = 100
ZOOM_SPEED = 1

# keys
MOVE_KEYS = {
    119: "W",
    97: "A",
    115: "S",
    100: "D"
}