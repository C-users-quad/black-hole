from settings import *
from shaders import *
from utils import *
from cam import Camera

# the points of the corners
vertices = np.array([
    [-0.5, -0.5, -0.5,   0, 0, 0], # front bottom left(0)
    [ 0.5, -0.5, -0.5,   1, 0, 0], # front bottom right(1)
    [-0.5,  0.5, -0.5,   0, 0, 1], # front top left(2)
    [ 0.5,  0.5, -0.5,   1, 0, 1], # front top right(3)

    [-0.5, -0.5,  0.5,   0, 1, 0], # back bottom left(4)
    [ 0.5, -0.5,  0.5,   1, 1, 0], # back bottom right(5)
    [-0.5,  0.5,  0.5,   0, 1, 1], # back top left(6)
    [ 0.5,  0.5,  0.5,   1, 1, 1], # back top right(7)
], dtype='f4')
indices = np.array([
    0, 1, 2, # front triangles
    1, 2, 3,

    4, 5, 6, # back triangles
    5, 6, 7,

    0, 4, 2, # left triangles
    4, 2, 6,

    1, 5, 3, # right triangles
    5, 3, 7,

    3, 2, 7, # top triangles
    2, 7, 6,

    1, 5, 0, # bottom triangles
    5, 0, 4
], dtype='u4')

class Game(glw.WindowConfig):
    update_rate = 60.0
    gl_version = (3, 3)
    window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
    title = "3d tests go brrr"
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
        self.comp_shade = self.ctx.compute_shader(compute_shader)
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.ibo = self.ctx.buffer(indices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, "3f 3f", "in_vert", "in_color")],
            index_buffer=self.ibo
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
        self.vbo.write(vertices.tobytes())
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
