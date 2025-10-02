from settings import G, c, np, h, WORLD_RECT, WINDOW_HEIGHT
from utils import (
    cartesian_to_polar_coords, cartesian_to_polar_vel, 
    point_in_rect, polar_to_cartesian_vel
)
from geodesic import rk4_step

class BlackHole:
    def __init__(self, mass: float, x: float, y: float) -> None:
        # schwarzschild radius
        self.r_s = 2.0 * G * mass / (c*c)
        self.mass = mass
        # attributes for visualization
        self.pos = np.array([x, y], dtype=np.float64)
        self.color = 'red'

class Ray:
    def __init__(
        self, x: float, y: float, vx: float, vy: float, 
        bh_pos: tuple[float, float], r_s: float
    ) -> None:
        # Physics coordinates relative to black hole
        self.pos_phys = np.array(
            [x - bh_pos[0], y - bh_pos[1]], 
            dtype=np.float64
        )
        self.r, self.phi = cartesian_to_polar_coords(
            *self.pos_phys
        )
        self.dr, self.dphi = cartesian_to_polar_vel(
            self.r, self.phi, vx, vy
        )
        f = 1 - r_s/self.r
        self.E = f * np.sqrt(
            (self.dr*self.dr)/(f*f) + 
            (self.r*self.r * self.dphi*self.dphi)/f
        )
        self.state = np.array(
            [self.r, self.phi, self.dr, self.dphi], 
            dtype=np.float64
        )
        # Visual / screen coordinates
        self.pos = np.array([x, y], dtype=np.float64)
        self._trail = [(x, y)]
        self.color = (255, 255, 255)
        self.radius = 5

    def update_state(self, r_s):
        self.state = rk4_step(self.state, r_s, h, self.E)
        self.r, self.phi, self.dr, self.dphi = self.state

    def update_pos_phys(self):
        dx, dy = polar_to_cartesian_vel(
            self.r, self.phi, self.dr, self.dphi
        )
        self.pos_phys[0] += dx
        self.pos_phys[1] += dy

    def update_screen_pos(self, bh_pos):
        self.pos[0] = self.pos_phys[0] + bh_pos[0]
        self.pos[1] = self.pos_phys[1] + bh_pos[1]

    def get_trail(self, cam):
        return [cam.make_cam_relative(point)
                for point in self._trail]

    def update_trail(self):
        if not point_in_rect(self.pos, WORLD_RECT):
            return
        self._trail.append(tuple(self.pos))

    def step(self, r_s: float, bh_pos: np.ndarray) -> int:
        if self.r <= r_s:
            # Ray reached event horizon
            return 1
        if not point_in_rect(self.pos, WORLD_RECT):
            return 1
        # Physics update
        self.update_state(r_s)
        self.update_pos_phys()

        # Image update
        self.update_screen_pos(bh_pos)
        self.update_trail()
        
        return 0

def generate_rays(
        n: int, bh_pos: tuple[float, float], r_s: float
    ) -> list[Ray]:
    """
    Generates n light rays and initializes their
    positions and velocities.
    Args:
        n (int) : the number of light rays you wish to generate.
        bh_pos (tuple[float, float]) : the black hole's position.
        r_s (float) : the schwarzschild radius of the black hole.
    Returns:
        rays : a list of Ray objects.
    """
    rays = []
    
    if n == 1:
        y = WINDOW_HEIGHT / 2
        rays.append(Ray(0, y, -c, 0))
        return rays
    
    for i in range(n):
        rays.append(
            Ray(0, WINDOW_HEIGHT - WINDOW_HEIGHT/(n-1)*i,
                c, 0, bh_pos, r_s)
        )
    return rays
