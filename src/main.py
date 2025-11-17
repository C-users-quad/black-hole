from settings import *
from shaders import *
from utils import *
from cam import Camera

class Game(glw.WindowConfig):
    update_rate = 60.0
    gl_version = (3, 3)
    window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
    title = "Black Hole"
    resizable = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # initialize context and vertex objects
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.prog=self.ctx.program(
            vertex_shader=vert_shader,
            fragment_shader=frag_shader,
        )
        # compute shader for gpu accelereated integration
        self.comp_shade = self.ctx.compute_shader(
            get_comp_shader_src()
        )

        # initialize other
        self.input = set()
        self.cam = Camera([2.0, 0.0, 3.0], [0.0,0.0,0.0])
        self.mvp = get_mvp_matrix(self.cam.pos, self.aspect_ratio)

    def on_render(self, time: float, frametime: float):
        self.update(frametime)
        self.draw()

    def update(self, dt):
        self.cam.update(self.input, dt)
        self.comp_shade.run()
        self.update_program()

    def draw(self):
        self.ctx.clear(*CLEAR_COLOR, depth=1.0)
        self.vao.render()

    def update_program(self):
        # update vbo
        self.vbo.orphan()
        # update uniforms
        self.mvp = get_mvp_matrix(self.cam.get_pos(), self.aspect_ratio)
        self.prog['mvp'].write(self.mvp.to_bytes())

    def on_resize(self, width: int, height: int):
        self.aspect_ratio = width / height
        self.ctx.viewport = (0, 0, width, height)

    def on_mouse_scroll_event(self, x_offset: float, y_offset: float):
        print(f"Scrolled: x={x_offset}, y={y_offset}")

    def on_key_event(self, key, action, modifiers):
        parse_key_input(key, action, modifiers, self.input)

if __name__ == '__main__':
    glw.run_window_config(Game)

