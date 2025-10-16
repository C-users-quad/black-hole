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

def get_mvp_matrix(cam_pos, aspect):
    projection = glm.perspective(
        glm.radians(FOV), aspect, Z_NEAR, Z_FAR
    )
    view = glm.lookAt(
        glm.vec3(cam_pos), glm.vec3(0, 0, 0), UP
    )
    model = glm.mat4(1.0)
    return projection * view * model

def spherical_to_cartesian(r, theta, phi):
    x = r*np.sin(theta)*np.cos(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)
    return (x, y, z)

def cartesian_to_spherical(x, y, z):
    r = np.sqrt(x*x + y*y + z*z)
    theta = np.acos(max(-1,min(1,z/(r+EPSILON))))
    phi = np.atan2(y,x)
    return (r, theta, phi)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm < EPSILON:
        return v
    return v / norm
