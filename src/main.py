from settings import *
from shaders import vertex_shader, fragment_shader
from black_hole import BlackHole
from camera import Camera

class Canvas(app.Canvas):
    def __init__(self):
        super().__init__(title='black-hole', size=(WINDOW_WIDTH, WINDOW_HEIGHT), keys='interactive')
        gloo.set_clear_color('black')

        self.dt = DT
        self.timer = app.Timer(interval=self.dt, connect=self.on_timer, start=True)

        self.black_hole = BlackHole(1_000_000 * sol)

        self.cam = Camera()
        self.keys = set() # a set of movement keys

        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.update_program()

        self.show()
    
    def update_program(self):
        self.program['a_color'] = self.black_hole.color
        self.program['a_pos'] = self.black_hole.pos
        self.program['a_radius'] = self.black_hole.r_s
        self.program['u_CamPos'] = self.cam.pos
        self.program['u_CamZoom'] = self.cam.zoom
        self.program['u_WindowSize'] = self.size

    def on_timer(self, event):
        self.dt = event.dt
        self.cam.update(self.keys, self.dt)
        self.update_program()
        self.update()
    
    def on_key_press(self, event):
        if event.key.name in MOVEMENT_KEYS:
            self.keys.add(event.key.name)

    def on_key_release(self, event):
        if event.key.name in MOVEMENT_KEYS:
            self.keys.discard(event.key.name)

    def on_mouse_wheel(self, event):
        if 'Control' in event.modifiers:
            self.cam.update_speed(event.delta[1])
        else:
            self.cam.update_zoom(event.delta[1])

    def on_draw(self, event):
        self.program.draw('points')

if __name__ == '__main__':
    c = Canvas()
    app.run()
