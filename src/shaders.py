vert_shader=(
    """
    #version 330

    in vec3 in_vert;
    in vec3 in_color;

    uniform mat4 mvp;

    out vec3 v_color;

    void main() {
        gl_Position = mvp * vec4(in_vert, 1.0);
        v_color = in_color;
    }
    """
)

frag_shader=(
    """
    #version 330

    in vec3 v_color;

    out vec4 f_color;

    void main() {
        f_color = vec4(v_color, 1.0);
    }
    """
)

