from settings import (
    glm, np, UP, Z_NEAR, Z_FAR, FOV, MOVE_KEYS, EPSILON
)

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def parse_key_input(key, action, modifiers, input):
    if key not in MOVE_KEYS.keys():
        # No valid keys were pressed
        return

    if action == "ACTION_PRESS":
        input.add(MOVE_KEYS[key])
    elif action == "ACTION_RELEASE":
        input.remove(MOVE_KEYS[key])

def get_comp_src():
    with open('shaders/geodesic.comp') as f:
        return f.read()

def get_vert_src():
    with open('shaders/vertex.glsl') as f:
        return f.read()

def get_frag_src():
    with open('shaders/fragment.glsl') as f:
        return f.read()
