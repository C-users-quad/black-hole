from settings import np, epsilon

def geodesic(state: np.ndarray, r_s: float, E: float) -> np.ndarray:
    """
    Calculates the trajectory of light across Schwarzschild spacetime.
    Args:
        state (np.ndarray) : a vector representative of [r, ϕ, dr, dϕ]
        r_s (float) : the Schwarzschild radius of the central black hole
        E (float) : the conserved energy of the light ray
    Returns:
        np.ndarray : the derivative of the state vector
    """
    # unpack state vector into its components
    r, phi, dr, dphi = state
    r += epsilon

    # recompute key values
    f = 1 - r_s/r + epsilon
    dt = E / f

    # radial acceleration
    d2r = (
        r_s/(2*r*r*f)*dr*dr -
        r_s/(2*r*r)*f*dt*dt +
        (r - r_s)*dphi*dphi
    )

    # angular acceleration
    d2phi = -2*(dr*dphi/r)

    return np.array([dr, dphi, d2r, d2phi])

def rk4_step(
        state: np.ndarray, r_s: float, h: float, E: float
    ) -> np.ndarray:
    """
    A high precision geodesic calculation for 
    integrating a photons trajectory over time.
    Args:
        state (np.ndarray) : a vector representative of [r, ϕ, dr, dϕ]
        r_s (float) : the Schwarzschild radius of the central black hole
        h (float) : an arbitrary step size; the affine parameter
        E (float) : the conserved energy of the light ray
    Returns:
        np.ndarray : new state vector
    """
    k1 = geodesic(state, r_s, E)
    k2 = geodesic(state + (h/2)*k1, r_s, E)
    k3 = geodesic(state + (h/2)*k2, r_s, E)
    k4 = geodesic(state + h*k3, r_s, E)
    return state + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
