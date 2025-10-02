from settings import (
    pygame, WINDOW_WIDTH, WINDOW_HEIGHT, NUM_RAYS, 
    SRCALPHA, FPS, QUIT, sys, prange
)
from sprites import BlackHole, generate_rays
from cam import Camera

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.display = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), SRCALPHA
        )
        self.on = True
        self.clock = pygame.time.Clock()
        self.cam = Camera(0,0)

        # sprite setup
        self.black_hole = BlackHole(
            50, 
            WINDOW_WIDTH/2, 
            WINDOW_HEIGHT/2
        )
        self.rays = generate_rays(
            NUM_RAYS, self.black_hole.pos, self.black_hole.r_s
        )
    
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
            if event.type == QUIT:
                self.on = False
                pygame.quit()
                sys.exit()

    def draw(self):
        # draw rays
        for ray in self.rays:
            pygame.draw.lines(
                self.display, ray.color, False, 
                ray.get_trail(self.cam), ray.radius
            )
        # draw black hole
        pygame.draw.circle(
            self.display, 
            self.black_hole.color, 
            self.cam.make_cam_relative(self.black_hole.pos),
            self.black_hole.r_s
        )

    def update(self):
        for ray in self.rays:
            return_value = ray.step(
                self.black_hole.r_s, 
                self.black_hole.pos
            )
        self.cam.update(self.dt)

if __name__ == '__main__':
    game = Game()
    game.run()
