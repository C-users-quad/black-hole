from settings import (
    np, pygame, K_d, K_a, K_s, K_w, Literal,
    MIN_ZOOM, WINDOW_WIDTH, WINDOW_HEIGHT
)

class Camera:
    """2D camera"""
    def __init__(self, x: float, y: float) -> None:
        self.pos = np.array([x, y])
        self.direction = np.zeros(shape=(2,))
        self.speed = 1000
        self.zoom = 1

    def input(self) -> None:
        """Changes movement direction depending on key input"""
        keys = pygame.key.get_pressed()
        self.direction[0] = int(keys[K_d]) - int(keys[K_a])
        self.direction[1] = int(keys[K_s]) - int(keys[K_w])
        mag_dir = np.linalg.norm(self.direction)
        if mag_dir != 0:
            self.direction /= mag_dir

    def move(self, dt: float) -> None:
        """Updates camera position based on current direction"""
        self.pos += self.direction * self.speed * dt

    def update_zoom(self, event_y: Literal[-1, 1]) -> None:
        """
        Updates zoom clamped to a minimum
        based on mouse scroll input
        """
        new_zoom = self.zoom * 1.1 ** event_y
        self.zoom = max(MIN_ZOOM, new_zoom)

    def make_cam_relative(
            self, point: tuple[float, float]
        ) -> tuple[float, float]:
        """
        Returns the inserted point 
        made relative to the cameras position
        """
        return (
            (point[0] - self.pos[0]) * self.zoom + WINDOW_WIDTH / 2, 
            (point[1] - self.pos[1]) * self.zoom + WINDOW_HEIGHT / 2
        )

    def update(self, dt: float) -> None:
        """Gets key input and updates the cameras position"""
        self.input()
        self.move(dt)
