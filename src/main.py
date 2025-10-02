from settings import (
    pygame, WINDOW_WIDTH, WINDOW_HEIGHT, NUM_RAYS, 
    SRCALPHA, RESIZABLE, FPS, QUIT, MOUSEWHEEL, 
    sys, prange
)
from sprites import BlackHole, generate_rays
from cam import Camera

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.display = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), SRCALPHA | RESIZABLE
        )
        self.on = True
        self.clock = pygame.time.Clock()
        self.cam = Camera(x=0, y=0)

        # sprite setup
        self.black_hole = BlackHole(
            mass=500, 
            x=WINDOW_WIDTH/2+500, 
            y=WINDOW_HEIGHT/2 + 100
        )
        self.rays = generate_rays(
            n=NUM_RAYS, 
            bh_pos=self.black_hole.pos, 
            r_s=self.black_hole.r_s
        )
    
    def run(self):
        while self.on:
            self.dt = self.clock.tick(FPS) / 1000
            self.event_handler()
            self.update()
            self.display.fill('black')
            self.draw()
            pygame.display.update()
            print(self.cam.zoom)

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.on = False
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEWHEEL:
                self.cam.update_zoom(event.y)

    def draw(self):
        # draw rays
        for ray in self.rays:
            pygame.draw.lines(
                self.display, ray.color, False, 
                ray.get_trail(self.cam), 
                int(ray.radius * self.cam.zoom)
            )
        # draw black hole
        pygame.draw.circle(
            self.display, 
            self.black_hole.color, 
            self.cam.make_cam_relative(self.black_hole.pos),
            self.black_hole.r_s * self.cam.zoom
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
