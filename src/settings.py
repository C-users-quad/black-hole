import numpy as np
import moderngl
import moderngl_window as glw
import glm
import struct

# general
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
EPSILON = 1e-4

# rendering params
Z_NEAR, Z_FAR = 0.1, 100.0
UP = (0, 1, 0)
FOV = 45
CLEAR_COLOR = (0.0, 0.0, 0.0)
SCREEN_QUAD = np.array([
    -1.0, -1.0, 0.0, 0.0,  # bottom-left (x, y, u, v)
     1.0, -1.0, 1.0, 0.0,  # bottom-right
    -1.0,  1.0, 0.0, 1.0,  # top-left
     1.0,  1.0, 1.0, 1.0,  # top-right
], dtype='f4')
LOCAL_SIZE = 16

# physics params
G = c = h = 1
BH_MASS = 0.5
R_S = BH_MASS * 2

# cam params
MIN_ZOOM, MAX_ZOOM = 1, 20
PAN_SPEED = 5
ZOOM_SPEED = 10

# keys
MOVE_KEYS = {
    119: "W",
    97: "A",
    115: "S",
    100: "D"
}
