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

def cartesian_to_spherical_pos(pos):
    """
    given pos=(x, y, z),
    returns (r, theta, phi)
    """
    x, y, z = pos

    r = np.sqrt(x*x + y*y + z*z)
    theta = np.acos(clamp(z / r, -1, 1))
    phi = np.atan2(y, x)

    return r, theta, phi

def cartesian_to_spherical_vel(pos, vel):
    """
    given pos=(x, y, z) & vel=(vx, vy, vz),
    returns (dr, dtheta, dphi)
    """
    x, y, z = pos
    r, theta, phi = cartesian_to_spherical_pos(pos)
    vx, vy, vz = vel
    sin_theta = np.sin(theta)

    dr = (x*vx + y*vy + z*vz) / r
    if sin_theta < EPSILON:
        dtheta = 0.0
        dphi = 0.0
    else:
        dtheta = (dr*np.cos(theta) - vz) / (r*np.sin(theta))
        dphi = (vy*np.cos(phi) - vx*np.sin(phi)) / (r*np.sin(theta))

    return dr, dtheta, dphi

def compute_E(bh_mass, r, dr, dphi):
    """Compute the conserved energy E for the photon."""
    f = 1 - 2*bh_mass / r
    return f * np.sqrt((dr**2/f + (r**2)*(dphi**2))/f)

def compute_dt(bh_mass, r, E):
    """
    Compute the time velocity component
    dt based on the conserved energy E.
    """
    return E / (1 - 2 * bh_mass / r)

def normalize(v):
    """given a vector v, returns a normalized vector."""
    mag = np.linalg.norm(v)
    if mag == 0:
        return v
    return v / mag

def get_comp_src():
    with open('shaders/geodesic.comp') as f:
        return f.read()

def get_vert_src():
    with open('shaders/vertex.glsl') as f:
        return f.read()

def get_frag_src():
    with open('shaders/fragment.glsl') as f:
        return f.read()
