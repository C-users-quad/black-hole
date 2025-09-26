from src.settings import *

class BlackHole:
    def __init__(self, mass):
        self.r_s = 2.0 * G * mass / (c*c)
        self.mass = mass

def get_best_fit(x, y):
    x = np.array(x)
    y = np.array(y)
    coeffs = np.polyfit(x, y, 2)
    print("Quadtratic coefficients (a, b, c):", coeffs)

def cartesian_to_polar_coords(x, y):
    r = np.hypot(y, x)
    phi = np.atan2(y, x)
    return r, phi

def cartesian_to_polar_vel(r, phi, vx, vy):
    """
    Convert a desired Cartesian velocity (vx, vy) into polar velocities (dr, dphi)
    at a given polar position (r, phi).
    Args:
        r (float): radial distance
        phi (float): polar angle in radians
        vx (float): desired Cartesian x velocity
        vy (float): desired Cartesian y velocity
    Returns:
        (dr, dphi): radial and angular velocity components
    """
    # Solve the linear system:
    # vx = dr*cos(phi) - r*dphi*sin(phi)
    # vy = dr*sin(phi) + r*dphi*cos(phi)
    # for dr and dphi
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)
    dr = vx*cos_phi + vy*sin_phi
    dphi = (-vx*sin_phi + vy*cos_phi) / r
    return dr, dphi

class Ray:
    def __init__(self, x, y, vx, vy):
        self.r, self.phi = cartesian_to_polar_coords(x, y)
        self.dr, self.dphi = cartesian_to_polar_vel(self.r, self.phi, vx, vy)
        self.state = np.array([
            self.r, self.phi, self.dr, self.dphi
        ], dtype=np.float64)
        self.x = []
        self.y = []

    def step(self, r_s):
        if self.r <= r_s:
            print("Reached event horizon!!")
            return 1
        self.state = rk4step(self.state, r_s, h)
        self.r, self.phi, self.dr, self.dphi = self.state
        self.x.append(self.r*np.cos(self.phi))
        self.y.append(self.r*np.sin(self.phi))
        return 0

def enforce_null(state, r_s):
    r, phi, dr, dphi = state
    r += epsilon
    f = 1 - r_s/r
    dt = math.sqrt((dr*dr)/(f*f) + (r*r*dphi*dphi)/f)
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

def rk4step(state: np.ndarray, r_s: float, h: float) -> np.ndarray:
    """
    A high precision geodesic calculation for integrating a photons trajectory over time.
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

black_hole = BlackHole(100)
ray = Ray(1000, 750, -c, 0)
num = 0
while num == 0:
    num = ray.step(black_hole.r_s)
get_best_fit(ray.x, ray.y)
plt.figure(figsize=(6,6))
plt.plot(ray.x, ray.y, marker='.', linestyle='-', color='blue')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Ray trajectory around black hole')
plt.axis('equal')  # keep aspect ratio so circles look like circles
theta = np.linspace(0, 2*np.pi, 100)
r = black_hole.r_s
x = r*np.cos(theta)
y = r*np.sin(theta)
plt.plot(x, y, 'r-')
plt.axis('equal')
plt.grid(True)
plt.show()