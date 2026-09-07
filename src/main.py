from settings import *
from utils import *
from cam import Camera

class Game(glw.WindowConfig):
    update_rate = 60.0
    gl_version = (3, 3)
    window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
    title = "Black Hole"
    resizable = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # initialize context and vertex objects
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.prog=self.ctx.program(
            vertex_shader=get_vert_src(),
            fragment_shader=get_frag_src(),
        )
        # compute shader for gpu accelereated integration
        self.compute = self.ctx.compute_shader(
            get_comp_src()
        )
        self.compute['windowWidth'].write(
            struct.pack('i', WINDOW_WIDTH))
        self.compute['windowHeight'].write(
            struct.pack('i', WINDOW_HEIGHT))

        # create texture
        self.tex = self.ctx.texture(
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            components=4,
            dtype='f4'
        )
        self.tex.repeat_x = self.tex.repeat_y = False
        self.tex.bind_to_image(0, read=False, write=True)

        self.vbo = self.ctx.buffer(SCREEN_QUAD.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog, [(self.vbo, '2f 2f', 'in_pos', 'in_uv')])

        # initialize other
        self.input = set()
        self.cam = Camera([10.0, -5.0, 5.0], [0.0,0.0,0.0])
        self.update_program()

    def on_render(self, time: float, frametime: float):
        self.dt = frametime
        self.update()
        self.draw()

    def update(self):
        self.cam.update(self.input, self.dt)
        if self.cam.moved().any(): self.run_compute()
        self.draw()

    def run_compute(self):
        groups_x = (self.ctx.viewport[2] + LOCAL_SIZE - 1) // LOCAL_SIZE
        groups_y = (self.ctx.viewport[3] + LOCAL_SIZE - 1) // LOCAL_SIZE
        self.compute.run(groups_x, groups_y, 1)
        self.ctx.memory_barrier(
            moderngl.SHADER_IMAGE_ACCESS_BARRIER_BIT)
        self.update_program()

    def draw(self):
        self.ctx.clear(*CLEAR_COLOR, depth=1.0)
        self.tex.use(location=0)
        self.prog['tex'].value = 0
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def update_program(self):
        # update uniforms
        self.compute['camPos'].write(struct.pack('3f', *self.cam.pos))
        self.compute['bhMass'].write(struct.pack('f', BH_MASS))
        self.compute['rS'].write(struct.pack('f', R_S))

    # def on_resize(self, width: int, height: int):
    #     self.aspect_ratio = width / height
    #     self.ctx.viewport = (0, 0, width, height)
    #     self.compute['windowWidth'].write(struct.pack('i', width))
    #     self.compute['windowHeight'].write(struct.pack('i', height))
    #     self.tex.release()
    #     self.tex = self.ctx.texture(
    #         size=(width, height),
    #         components=4,
    #         dtype='f4'
    #     )
    #     self.tex.bind_to_image(0, read=False, write=True)


    def on_mouse_scroll_event(self, x_offset: float, y_offset: float):
        self.cam.update_zoom(y_offset, self.dt)

    def on_key_event(self, key, action, modifiers):
        parse_key_input(key, action, modifiers, self.input)

if __name__ == '__main__':
    glw.run_window_config(Game)

