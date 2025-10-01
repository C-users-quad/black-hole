from settings import *
from utils import *

def enforce_null(state: np.ndarray, r_s: float) -> None:
    """
    Enhances accuracy of null geodesic calculations
    by recalculating dr and dphi every time.
    Args:
        state (np.ndarray) : a vector representative of [r, ϕ, dr, dϕ]
        r_s (float) : the schwarzschild radius of the central black hole
    """
    r, phi, dr, dphi = state
    r += epsilon
    f = 1 - r_s/r
    dt = np.sqrt((dr*dr)/(f*f) + (r*r*dphi*dphi)/f)
    scale = c / dt
    state[2] = dr * scale
    state[3] = dphi * scale

def geodesic(state: np.ndarray, r_s: float) -> np.ndarray:
    """
    Calculates the trajectory of light across schwarzschild spacetime.
    Args:
        state (np.ndarray) : a vector representative of [r, ϕ, dr, dϕ]
        r_s (float) : the schwarzschild radius of the central black hole
    Returns:
        np.ndarray : the derivative of the state vector
    """
    # unpack state vector into its components
    r, phi, dr, dphi = state
    r += epsilon

    # recompute key values
    f = 1 - r_s/r
    dt = np.sqrt((dr*dr)/(f*f) + (r*r*dphi*dphi)/f)

    # radial acceleration
    d2r = (
        r_s/(2*r*r*f)*dr*dr -
        r_s/(2*r*r)*f*dt*dt -
        (r - r_s)*dphi*dphi
    )

    # angular acceleration
    d2phi = -2*(dr*dphi/r)

    return np.array([dr, dphi, d2r, d2phi], dtype=np.float64)

def rk4_step(state: np.ndarray, r_s: float, h: float) -> np.ndarray:
    """
    A high precision geodesic calculation for 
    integrating a photons trajectory over time.
    Args:
        state (np.ndarray) : a vector representative of [r, ϕ, dr, dϕ]
        r_s (float) : the schwarzschild radius of the central black hole
        h (float) : an arbitrary step size; the affine parameter
    Returns:
        np.ndarray : new state vector
    """
    enforce_null(state, r_s)
    k1 = geodesic(state, r_s)
    k2 = geodesic(state + (h/2)*k1, r_s)
    k3 = geodesic(state + (h/2)*k2, r_s)
    k4 = geodesic(state + h*k3, r_s)
    return state + (h/6)*(k1 + 2*k2 + 2*k3 + k4)

# black_hole = BlackHole(100, 100, 100)
# ray = Ray(1000, 750, -c, 0)
# num = 0
# while num == 0:
#     num = ray.step(black_hole.r_s, black_hole.pos)
# get_best_fit(ray.x, ray.y)
# plt.figure(figsize=(6,6))
# plt.plot(ray.x, ray.y, marker='.', linestyle='-', color='blue')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('Ray trajectory around black hole')
# plt.axis('equal')  # keep aspect ratio so circles look like circles
# theta = np.linspace(0, 2*np.pi, 100)
# r = black_hole.r_s
# x = black_hole.pos[0]+r*np.cos(theta)
# y = black_hole.pos[1]+r*np.sin(theta)
# plt.plot(x, y, 'r-')
# plt.axis('equal')
# plt.grid(True)
# plt.show()
