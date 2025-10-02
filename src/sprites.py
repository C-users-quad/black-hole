from settings import (
    G, c, np, h, RAY_TRAIL_COLOR, 
    RAY_TRAIL_RADIUS, TYPE_CHECKING, WORLD_RECT
)
from utils import (
    cartesian_to_polar_coords, cartesian_to_polar_vel, 
    point_in_rect, polar_to_cartesian_vel
)
from geodesic import rk4_step
if TYPE_CHECKING:
    from cam import Camera

class BlackHole:
    """A Schwarzschild black hole"""
    def __init__(self, mass: float, x: float, y: float) -> None:
        # Schwarzschild radius
        self.r_s = 2.0 * G * mass / (c*c)
        self.mass = mass
        # attributes for visualization
        self.pos = np.array([x, y])
        self.color = 'red'

class Ray:
    """
    A light ray that moves according to the 
    curvature of Schwarzschild spacetime.
    """
    def __init__(
        self, x: float, y: float, vx: float, vy: float, 
        bh_pos: tuple[float, float], r_s: float
    ) -> None:
        # Physics coordinates relative to black hole
        self.pos_phys = np.array(
            [x - bh_pos[0], y - bh_pos[1]]
        )
        self.r, self.phi = cartesian_to_polar_coords(
            *self.pos_phys
        )
        self.dr, self.dphi = cartesian_to_polar_vel(
            self.r, self.phi, vx, vy
        )

        # setup state attributes
        f = 1 - r_s/self.r
        self.E = f * np.sqrt(
            (self.dr*self.dr)/(f*f) + 
            (self.r*self.r * self.dphi*self.dphi)/f
        )
        self.state = np.array([self.r, self.phi, self.dr, self.dphi])

        # Visual / screen coordinates
        self.pos = np.array([x, y])
        self._trail = [(x, y)]
        self.color = RAY_TRAIL_COLOR
        self.radius = RAY_TRAIL_RADIUS

    def update_state(self, r_s: float) -> None:
        """
        Updates the state vector with geodesic calculations
        integrated with Runge-Kutta 4.
        """
        self.state = rk4_step(self.state, r_s, h, self.E)
        self.r, self.phi, self.dr, self.dphi = self.state

    def update_pos_phys(self) -> None:
        """
        Updates the cartesian representation
        of the light rays physical position.
        """
        dx, dy = polar_to_cartesian_vel(
            self.r, self.phi, self.dr, self.dphi
        )
        self.pos_phys[0] += dx
        self.pos_phys[1] += dy

    def update_screen_pos(self, bh_pos: np.ndarray) -> None:
        """
        Updates the position of the light ray in world space
        with respect to the position of the black hole.
        """
        self.pos[0] = self.pos_phys[0] + bh_pos[0]
        self.pos[1] = self.pos_phys[1] + bh_pos[1]

    def get_trail(self, cam: "Camera") -> list[tuple[float, float]]:
        """
        Gets a list of points representing the path 
        of the light ray in camera-relative world space
        """
        return [cam.make_cam_relative(point)
                for point in self._trail]

    def update_trail(self) -> None:
        """
        Updates the trail represented by points in world space
        """
        self._trail.append(tuple(self.pos))

    def step(self, bh_pos: np.ndarray, r_s: float) -> int:
        """
        Steps the ray forward through space and time using
        geodesic calculations to update the trajectory.
        """
        if self.r <= r_s:
            # Ray reached event horizon
            return 1
        if not point_in_rect(self.pos, WORLD_RECT):
            # Ray outside of world bounds
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
        r_s (float) : the Schwarzschild radius of the black hole.
    Returns:
        rays : a list of Ray objects.
    """
    rays = []

    if n == 1:
        y = WORLD_RECT[3] / 2
        rays.append(Ray(0, y, -c, 0))
        return rays
    
    for i in range(n):
        if i >= n/2:
            angular_velocity = 1.5
        else:
            angular_velocity = -1.5
        rays.append(
            Ray(0, WORLD_RECT[3] - WORLD_RECT[3]/(n-1)*i,
                c, angular_velocity, bh_pos, r_s)
        )
    return rays
