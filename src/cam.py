from settings import np, pygame, K_d, K_a, K_s, K_w

class Camera:
    def __init__(self, x:float, y: float) -> None:
        self.pos = np.array([x, y], dtype=np.float64)
        self.direction = np.zeros(
            shape=(2,), 
            dtype=np.float64
        )
        self.speed = 1000

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        self.direction[0] = int(keys[K_d]) - int(keys[K_a])
        self.direction[1] = int(keys[K_s]) - int(keys[K_w])
        mag_dir = np.linalg.norm(self.direction)
        if mag_dir != 0:
            self.direction /= mag_dir

    def move(self, dt: float) -> None:
        self.pos += self.direction * self.speed * dt

    def make_cam_relative(
            self, point: tuple[float, float]
        ) -> tuple[float, float]:
        """Returns the inserted point made relative to the cameras position"""
        return (point[0] - self.pos[0], point[1] - self.pos[1])

    def update(self, dt: float) -> None:
        """Gets key input and updates the cameras position"""
        self.input()
        self.move(dt)
