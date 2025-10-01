from settings import *
from geodesic import *
from sprites import BlackHole, generate_rays

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.display = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.on = True
        self.clock = pygame.time.Clock()

        # sprite setup
        self.black_hole = BlackHole(
            50, 
            WINDOW_WIDTH/2, 
            WINDOW_HEIGHT/2
        )
        self.rays = generate_rays(3, self.black_hole.pos)
        
    def run(self):
        while self.on:
            self.dt = self.clock.tick(FPS) / 1000
            self.event_handler()
            self.update()
            self.display.fill('black')
            self.draw()
            pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on = False
                pygame.quit()
                sys.exit()

    def draw(self):
        # draw black hole
        pygame.draw.circle(
            self.display, 
            self.black_hole.color, 
            self.black_hole.pos, 
            self.black_hole.r_s
        )
        # draw rays
        for j, ray in enumerate(self.rays):
            for i, point in enumerate(ray.get_trail()):
                pygame.draw.circle(
                    self.display,
                    ray.color+(point[2],),
                    point[:2],
                    ray.radius
                )
                print(point[:2]) if i == 0 and j == 0 else ''

    def update(self):
        for ray in self.rays:
            ray.step(
                self.black_hole.r_s, 
                self.black_hole.pos
            )

if __name__ == '__main__':
    game = Game()
    game.run()
