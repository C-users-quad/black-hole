from settings import *
from utils import cartesian_to_polar_coords, cartesian_to_polar_vel, polar_to_cartesian_coords, point_in_rect
from geodesic import *

class BlackHole:
    def __init__(self, mass: float, x: float, y: float) -> None:
        # schwarzschild radius
        self.r_s = 2.0 * G * mass / (c*c)
        self.mass = mass
        # attributes for visualization
        self.pos = np.array([x, y], dtype=np.float64)
        self.color = 'red'

class Ray:
    def __init__(self, x: float, y: float, vx: float, vy: float) -> None:
        # used for physics
        self.r, self.phi = cartesian_to_polar_coords(x, y)
        self.dr, self.dphi = cartesian_to_polar_vel(
            self.r, 
            self.phi, 
            vx, 
            vy
        )
        self.state = np.array([
            self.r, self.phi, self.dr, self.dphi
        ], dtype=np.float64)
        # used for visualization
        self.pos = np.array([x, y], dtype=np.float64)
        self.trail_length = 10
        self._trail = [(x, y)]
        self.color = (255, 255, 255)
        self.radius = 5

    def step(self, r_s: float, bh_pos: np.ndarray) -> int:
        """
        Updates the rays position.
        Args:
            r_s (float) : 
                the schwarzschild radius 
                of the central black hole
            bh_pos (np.ndarray) : 
                the position of the black hole
                in cartesian coordinates.
        Returns:
            int : 
                0 for not hitting the horizon/being out of bounds,
                1 for hitting it or going outside the world bounds.
        """
        if self.r <= r_s:
            # ray reached event horizon.
            return 1
        
        # physics update
        self.state = rk4_step(self.state, r_s, h)
        self.r, self.phi, self.dr, self.dphi = self.state

        # image position update
        self.pos[:] = polar_to_cartesian_coords(self.r, self.phi)
        # y flipped for pygame
        self.pos[1] *= -1
        self.pos += bh_pos
        if len(self._trail) >= self.trail_length:
            self._trail.pop(0)
        self._trail.append(tuple(self.pos))

        if not point_in_rect(self.pos, WORLD_RECT):
            # ray is going off to infinity (outside of world bounds).
            return 1
        return 0
    
    def get_trail(self) -> list[tuple[float, float, float]]:
        """
        Gets a list of positions and alpha values ordered such that
        index -1 of trail is the front of the trail
        index 0 of trail is the back of the trail
        Returns:
            trail : 
                a list of positions and alpha values
                in the trail represented as (x, y, alpha).
        """
        max_alpha = 255
        trail = []
        for i, pos in enumerate(self._trail):
            alpha = int(max_alpha * (i + 1) / len(self._trail))
            trail.append(pos + (alpha,))
        return trail

def generate_rays(n: int) -> list[Ray]:
    """
    Generates n light rays and initializes their
    positions and velocities.
    Args:
        n (int) : the number of light rays you wish to generate.
    Returns:
        rays : a list of Ray objects.
    """
    rays = []
    for i in range(n):
        rays.append(
            Ray(0, WINDOW_HEIGHT - WINDOW_HEIGHT/(n-1)*i, c, 0)
        )
        print(rays[0].pos)
    return rays
