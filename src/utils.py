from settings import njit, np, G as _G, c as _c, sol as _sol

G = _G
c = _c
sol = _sol

@njit
def get_schwarzschild_radius(M):
    """
    Input a mass in kg to get the schwarzschild radius of that mass
    """
    return (2.0 * G * M) / (c*c)
