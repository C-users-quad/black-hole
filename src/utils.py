from settings import np, epsilon, Sequence

def polar_to_cartesian_coords(r: float, phi: float) -> tuple[float, float]:
    """
    Converts a point in polar coordinates
    to a point in cartesian coordinates.
    Args:
        r (float) : 
            the radial coordinate
            of the point you wish to convert.
        phi (float) : 
            the angular coordinate
            of the point you wish to convert.
    Returns:
        (x, y) : 
            the converted cartesian coordinates,
            represented as a tuple of floats.
    """
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y

def cartesian_to_polar_coords(x: float, y: float) -> tuple[float, float]:
    """
    Converts a point in cartesian coordinates 
    to a point in polar coordinates.
    Args:
        x (float) : 
            the x coordinate 
            of the point you wish to convert.
        y (float) : 
            the y coordinate 
            of the point you wish to convert.
    Returns:
        (r, phi) : 
            the converted polar coordinates, 
            represented as a tuple of floats.
    """
    r = np.hypot(y, x)
    phi = np.atan2(y, x)
    return r, phi

def cartesian_to_polar_vel(
        r: float, phi: float, vx: float, vy: float
    ) -> tuple[float, float]:
    """
    Convert a desired Cartesian velocity (vx, vy) 
    into polar velocities (dr, dphi)
    at a given polar position (r, phi).
    Args:
        r (float) : radial distance
        phi (float) : polar angle in radians
        vx (float) : desired Cartesian x velocity
        vy (float) : desired Cartesian y velocity
    Returns:
        (dr, dphi) : radial and angular velocity components
    """
    dr = vx*np.cos(phi) + vy*np.sin(phi)
    dphi = (-vx*np.sin(phi) + vy*np.cos(phi)) / (r + epsilon)
    return dr, dphi

def polar_to_cartesian_vel(
        r: float, phi: float, dr: float, dphi: float
    ) -> tuple[float, float]:
    """
    Convert a desired Polar velocity (dr, dphi) 
    into cartesian velocities (dx, dy)
    at a given polar position (r, phi).
    Args:
        r (float) : the current radial coordinate.
        phi (float) : the current angular coordinate.
        dr (float) : the current radial velocity.
        dphi (float) : the current angular velocity.
    Returns:
        (dx, dy) : the cartesian velocity
    """
    dx = dr*np.cos(phi) - r*np.sin(phi)*dphi
    dy = dr*np.sin(phi) + r*np.cos(phi)*dphi
    return dx, dy

def point_in_rect(point: Sequence[float], rect: Sequence[float]) -> bool:
    """
    Determines if a 2d point is contained within a 2d rectangle
    in cartesian coordinates.
    Args:
        point (Sequence[float]) : the point which you wish to check
        rect (Sequence[float]) : 
            a rectangle represented as a tuple
            of numbers in the form [left, top, width, height]
    Returns:
        bool : 
            True if its inside the rectangle, 
            False if not.
    """
    px, py = point
    left, top, width, height = rect
    return (
        px >= left and
        px <= left + width and
        py >= top and
        py <= top + height
    )
