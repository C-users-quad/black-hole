vertex_shader = (
    """
    attribute vec3 a_color;
    attribute vec2 a_pos;
    attribute float a_radius;

    uniform vec2 u_CamPos;
    uniform float u_CamZoom;
    uniform vec2 u_WindowSize;

    varying vec3 v_color;

    void main()
    {
        // Camera-relative world position
        vec2 camRelative = u_CamPos - a_pos;

        // Scale by zoom (world units -> pixels)
        vec2 zoomed = camRelative * u_CamZoom;

        // Convert to NDC
        vec2 ndc = zoomed / (u_WindowSize / 2.0);
        ndc.x = -ndc.x;
        
        // set position in opengl
        gl_Position = vec4(ndc, 0.0, 1.0);

        // Point diameter in pixels
        gl_PointSize = a_radius * 2.0 * u_CamZoom;
        
        // return color to fragment shader
        v_color = a_color;
    }
    """
)

fragment_shader = (
    """
    varying vec3 v_color;

    void main() {
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist2 = dot(coord,coord);

        if (dist2 > 0.25) {
            discard;
        }

        gl_FragColor = vec4(v_color, 1.0);
    }
    """
)