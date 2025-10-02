from settings import (
    pygame, sys, WINDOW_WIDTH, WINDOW_HEIGHT, CLEAR_COLOR, 
    NUM_RAYS, SRCALPHA, RESIZABLE, FPS, QUIT, MOUSEWHEEL,
    WORLD_RECT
)
from sprites import BlackHole, generate_rays
from cam import Camera

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.display = pygame.display.set_mode(
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            flags=SRCALPHA | RESIZABLE
        )
        self.on = True
        self.clock = pygame.time.Clock()
        self.cam = Camera(
            x=WINDOW_WIDTH/2,
            y=WINDOW_HEIGHT/2
        )

        # sprite setup
        self.black_hole = BlackHole(
            mass=100000, 
            x=WORLD_RECT[2]/2, 
            y=WORLD_RECT[3]/2
        )
        self.rays = generate_rays(
            n=NUM_RAYS, 
            bh_pos=self.black_hole.pos, 
            r_s=self.black_hole.r_s
        )
    
    def run(self):
        while self.on:
            # time between frames in seconds
            self.dt = self.clock.tick(FPS) / 1000
            self.event_handler()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.on = False
            elif event.type == MOUSEWHEEL:
                self.cam.update_zoom(event.y)

    def draw(self):
        # clear window
        self.display.fill(CLEAR_COLOR)
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
        pygame.display.flip()

    def update(self):
        for ray in self.rays:
            ray.step(
                self.black_hole.pos,
                self.black_hole.r_s
            )
        self.cam.update(self.dt)

if __name__ == '__main__':
    game = Game()
    game.run()
